import discord
from datetime import datetime
import json
import modules.custom_exceptions as custom_exceptions
from base.modules.interactive_message import InteractiveMessage
from modules.cyra_constants import world_url, tower_menu_url, achievements, tower_achievements
from base.modules.constants import num_emojis, text_emojis, letter_emojis
from modules.level_parser import parse_wave_achievements, sum_dict
from modules.optimize import find_minimal_cost

class LevelRootMessage(InteractiveMessage):
  def __init__(self, parent=None, **attributes):
    super().__init__(parent, **attributes)
    # emojis for 7 worlds
    self.child_emojis = num_emojis[1:8]
    self.connie_emoji = self.context.bot.get_emoji(self.context.guild, "connie")
    # emojis for SR, Arcade, endless, challenges, connie story
    self.child_emojis += [letter_emojis["S"], letter_emojis["A"], letter_emojis["E"], letter_emojis["C"], self.connie_emoji]

  async def transfer_to_child(self, emoji):
    if emoji == letter_emojis["S"]:
      world = "S"
    elif emoji == letter_emojis["A"]:
      world = "A"
    elif emoji == letter_emojis["E"]:
      world = "E"
    elif emoji == letter_emojis["C"]:
      world = "C"
    elif emoji == self.connie_emoji:
      world = "Connie"
    else:
      world = num_emojis.index(emoji)
    return LevelWorldMessage(world, self)
    
  async def get_embed(self):
    embed = discord.Embed(title=f"Level Main Menu", timestamp=datetime.utcnow(), colour=discord.Colour.green(), description="Choose a world (by reacting):")
    embed.set_thumbnail(url=tower_menu_url)
    embed.add_field(name=f"World 1:", value="Level 1-20")
    embed.add_field(name=f"World 2:", value="Level 21-40")
    embed.add_field(name=f"World 3:", value="Level 41-80")
    embed.add_field(name=f"World 4:", value="Level 81-120")
    embed.add_field(name=f"World 5:", value="Level 121-160")
    embed.add_field(name=f"World 6:", value="Level 161-200")
    embed.add_field(name=f"World 7:", value="Level 201-210")
    embed.add_field(name=f"Shattered Realms:", value="Level 1-40")
    embed.add_field(name=f"Arcade:", value="Level 1-5")
    embed.add_field(name=f"Endless:", value="World 1-5")
    embed.add_field(name=f"Challenges:", value="World 1,2,3,6")
    embed.add_field(name=f"{self.connie_emoji} Connie Story:", value="Chapter 1-7")
    embed.set_footer(text="MAIN MENU")
    return embed

class LevelWorldMessage(InteractiveMessage):
  def __init__(self, world, parent=None, **attributes):
    if world not in [1,2,3,4,5,6,7,"S","A","E","C","Connie"]:
      raise custom_exceptions.DataNotFound("World", world)
    super().__init__(parent, **attributes)
    self.world = world
    if self.parent is None:
      self.parent = LevelRootMessage(**attributes)
    if world in [1,2]:
      self.world_text = f"World {world}"
      self.child_emojis = num_emojis[1:3]
      self.categories = [f"Level {world*20-19}-{world*20-10}", f"Level {world*20-9:>2}-{world*20}"]
      self.lists = [[f"{i}" for i in range(world*20-19,world*20-10+1)], [f"{i}" for i in range(world*20-9,world*20+1)]]
    elif world in [3,4,5,6]:
      self.world_text = f"World {world}"
      self.child_emojis = num_emojis[1:5]
      self.categories = [f"Level {world*40-79}-{world*40-70}", f"Level {world*40-69}-{world*40-60}",
                       f"Level {world*40-59}-{world*40-50}", f"Level {world*40-49}-{world*40-40}"]
      self.lists = [[f"{i}" for i in range(world*40-79,world*40-70+1)], [f"{i}" for i in range(world*40-69,world*40-60+1)],
                    [f"{i}" for i in range(world*40-59,world*40-50+1)], [f"{i}" for i in range(world*40-49,world*40-40+1)]]
    elif world in [7]:
      self.world_text = f"World {world}"
      self.child_emojis = num_emojis[1:2]
      self.categories = [f"Level {world*40-79}-{world*40-70}"]
      self.lists = [[f"{i}" for i in range(world*40-79,world*40-70+1)]]
    elif world in ["S"]:
      self.world_text = f"Shattered Realms"
      self.child_emojis = num_emojis[1:9]
      self.categories = [f"Level  1-5  Piece of Pridefall", f"Level  6-10 Frozen Fragment",
                       f"Level 11-15 Sunken Sands", f"Level 16-20 Fallen Corruption",
                       f"Level 21-25 Shifted Sands", f"Level 26-30 Tundra Plateau",
                       f"Level 31-35 Simmering Sands", f"Level 36-40 Desolate Drifts"]
      self.lists = [[f"S{i}" for i in range(1,6)], [f"S{i}" for i in range(6,11)],
                    [f"S{i}" for i in range(11,16)], [f"S{i}" for i in range(16,21)],
                    [f"S{i}" for i in range(21,26)], [f"S{i}" for i in range(26,31)],
                    [f"S{i}" for i in range(31,36)], [f"S{i}" for i in range(36,41)]]
    elif world in ["A"]:
      self.world_text = f"Arcade"
      self.child_emojis = num_emojis[1:6]
      self.categories = [f"A1 Potions vs Slimes", f"A2 Present Plunder", f"A3 Secret Weapon", 
                       f"A4 Siberian Match", f"A5 Defense of Athena"]
      self.lists = [[f"A1-{i}" for i in range(1,4)], [f"A2-{i}" for i in range(1,4)],
                    [f"A3-{i}" for i in range(1,4)], [f"A4-{i}" for i in range(1,4)],
                    [f"A5-{i}" for i in range(1,4)]]
    elif world in ["E"]:
      self.world_text = f"Endless"
      self.child_emojis = num_emojis[1:6]
      self.categories = [f"World {i} Endless" for i in range(1,6)]
      self.levels = [f"E{i}" for i in range(1,6)]
    elif world in ["C"]:
      self.world_text = f"Challenge"
      self.child_emojis = [num_emojis[i] for i in [1,2,3,6]]
      self.categories = [f"World {i} Challenge" for i in [1,2,3,6]]
      self.lists = [[f"C1-{i}" for i in range(1,6)], [f"C2-{i}" for i in range(1,11)],
                    [f"C3-{i}" for i in range(1,11)], [f"C6-{i}" for i in range(1,11)]]
    elif world in ["Connie"]:
      self.world_text = f"Connie Story"
      self.child_emojis = num_emojis[1:8]
      self.categories = [f"Chapter {i}" for i in range(1,8)]
      self.levels = [f"Connie{i}" for i in range(1,8)]
    
  async def transfer_to_child(self, emoji):
    if self.world in [1,2,3,4,5,6,7,"S","A","C"]:
      return LevelCategoryMessage(self.lists[self.child_emojis.index(emoji)], self.world_text, self)
    else:
      return LevelIndividualMessage(self.levels[self.child_emojis.index(emoji)], self)
    
  async def get_embed(self):
    instructions = "\n".join([f"{emoji} `{category}`" for emoji, category in zip(self.child_emojis, self.categories)])
    embed = discord.Embed(title=f"{self.world_text} Level Menu", timestamp=datetime.utcnow(), colour=discord.Colour.green(),
      description=f"Choose a category (by reacting):\n{instructions}")
    embed.set_thumbnail(url=world_url[self.world])
    embed.set_footer(text=f"{self.world_text}")
    return embed

  
class LevelCategoryMessage(InteractiveMessage):
    
  def __init__(self, levels, name, parent=None, **attributes):
    super().__init__(parent, **attributes)
    if self.parent is None:
      self.parent = LevelRootMessage(None, **attributes)
    self.name = name
    db = self.context.bot.db[self.context.guild.id]
    level_list = ", ".join([f'"{level}"' for level in levels])
    self.level_info = db.query(f"SELECT * FROM levels where level in ({level_list})")
    self.level_info.sort(key=lambda level:levels.index(level[0]))
    if not self.level_info:
      raise custom_exceptions.DataNotFound("Levels", level_list)
    if len(self.level_info) > len(num_emojis)-1:
      raise ValueError("Too many levels")
    elif len(self.level_info) == len(num_emojis)-1:
      self.child_emojis = num_emojis[1:]
    else:
      self.child_emojis = num_emojis[1:len(self.level_info)+1]
    
  async def transfer_to_child(self, emoji):
    ind = self.child_emojis.index(emoji)
    level_row = self.level_info[ind]
    return LevelIndividualMessage(level_row[0], self, dbrow=level_row)
    
  async def get_embed(self):
    max_level_len = max(len(level[0]) for level in self.level_info)
    instructions = "\n".join([f"{emoji} `{level[0]:<{max_level_len}} {level[2]}`" for emoji, level in zip(self.child_emojis, self.level_info)])
    embed = discord.Embed(title=f"{self.name} Levels", colour=discord.Colour.green(), timestamp=datetime.utcnow(), 
                          description=f"Choose a level (by reacting):\n{instructions}")
    embed.set_footer(text=f"{self.name}")
    return embed
    
class LevelIndividualMessage(InteractiveMessage):
    
  def __init__(self, level, parent=None, **attributes):
    super().__init__(parent, **attributes)
    self.level = level
    self.dbrow = attributes.pop("dbrow", None)
    db = self.context.bot.db[self.context.guild.id]
    if not self.dbrow:
      self.dbrow = db.select("levels", level)
      if not self.dbrow:
        raise custom_exceptions.DataNotFound("Level", level)
      else:
        self.dbrow = list(self.dbrow.values())
    world = self.dbrow[1]
    if level.startswith("S"):
      self.footer = "Shattered Realms"
      w = "S"
    elif level.startswith("A"):
      self.footer = "Arcade"
      w = "A"
    elif level.startswith("Connie"):
      self.footer = "Connie Story"
      w = "Connie"
    elif level.startswith("C"):
      self.footer = f"World {world} Challenge"
      w = "C"
    elif level.startswith("E"):
      self.footer = f"World {world} Endless"
      w = "E"
    else:
      self.footer = f"World {world}"
      w = world
    if self.parent is None:
      self.parent = LevelWorldMessage(w, **attributes)
    # check the level's wave data to decide its child emojis
    wave_info = db.query(f'SELECT * FROM wave WHERE level="{level}"')
    self.wave_info = None
    self.legendary_info = None
    if wave_info:
      for row in wave_info:
        if row[1].lower() == "legendary":
          self.legendary_info = row
        elif row[1].lower() in ["", "campaign"]:
          self.wave_info = row
    if self.wave_info:
      self.child_emojis.append("👽")
    if self.legendary_info:
      self.child_emojis.append("🏆")
    
  async def transfer_to_child(self, emoji):
    if emoji == "👽":
      return LevelWaveMessage(self.level, self.wave_info[1], self, dbrow=self.wave_info, link=self.dbrow[6], task=self.dbrow[4])
    elif emoji == "🏆":
      return LevelWaveMessage(self.level, self.legendary_info[1], self, dbrow=self.legendary_info, link=self.dbrow[6], task=self.dbrow[4])
    
  async def get_embed(self):
    level, world, name, handicap, task, tappable, link, remark = self.dbrow
    descriptions = []
    if remark: descriptions.append(f"🕹️ Level Type: {remark.title()}")
    if task == "bandit":
      descriptions.append(f"📝 Campaign Task: Kill the bandit")
    elif task == "villager":
      descriptions.append(f"📝 Campaign Task: Protect the villager")
    if handicap and handicap != "NONE": descriptions.append(f"🏅 Legendary Handicap: {handicap}")
    description = "\n".join(descriptions) if descriptions else None
    embed = discord.Embed(title=f"{level}. {name}", colour=discord.Colour.green(), timestamp=datetime.utcnow(), description=description)
    if tappable and tappable != "NONE":
      coin_emoji = self.context.bot.get_emoji(self.context.guild, "coin")
      if coin_emoji is not None:
        tappable = tappable.replace("💰", f"{coin_emoji}")
      embed.add_field(name="Tappable(s):", value=tappable, inline=False)
    if self.wave_info or self.legendary_info:
      instructions = []
      if self.wave_info:
        instructions.append("👽 Enemy waves")
      if self.legendary_info:
        instructions.append("🏆 Legendary waves")
      embed.add_field(name="To check enemy waves:", value=" ".join(instructions), inline=False)
    if link and link != "NONE":
      embed.set_image(url=link)
    embed.set_footer(text=self.footer)
    return embed
    
class LevelWaveMessage(InteractiveMessage):
    
  def __init__(self, level, mode, parent=None, **attributes):
    super().__init__(parent, **attributes)
    self.level = level
    self.mode = mode
    self.state = 0
    self.achieve = False
    dbrow = attributes.pop("dbrow", None)
    self.link = attributes.pop("link", None)
    self.task = attributes.pop("task", None)
    if not dbrow:
      dbrow = self.context.bot.db[self.context.guild.id].select("wave", [level, mode])
      if not dbrow:
        raise custom_exceptions.DataNotFound("Level Waves", f"{level} {mode}" if mode else level)
      else:
        dbrow = list(dbrow.values())
    if self.task is None or self.link is None:
      level_general = self.context.bot.db[self.context.guild.id].select("levels", level)
      if not level_general:
        raise custom_exceptions.DataNotFound("Level", level)
      else:
        self.task = level_general["task"]
        self.link = level_general["link"]
    if self.parent is None:
      self.parent = LevelIndividualMessage(level, **attributes)
    # check the level's wave data to decide its child emojis
    self.level_info = {"level":dbrow[0], "mode":dbrow[1], "initial_gold":dbrow[2], "max_life":dbrow[3], "enemy_waves":json.loads(dbrow[4])}
    for wave in self.level_info["enemy_waves"]:
      wave["achievements"] = parse_wave_achievements(wave["enemies"])
    if len(self.level_info["enemy_waves"]) > 1: # only need to show more info when there are more than 1 waves
      self.child_emojis += [text_emojis["info"], "🏆"] + num_emojis[1:len(self.level_info["enemy_waves"])+1]
    else:
      self.child_emojis = ["🏆"]
    
  async def transfer_to_child(self, emoji):
    if emoji == "🏆":
      self.achieve = not self.achieve
      return self
    if emoji == text_emojis["info"]:
      state = 0
    else:
      state = num_emojis.index(emoji)
    if state == self.state:
      return None
    else:
      self.state = state
      return self
    
  async def get_embed(self):
    gold_emoji = self.context.bot.get_emoji(self.context.guild, "coin")
    if not gold_emoji:
      gold_emoji = "💰"
    if self.state == 0:
      # show sum information
      enemies = {}
      total_time = 0
      total_reward = 0
      total_bonus = 0
      i = 0
      for wave in self.level_info["enemy_waves"]:
        i += 1
        sum_dict(enemies, wave["enemies"] if not self.achieve else wave["achievements"])
        total_time += wave["time"]
        total_reward += wave["reward"]
        if i > 1:
          total_bonus += wave["bonus"]
      category = "Level Information"
    else:
      # show a specific wave info
      wave = self.level_info["enemy_waves"][self.state-1]
      enemies = wave["enemies"] if not self.achieve else wave["achievements"]
      total_time = wave["time"]
      total_reward = wave["reward"]
      if self.state == 1:
        total_bonus = 0
      else:
        total_bonus = wave["bonus"]
      category = f"Wave {self.state} Information"
    description=(f"{gold_emoji} Initial Gold: {self.level_info['initial_gold']}\n❤️ Life: {self.level_info['max_life']}\n"
                 f"🌊 Wave Num: {len(self.level_info['enemy_waves'])}")
    if total_bonus == 0:
      text = f"⏳ Time: {total_time:.1f}s\n{gold_emoji} Reward: {total_reward}"
    else:
      text = f"⏳ Time: {total_time:.1f}s\n{gold_emoji} Reward: {total_reward}\n{gold_emoji} Early wave bonus: {total_bonus}"
    embed = discord.Embed(title=f"Level {self.level} {self.mode.title()}", colour=discord.Colour.green(), 
                          timestamp=datetime.utcnow(), description=description)
    embed.add_field(name=f"{category}:", value=text, inline=False)
    max_num_len = 1
    if enemies:
      max_num_len = max(len(str(num)) for num in enemies.values())
      if self.achieve:
        kill_msg = [f"`{num:<{max_num_len}} {enemy.replace('_', ' ').title()} Enemies`" for enemy, num in enemies.items()]
      else:
        kill_msg = [f"`{num:<{max_num_len}} {enemy.title()}`" for enemy, num in enemies.items()]
    else:
      kill_msg = []
    if self.state == 0 and self.mode != "legendary" and (self.task == "bandit" or (self.task == "villager" and self.achieve)):
      kill_msg.append(f"`{1:<{max_num_len}} {self.task.title()}`")
    embed.add_field(name="Enemies:" if not self.achieve else "Achievements:", value="\n".join(kill_msg) if kill_msg else "None", inline=False)
    if len(self.level_info["enemy_waves"]) > 1:
      wave_emojis = " ".join(num_emojis[1:len(self.level_info["enemy_waves"])+1])
      instruction = (f"{text_emojis['info']} Overview {num_emojis[1]}-{num_emojis[len(self.level_info['enemy_waves'])]} Wave Info\n"
                     f"🏆 Switch to {'Achievements' if not self.achieve else 'Enemies'}")
    else:
      instruction = f"🏆 Switch to {'Achievements' if not self.achieve else 'Enemies'}"
    embed.add_field(name="For information:", value=instruction, inline=False)
    embed.set_footer(text="Enemy Waves")
    if self.link and self.link != "NONE":
      embed.set_thumbnail(url=self.link)
    return embed
    
class LevelAchievementMessage(InteractiveMessage):
  general_columns = ["level","name","mode","strategy","time","gold","wave","link","task"]
    
  def __init__(self, achievement, num, parent=None, **attributes):
    super().__init__(parent, **attributes)
    world = attributes.pop("world", None)
    mode = attributes.pop("mode", None)
    sort_by_absolute = attributes.pop("sort_by_absolute", False)
    # use the world and mode arguments to limit the search
    where_clause = []
    select_clause = self.general_columns + achievements
    # the time required for entering and exiting the level
    self.tlevel = self.context.bot.get_setting(self.context.guild, "LEVEL_EXTRA_TIME")
    # the time required for calling a wave
    self.twave = self.context.bot.get_setting(self.context.guild, "WAVE_EXTRA_TIME")
    limit = 10
    if world:
      where_clause.append(f"world={world}")
    if mode:
      where_clause.append(f'mode="{mode}"')
    # check the achievemnt argument to get the sorting method
    achievement_parse = achievement.replace('_', ' ').title()
    time_string = f"time/2.0+{self.tlevel}+wave*{self.twave}"
    time_calculation = lambda row: row[4]/2.0+self.tlevel+row[6]*self.twave
    if achievement == "fast":
      self.goal = "levels with the shortest completion time"
      self.info = ["TIME"]
      self.info_fun = lambda row: [f"{row[-1]:.0f}"]
      select_clause.append(f"MIN({time_string}) AS criteria")
      sort_method = "criteria ASC"
    elif achievement in tower_achievements:
      self.goal = f"levels with the highest gold rewards to help tower achievements"
      self.info = ["GOLD", "TIME", "GPS"]
      self.info_fun = lambda row: [row[5], f"{time_calculation(row):.0f}", f"{row[-1]:.2f}"]
      criteria_str = f"CAST(gold AS FLOAT)/({time_string})"
      if sort_by_absolute == False:
        select_clause.append(f"MAX({criteria_str}) AS criteria")
        sort_method = "criteria DESC"
      else:
        select_clause.append(f"MAX(gold-time/100.0)")
        select_clause.append(f"({criteria_str}) AS criteria")
        sort_method = "gold DESC"
    else:
      if achievement in ["villager", "bandit"]:
        target = f"**{achievement_parse}s**"
        farm = "NUM"
      else:
        target = f"**{achievement_parse}** Enemies"
        farm = "KILL"
      ind = select_clause.index(achievement) # index of achievement in results
      where_clause.append(f"{achievement}>0")
      if num:
        self.goal = f"levels that quickly farm **{num}** {target}"
        self.info = [f"{farm}","TIME","RUN","SUM_T"]
        self.info_fun = lambda row: [row[ind], f"{time_calculation(row):.0f}", 
                        int(-(-num // row[ind])), f"{row[-1]:.0f}"]
        num = float(num)
        criteria_str = f"({time_string})*(CAST (({num}/{achievement}) AS INT)+(({num}/{achievement})>CAST (({num}/{achievement}) AS INT)))"
        select_clause.append(f"MIN({criteria_str}) AS criteria")
        sort_method = "criteria ASC"
      else:
        self.goal = f"levels that quickly farm {target}"
        self.info = [f"{farm}","TIME","KPS"]
        self.info_fun = lambda row: [row[ind], f"{time_calculation(row):.0f}", f"{row[-1]:.2f}"]
        criteria_str = f"CAST({achievement} AS FLOAT)/({time_string})"
        if not sort_by_absolute == True:
          select_clause.append(f"MAX({criteria_str}) AS criteria")
          sort_method = "criteria DESC"
        else:
          select_clause[ind] = f"MAX({achievement})"
          select_clause.append(f"({criteria_str}) AS criteria")
          sort_method =  f"{achievement} DESC"
    where_clause = " AND ".join(where_clause) if where_clause else "TRUE"
    select_clause = ", ".join(select_clause)
    self.result = self.context.bot.db[self.context.guild.id].query(
      f"SELECT {select_clause} FROM achievement NATURAL JOIN levels WHERE ({where_clause}) GROUP BY level, mode ORDER BY {sort_method}, LENGTH(level), level LIMIT {limit}")
    if not self.result:
      condition = []
      if world:
        condition.append(f"W{world}")
      if mode:
        condition.append(f"{mode.title()} mode")
      raise custom_exceptions.DataNotFound("Achievement", f"{achievement_parse} in {' '.join(condition)}" if condition else achievement_parse)
    self.update_state(0)
      
  def update_state(self, state):
    if state <= 0:
      self.state = 0
      self.child_emojis = [text_emojis["info"]] + num_emojis[1:len(self.result)+1]
    else:
      self.state = min(state, len(self.result))
      self.child_emojis = [text_emojis["info"]] + num_emojis[1:len(self.result)+1] + ["👽"]
      
  @property
  def current_row(self):
    if self.state > 0:
      return self.result[self.state-1]
    
  async def transfer_to_child(self, emoji):
    if emoji == "👽":
      if self.state > 0:
        return LevelWaveMessage(self.current_row[0], self.current_row[2], self, link=self.current_row[7], task=self.current_row[8])
      else:
        return None
    if emoji == text_emojis["info"]:
      state = 0
    else:
      state = num_emojis.index(emoji)
    if state == self.state:
      return None
    else:
      self.update_state(state)
      return self
    
  async def get_embed(self):
    if self.state <= 0: # return the summary
      description = (f"🎯 Goal: Find {self.goal}\n"
                     f"📖 Assume: {self.tlevel:<.0f}s to enter and exit, {self.twave:<.0f}s to call a wave, and played under **x2 speed**\n"
                     f"Candidate levels with their attributes are shown below:\n")
      table = [["NO","LEVEL"]+self.info]
      max_len = [len(str(item)) for item in table[0]]
      i = 0
      for row in self.result:
        i += 1
        new_row = [str(i), f"{row[0]} {row[2][:3].title()}"]+self.info_fun(row)
        table.append(new_row)
        max_len = [max(column) for column in zip(max_len, [len(str(item)) for item in new_row])]
      summary = ["`" + "  ".join(f"{row[i]:<{max_len[i]}}" for i in range(len(row))) + "`" for row in table]
      embed = discord.Embed(title=f"Search Results", colour=discord.Colour.green(), 
                            timestamp=datetime.utcnow(), description=description+"\n".join(summary))
      instruction = f"{text_emojis['info']} Summary  {num_emojis[1]}-{num_emojis[len(self.result)]} Results"
      embed.add_field(name="For Level Details:", value=instruction, inline=False)
    else: # return the level info
      general_columns_num = len(self.general_columns)
      level, name, mode, strategy, time, gold, wave, link, _ = self.current_row[:general_columns_num]
      kills = self.current_row[general_columns_num:general_columns_num+len(achievements)]
      description = []
      if strategy:
        description.append(f"⚔️ Strategy: {strategy}")
      description.append(f"⏳ Completion Time (x1 speed): {time}s")
      description.append(f"🌊 Wave Num: {wave}")
      gold_emoji = self.context.bot.get_emoji(self.context.guild, "coin")
      if not gold_emoji:
        gold_emoji = "💰"
      description.append(f"{gold_emoji} Gold Rewards: {gold}")
      embed = discord.Embed(title=f"{level}. {name} {mode.title()}", colour=discord.Colour.green(), 
                            timestamp=datetime.utcnow(), description="\n".join(description))
      kill_msg = []
      max_kill_len = max([len(str(kill)) for kill in kills])
      for name, kill in zip(achievements, kills):
        if kill > 0:
          name = name.title() if name in ["villager", "bandit"] else f"{name.replace('_', ' ').title()} Enemies"
          kill_msg.append(f"`{kill:<{max_kill_len}} {name}`")
      embed.add_field(name="Achievement Counts:", value="\n".join(kill_msg) if kill_msg else "None", inline=False)
      instruction = (f"{text_emojis['info']} Summary  {num_emojis[1]}-{num_emojis[len(self.result)]} Results\n"
                     f"👽 Details of Enemy Waves")
      embed.add_field(name="For Other Details:", value=instruction, inline=False)
      if link and link != "NONE":
        embed.set_image(url=link)
    embed.set_footer(text="Achievements")
    return embed
    
    
class AchievementPlanMessage(InteractiveMessage):
  general_columns = ["level","name","mode","strategy","time","gold","wave","link","task"]

  def __init__(self, achieves, nums, parent=None, **attributes):
    super().__init__(parent, **attributes)
    self.achieves = achieves
    self.nums = nums
    self.attributes = attributes.copy()
    self.achieves_ind = [achievements.index(achievement) for achievement in achieves]
    world = attributes.pop("world", None)
    mode = attributes.pop("mode", None)
    sort_by_absolute = attributes.pop("sort_by_absolute", False)
    self.candidates = attributes.pop("candidates", None)
    self.tlevel = self.context.bot.get_setting(self.context.guild, "LEVEL_EXTRA_TIME")
    self.twave = self.context.bot.get_setting(self.context.guild, "WAVE_EXTRA_TIME")
    if self.candidates is None:
      # use the world and mode arguments to limit the search
      where_clause = [" OR ".join([f"{achievement}>0" for achievement in achieves])]
      select_clause = self.general_columns + achievements + [f"time/2.0+{self.tlevel}+wave*{self.twave} AS tvalid"] 
      if world:
        where_clause.append(f"world={world}")
      if mode:
        where_clause.append(f'mode="{mode}"')
      select_clause = ", ".join(select_clause)
      where_clause = f"({') AND ('.join(where_clause)})"
      self.candidates = self.context.bot.db[self.context.guild.id].query(f"SELECT {select_clause} FROM achievement NATURAL JOIN levels WHERE {where_clause}")
    if not self.candidates:
      condition = []
      if world:
        condition.append(f"W{world}")
      if mode:
        condition.append(f"{mode.title()} mode")
      achieves_parse = ', '.join([achievement.replace('_', ' ').title() for achievement in achieves])
      raise custom_exceptions.DataNotFound("Achievement", f"{achieves_parse} in {' '.join(condition)}" if condition else achieves_parse)
      
    # optimize process
    constraint_coeffs = []
    for i in range(len(achieves)):
      constraint_coeffs.append([])
    lower_bounds = nums
    cost_coeffs = []
    for i, row in enumerate(self.candidates):
      _, time, row_achieves = self.row_split(row)
      counts = self.get_target_achieves(row_achieves)
      for j, count in enumerate(counts):
        constraint_coeffs[j].append(count)
      cost_coeffs.append(time if not sort_by_absolute else 10000+time) # give a small weight on time so that level with less time will be more likely to be selected
    self.minimum_sol = find_minimal_cost(constraint_coeffs, lower_bounds, cost_coeffs)
    self.minimum_sol.sort(reverse=True, key=lambda sol: sol[1])
    self.update_state(0)
      
  def update_state(self, state):
    len_viewable = min(10, len(self.minimum_sol))
    if len_viewable == 0:
      self.state = 0
      self.child_emojis = []
      return
    if state <= 0:
      self.state = 0
      self.child_emojis = [text_emojis["info"]] + num_emojis[1:len_viewable+1]
    else:
      self.state = min(state, len(self.minimum_sol))
      self.child_emojis = [text_emojis["info"]] + num_emojis[1:len_viewable+1] + ["👽", "❌"]
      
  @property
  def current_row(self):
    if self.state > 0:
      return self.candidates[self.current_candidate_ind]
      
  @property
  def current_candidate_ind(self):
    if self.state > 0:
      return self.minimum_sol[self.state-1][0]
      
  def row_split(self, row):
    general = row[:len(self.general_columns)]
    time = row[-1]
    achieves = row[len(self.general_columns):-1]
    return general, time, achieves
    
  def get_target_achieves(self, achieves):
    return [achieves[ind] for ind in self.achieves_ind]
    
  async def transfer_to_child(self, emoji):
    if emoji == "👽":
      if self.state > 0:
        return LevelWaveMessage(self.current_row[0], self.current_row[2], self, link=self.current_row[7], task=self.current_row[8])
      else:
        return None
    if emoji == "❌":
      if self.state > 0:
        if len(self.candidates) <= 1:
          await self.context.send(f"{self.context.author.mention} You are going to remove all candidates levels and no solution can be found!")
          return None
        self.candidates.pop(self.current_candidate_ind)
        self.attributes["candidates"] = self.candidates
        self.attributes["message"] = self.message
        return AchievementPlanMessage(self.achieves, self.nums, self.parent, **self.attributes)
      else:
        return None
    if emoji == text_emojis["info"]:
      state = 0
    else:
      state = num_emojis.index(emoji)
    if state == self.state:
      return None
    else:
      self.update_state(state)
      return self
    
    
  async def get_embed(self):
    if self.state <= 0: # return the summary
      achieve_lists = [f"**{num}** **{achievement.title()}s**" if achievement in ["bandit", "villager"] else
                       f"**{num}** **{achievement.replace('_', ' ').title()}** enemies"
                       for achievement, num in zip(self.achieves, self.nums)]
      goal = f"Find a plan to quickly farm {', '.join(achieve_lists)}"
      description = (f"🎯 Goal: {goal}\n"
                     f"📖 Assume: {self.tlevel:<.0f}s to enter and exit, {self.twave:<.0f}s to call a wave, and played under **x2 speed**")
      embed = discord.Embed(title=f"Plan Results", colour=discord.Colour.green(), timestamp=datetime.utcnow(), description=description)
      if not self.minimum_sol:
        embed.add_field(name="Farm Plans:", value="No optimal plan can be found", inline=False)
      else:
        table = [["NO","LEVEL","RUN","TIME"] + [f"GOAL{i+1}" for i in range(len(self.achieves))]]
        max_len = [len(str(item)) for item in table[0]]
        sum_run = 0
        sum_t = 0
        i = 0
        for ind, runs in self.minimum_sol:
          i += 1
          row = self.candidates[ind]
          achieve_row = row[len(self.general_columns):-1]
          goal_counts = self.get_target_achieves(achieve_row)
          sum_run += runs
          sum_t += row[-1] * runs
          new_row = [str(i), f"{row[0]} {row[2][:3].title()}", runs, f"{row[-1]:.0f}"]+goal_counts
          table.append(new_row)
          max_len = [max(column) for column in zip(max_len, [len(str(item)) for item in new_row])]
        summary = ["`" + "  ".join(f"{row[i]:<{max_len[i]}}" for i in range(len(row))) + "`" for row in table]
        embed.add_field(name="Farm Plans:", value="\n".join(summary), inline=False)
        embed.add_field(name="Summary:", value=f"⏳ Total Time: {sum_t:.0f}s\n🏃 Total Runs: {sum_run}", inline=False)
        instruction = (f"{text_emojis['info']} Summary  {num_emojis[1]}-{num_emojis[len(self.minimum_sol)]} Results\n"
                       f"To remove a level, react its number and then ❌") 
        embed.add_field(name="For Level Details:", value=instruction, inline=False)
    else: # return the level info
      general, time, kills = self.row_split(self.current_row)
      level, name, mode, strategy, time, gold, wave, link, _ = general
      description = []
      if strategy:
        description.append(f"⚔️ Strategy: {strategy}")
      description.append(f"⏳ Completion Time (x1 speed): {time}s")
      description.append(f"🌊 Wave Num: {wave}")
      gold_emoji = self.context.bot.get_emoji(self.context.guild, "coin")
      if not gold_emoji:
        gold_emoji = "💰"
      description.append(f"{gold_emoji} Gold Rewards: {gold}")
      embed = discord.Embed(title=f"{level}. {name} {mode.title()}", colour=discord.Colour.green(), 
                            timestamp=datetime.utcnow(), description="\n".join(description))
      kill_msg = []
      max_kill_len = max([len(str(kill)) for kill in kills])
      for name, kill in zip(achievements, kills):
        if kill > 0:
          name = name.title() if name in ["villager", "bandit"] else f"{name.replace('_', ' ').title()} Enemies"
          kill_msg.append(f"`{kill:<{max_kill_len}} {name}`")
      embed.add_field(name="Achievement Counts:", value="\n".join(kill_msg) if kill_msg else "None", inline=False)
      instruction = (f"{text_emojis['info']} Summary  {num_emojis[1]}-{num_emojis[len(self.minimum_sol)]} Results\n"
                     f"👽 Details of Enemy Waves\n❌ Remove this Level from Results")
      embed.add_field(name="For Other Details:", value=instruction, inline=False)
      if link and link != "NONE":
        embed.set_image(url=link)
    embed.set_footer(text="Achievements")
    return embed
