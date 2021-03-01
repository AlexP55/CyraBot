import discord
from datetime import datetime
import string
import modules.custom_exceptions
from base.modules.interactive_message import InteractiveMessage
from modules.cyra_constants import world_url, tower_menu_url
from base.modules.constants import num_emojis, text_emojis, letter_emojis, item_emojis
import enum

class TowerRootMessage(InteractiveMessage):
  def __init__(self, parent=None, **attributes):
    super().__init__(parent, **attributes)
    db = self.context.bot.db[self.context.guild.id]
    result = db.query('SELECT tower, world FROM tower ORDER BY world')
    self.towers = {}
    for tower, world in result:
      if world not in self.towers:
        self.towers[world] = []
        self.child_emojis.append(num_emojis[world])
      self.towers[world].append(tower)

  async def transfer_to_child(self, emoji):
    world = num_emojis.index(emoji)
    return TowerWorldMessage(world, self)
    
  async def get_embed(self):
    embed = discord.Embed(title=f"Tower Main Menu", timestamp=datetime.utcnow(), colour=discord.Colour.blue(), description="Choose a world (by reacting):")
    embed.set_thumbnail(url=tower_menu_url)
    for key, towerList in self.towers.items():
      embed.add_field(name=f"World {key}:", value="\n".join(towerList))
    embed.set_footer(text="MAIN MENU")
    return embed

class TowerWorldMessage(InteractiveMessage):
  def __init__(self, world, parent=None, **attributes):
    if not (1 <= world <= 7):
      raise custom_exceptions.DataNotFound("World", world)
    super().__init__(parent, **attributes)
    if self.parent is None:
      self.parent = TowerRootMessage(**attributes)
    db = self.context.bot.db[self.context.guild.id]
    self.towers = db.query(f'SELECT tower, description1, description2 FROM tower WHERE world="{world}"')
    self.world = world
    self.child_emojis = num_emojis[1:len(self.towers)+1]
    
  async def transfer_to_child(self, emoji):
    tower = self.towers[self.child_emojis.index(emoji)][0]
    return TowerIndividualMessage(self.world, tower, self)
    
  async def get_embed(self):
    embed = discord.Embed(title=f"Tower World {self.world} Menu", timestamp=datetime.utcnow(), colour=discord.Colour.blue(),
      description="Choose a tower (by reacting):")
    embed.set_thumbnail(url=world_url[self.world])
    for emoji, towerInfo in zip(self.child_emojis, self.towers):
      tower, description1, description2 = towerInfo
      embed.add_field(name=f"{emoji} {string.capwords(tower)}:", 
        value=f"- {description1}\n- {description2}", inline=False)
    embed.set_footer(text=f"WORLD {self.world}")
    return embed

  
class TowerIndividualMessage(InteractiveMessage):
  class InfoType(enum.Enum):
    basic = 0
    star = 1
    level = 2
    left = 3
    right = 4
    
  def __init__(self, world, tower, parent=None, **attributes):
    super().__init__(parent, **attributes)
    if self.parent is None:
      self.parent = TowerWorldMessage(world, None, **attributes)
    self.info_type = TowerIndividualMessage.InfoType.basic
    self.towerInfo = attributes.pop("towerInfo", None)
    if self.towerInfo is None: # no result passed in attributes, then go for a new db query
      db = self.context.bot.db[self.context.guild.id]
      result = db.query(
        f'SELECT basic, starUpgrade, lvUpgrade, leftBranchName, leftBranch, rightBranchName, rightBranch, reinforcement, buff, url '
        f'FROM tower JOIN buff ON tower.type=buff.unit AND tower.world=buff.world WHERE tower.tower="{tower}" and tower.world={world}'
      )
      if len(result) == 0:
        raise custom_exceptions.DataNotFound(f"W{world} Tower", string.capwords(tower))
      self.towerInfo = result[0]
    self.towerInfo = list(self.towerInfo)
    self.tower = tower
    self.world = world
    coin_emoji = self.context.bot.get_emoji(self.context.guild, "coin")
    star_emoji = self.context.bot.get_emoji(self.context.guild, "star")
    if star_emoji is not None:
      self.towerInfo[1] = self.towerInfo[1].replace("⭐", f"{star_emoji}")
    else:
      star_emoji = item_emojis["star"]
    if coin_emoji is not None:
      self.towerInfo[2] = self.towerInfo[2].replace("💰", f"{coin_emoji}")
      self.towerInfo[4] = self.towerInfo[4].replace("💰", f"{coin_emoji}")
      self.towerInfo[6] = self.towerInfo[6].replace("💰", f"{coin_emoji}")
      self.towerInfo[7] = self.towerInfo[7].replace("💰", f"{coin_emoji}")
    self.child_emojis = [text_emojis["info"], star_emoji, text_emojis["up"], letter_emojis["L"], letter_emojis["R"]]
    self.emoji_descriptions = ["Basic Info", "Star Upgrade", "Level Upgrade", "Left Branch", "Right Branch"]
    
  async def transfer_to_child(self, emoji):
    new_info_type = TowerIndividualMessage.InfoType(self.child_emojis.index(emoji))
    if self.info_type != new_info_type:
      self.info_type = new_info_type
      return self
    else:
      return None
    
  async def get_embed(self):
    basic, starUpgrade, lvUpgrade, leftBranchName, leftBranch, rightBranchName, rightBranch, reinforcement, buff, url = self.towerInfo
    embed = discord.Embed(
      title=f"**{string.capwords(self.tower)}**", colour=discord.Colour.blue(),
      timestamp=datetime.utcnow(), description=f"{basic}"
    )
    if self.info_type == TowerIndividualMessage.InfoType.basic:
      if buff:
        embed.add_field(name="Extra Buffs:", value=f"{string.capwords(self.tower)} receives {buff}", inline=False)
      embed.add_field(name="For more information:", 
        value="\n".join([f"{emoji} {description}" for emoji, description in zip(self.child_emojis, self.emoji_descriptions)]))
    elif self.info_type == TowerIndividualMessage.InfoType.star:
      embed.add_field(name="Star Upgrade:", value=starUpgrade, inline=False)
    elif self.info_type == TowerIndividualMessage.InfoType.level:
      embed.add_field(name="Level Upgrade:", value=lvUpgrade, inline=False)
    elif self.info_type == TowerIndividualMessage.InfoType.left:
      embed.add_field(name=f"Left Branch: __{leftBranchName}__", value=leftBranch, inline=False)
      if reinforcement:
        embed.add_field(name="Reinforcements:", value=reinforcement, inline=False)
    elif self.info_type == TowerIndividualMessage.InfoType.right:
      embed.add_field(name=f"Right Branch: __{rightBranchName}__", value=rightBranch, inline=False)
      if reinforcement:
        embed.add_field(name="Reinforcements:", value=reinforcement, inline=False)
    if url:
      embed.set_thumbnail(url=url)
    embed.set_footer(text=f"WORLD {self.world} TOWER")
    return embed
