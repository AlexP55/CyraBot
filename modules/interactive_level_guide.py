import discord
from datetime import datetime
import json
import modules.custom_exceptions as custom_exceptions
from base.modules.interactive_message import InteractiveMessage
from modules.cyra_constants import world_url, tower_menu_url, achievements
from base.modules.constants import num_emojis, text_emojis, letter_emojis
from modules.level_parser import parse_wave_achievements, sum_dict

class LevelRootMessage(InteractiveMessage):
  def __init__(self, parent=None, **attributes):
    super().__init__(parent, **attributes)
    # emojis for 6 worlds
    self.child_emojis = num_emojis[1:7]
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
    embed.add_field(name=f"Shattered Realms:", value="Level 1-40")
    embed.add_field(name=f"Arcade:", value="Level 1-5")
    embed.add_field(name=f"Endless:", value="World 1-5")
    embed.add_field(name=f"Challenges:", value="World 1,2,3,6")
    embed.add_field(name=f"{self.connie_emoji} Connie Story:", value="Chapter 1-7")
    embed.set_footer(text="MAIN MENU")
    return embed

class LevelWorldMessage(InteractiveMessage):
  def __init__(self, world, parent=None, **attributes):
    if world not in [1,2,3,4,5,6,"S","A","E","C","Connie"]:
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
    if self.world in [1,2,3,4,5,6,"S","A","C"]:
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
        elif row[1] in ["", "campaign"]:
          self.wave_info = row
    if self.wave_info:
      self.child_emojis.append("👽")
    if self.legendary_info:
      self.child_emojis.append("🏆")
    
  async def transfer_to_child(self, emoji):
    if emoji == "👽":
      return LevelWaveMessage(self.level, self.wave_info[1], self, dbrow=self.wave_info, link=self.dbrow[5])
    elif emoji == "🏆":
      return LevelWaveMessage(self.level, self.legendary_info[1], self, dbrow=self.legendary_info, link=self.dbrow[5])
    
  async def get_embed(self):
    level, world, name, handicap, tappable, link, remark = self.dbrow
    if remark:
      description = f"Level Type: {remark.title()}"
    embed = discord.Embed(title=f"{level}. {name}", colour=discord.Colour.green(), timestamp=datetime.utcnow(), description=description)
    if handicap and handicap != "NONE":
      embed.add_field(name="Legendary Handicap:", value=handicap, inline=False)
    if tappable and tappable != "NONE":
      coin_emoji = self.context.bot.get_emoji(self.context.guild, "coin")
      if coin_emoji is not None:
        tappable = tappable.replace(":moneybag:", f"{coin_emoji}")
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
    if not dbrow:
      db = self.context.bot.db[self.context.guild.id]
      dbrow = db.select("wave", [level, mode])
      if not dbrow:
        raise custom_exceptions.DataNotFound("Level Waves", f"{level} {mode}" if mode else level)
      else:
        dbrow = list(dbrow.values())
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
    if enemies:
      max_num_len = max(len(str(num)) for num in enemies.values())
      if self.achieve:
        text = "\n".join([f"`{num:<{max_num_len}} {enemy.title()} Enemies`" for enemy, num in enemies.items()])
      else:
        text = "\n".join([f"`{num:<{max_num_len}} {enemy}`" for enemy, num in enemies.items()])
    else:
      text = "None"
    embed.add_field(name="Enemies:" if not self.achieve else "Achievements:", value=text, inline=False)
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
    
  def __init__(self, achievement, num, parent=None, **attributes):
    super().__init__(parent, **attributes)
    self.achievement = achievement
    self.num = num
    self.state = 0
    world = attributes.pop("world", None)
    mode = attributes.pop("mode", None)
    # use the world and mode arguments to limit the search
    where_clause = []
    general_columns = ["level","name","mode","strategy","time","link","remark"]
    select_clause = general_columns + achievements
    # the time required for entering exiting the level and
    self.extra_t = self.context.bot.get_setting(self.context.guild, "LEVEL_EXTRA_TIME")
    limit = self.context.bot.get_setting(self.context.guild, "SEARCH_LIMIT")-1
    if world:
      where_clause.append(f"world={world}")
    if mode:
      where_clause.append(f'mode="{mode}"')
    # check the achievemnt argument to get the sorting method
    if achievement == "fast":
      self.goal = "Levels with the shortest completion time"
      self.info = ["TIME"]
      self.info_fun = lambda row: [f"{row[-1]:.0f}"]
      select_clause.append(f"MIN(time/2.0+{self.extra_t}) AS criteria")
      sort_method = "criteria ASC"
    else:
      ind = achievements.index(achievement) + len(general_columns) # index of achievement in results
      where_clause.append(f"{achievement}>0")
      if num:
        self.goal = f"Levels that quickly farm **{num} {achievement.title()}** Enemies"
        self.info = ["KILL","TIME","RUN","SUM_T"]
        self.info_fun = lambda row: [row[ind], f"{row[4]/2.0+self.extra_t:.0f}", 
                        int(-(-num // row[ind])), f"{row[-1]:.0f}"]
        num = float(num)
        criteria_str = f"(time/2.0+{self.extra_t})*(CAST (({num}/{achievement}) AS INT)+(({num}/{achievement})>CAST (({num}/{achievement}) AS INT)))"
        select_clause.append(f"MIN({criteria_str}) AS criteria")
        sort_method = "criteria ASC"
      else:
        self.goal = f"Levels that quickly farm **{achievement.title()}** Enemies"
        self.info = ["KILL","TIME","KPS"]
        self.info_fun = lambda row: [row[ind], f"{row[4]/2.0+self.extra_t:.0f}", f"{row[-1]:.2f}"]
        criteria_str = f"CAST({achievement} AS FLOAT)/(time/2.0+{self.extra_t})"
        select_clause.append(f"MAX({criteria_str}) AS criteria")
        sort_method = f"criteria DESC"
    where_clause = " AND ".join(where_clause) if where_clause else "TRUE"
    select_clause = ", ".join(select_clause)
    self.result = self.context.bot.db[self.context.guild.id].query(
      f"SELECT {select_clause} FROM achievement NATURAL JOIN levels WHERE ({where_clause}) GROUP BY level, mode ORDER BY {sort_method} LIMIT {limit}")
    if not self.result:
      raise custom_exceptions.DataNotFound("Achievement", f"{achievement} in W{world}" if world else achievement)
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
        return LevelWaveMessage(self.current_row[0], self.current_row[2], self, link=self.current_row[5])
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
                     f"📖 Assume: {self.extra_t:<.0f} seconds to enter and exit the level, and played under **x2 speed**\n"
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
      instruction = f"{text_emojis['info']} Summary {num_emojis[1]}-{num_emojis[len(self.result)]} Results"
      embed.add_field(name="For Level Details:", value=instruction, inline=False)
    else: # return the level info
      level, name, mode, strategy, time, link, remark = self.current_row[:7]
      kills = self.current_row[7:-1]
      description = []
      if strategy == "long":
        if remark == "boss":
          description.append("⚔️ Strategy: Play as long as you can without killing the boss")
        else:
          description.append("⚔️ Strategy: Play as long as you can")
      elif strategy == "short":
        if remark == "boss":
          description.append("⚔️ Strategy: Kill the boss as fast as you can")
        else:
          description.append("⚔️ Strategy: Compelete the mission as fast as you can")
      elif strategy.startswith("skip"):
        description.append(f"⚔️ Strategy: {strategy.capitalize()} by killing the boss quickly, but delay as long as you can in other waves")
      else:
        description.append("⚔️ Strategy: Kill all enemies as fast as you can")
      description.append(f"⏳ Completion Time (x1 speed): {time}s")
      embed = discord.Embed(title=f"{level}. {name} {mode.title()}", colour=discord.Colour.green(), 
                            timestamp=datetime.utcnow(), description="\n".join(description))
      kill_msg = []
      max_kill_len = max([len(str(kill)) for kill in kills])
      for name, kill in zip(achievements, kills):
        if kill > 0:
          kill_msg.append(f"`{kill:<{max_kill_len}} {name.title()} Enemies`")
      embed.add_field(name="Achievement Counts:", value="\n".join(kill_msg) if kill_msg else "None", inline=False)
      instruction = (f"{text_emojis['info']} Summary {num_emojis[1]}-{num_emojis[len(self.result)]} Results\n"
                     f"👽 Details of Enemy Waves")
      embed.add_field(name="For Other Details:", value=instruction, inline=False)
      if link and link != "NONE":
        embed.set_image(url=link)
    embed.set_footer(text="Achievements")
    return embed
