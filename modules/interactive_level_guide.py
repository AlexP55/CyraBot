import discord
from datetime import datetime
import modules.custom_exceptions
from base.modules.interactive_message import InteractiveMessage
from modules.cyra_constants import world_url, tower_menu_url
from base.modules.constants import num_emojis, text_emojis, letter_emojis, item_emojis

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
    embed = discord.Embed(title=f"Level Main Menu", timestamp=datetime.utcnow(), colour=discord.Colour.blue(), description="Choose a world (by reacting):")
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
    embed = discord.Embed(title=f"{self.world_text} Level Menu", timestamp=datetime.utcnow(), colour=discord.Colour.blue(),
      description=f"Choose a category (by reacting):\n{instructions}")
    if isinstance(self.world, int):
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
    embed = discord.Embed(title=f"{self.name} Levels", colour=discord.Colour.blue(), timestamp=datetime.utcnow(), 
                          description=f"Choose a level (by reacting):\n{instructions}")
    embed.set_footer(text=f"{self.name}")
    return embed
    
class LevelIndividualMessage(InteractiveMessage):
    
  def __init__(self, level, parent=None, **attributes):
    super().__init__(parent, **attributes)
    if self.parent is None:
      self.parent = LevelRootMessage(None, **attributes)
    self.level = level
    self.dbrow = attributes.pop("dbrow", None)
    if not self.dbrow:
      db = self.context.bot.db[self.context.guild.id]
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
    
  async def transfer_to_child(self, emoji):
    return
    
  async def get_embed(self):
    level, world, name, handicap, tappable, link, remark = self.dbrow
    embed = discord.Embed(title=f"{level}. {name}", colour=discord.Colour.green(), timestamp=datetime.utcnow())
    if handicap != "NONE":
      embed.add_field(name="Legendary Handicap:", value=handicap, inline=False)
    if tappable != "NONE":
      coin_emoji = self.context.bot.get_emoji(self.context.guild, "coin")
      if coin_emoji is not None:
        tappable = tappable.replace(":moneybag:", f"{coin_emoji}")
      embed.add_field(name="Tappable(s):", value=tappable, inline=False)
    if link != "NONE":
      embed.set_image(url=link)
    embed.set_footer(text=self.footer)
    return embed
