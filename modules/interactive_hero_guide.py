import discord
from datetime import datetime
import string
import modules.custom_exceptions as custom_exceptions
from base.modules.interactive_message import InteractiveMessage, DetermInteractiveMessage
from modules.cyra_constants import world_url, world_hero, hero_menu_url
from base.modules.constants import empty_space, num_emojis, letter_emojis, arrow_emojis

class HeroRootMessage(InteractiveMessage):
  
  def __init__(self, parent=None, **attributes):
    super().__init__(parent, **attributes)
    self.child_emojis = num_emojis[1:8]
    
  async def transfer_to_child(self, emoji):
    world = num_emojis.index(emoji)
    return HeroWorldMessage(world, self)
    
  async def get_embed(self):
    embed = discord.Embed(title=f"Hero Main Menu", timestamp=datetime.utcnow(), colour=discord.Colour.blue(), description="Choose a world (by reacting):")
    embed.set_thumbnail(url=hero_menu_url)
    for k in world_hero.keys():
      if k is not None:
        embed.add_field(name=f"World {k}:", value=" ".join([
          f"{self.context.bot.get_emoji(self.context.guild, hero)}"# if (i+1)%4 != 0
          #else f"{self.context.bot.get_emoji(self.context.guild, hero)}\n"
          for i,hero in enumerate(world_hero[k])] + [empty_space])
        )
    embed.set_footer(text="MAIN MENU")
    return embed
    
class HeroWorldMessage(InteractiveMessage):
  #This class inherits everything from InteractiveMessage and the hero emojis from HeroRootMessage
  
  def __init__(self, world, parent=None, **attributes):
    if not (1 <= world <= 7):
      raise custom_exceptions.DataNotFound("World", world)
    super().__init__(parent, **attributes)
    if self.parent is None:
      self.parent = HeroRootMessage(**attributes)
    self.world = world
    self.child_emojis = [self.context.bot.get_emoji(self.context.guild, key) for key in world_hero[world]]
    
  async def transfer_to_child(self, emoji):
    hero = world_hero[self.world][self.child_emojis.index(emoji)]
    return HeroIndividualMessage(hero, self)
    
  async def get_embed(self):
    embed = discord.Embed(title=f"Hero World {self.world} Menu", timestamp=datetime.utcnow(), colour=discord.Colour.blue())
    embed.set_thumbnail(url=world_url[self.world])
    embed.add_field(
      name="Choose a hero (by reacting):",
      value="\n".join([f"{emoji}: {hero}" for emoji,hero in zip(self.child_emojis, world_hero[self.world])])
    )
    embed.set_footer(text=f"WORLD {self.world}")
    return embed
    
class HeroIndividualMessage(InteractiveMessage):
  def __init__(self, hero, parent=None, **attributes):
    super().__init__(parent, **attributes)
    db = self.context.bot.db[self.context.guild.id]
    result = db.query(f'SELECT ability, type, unlock, shortDescription, tag, world, link, introduction FROM ability JOIN hero on name=hero WHERE name="{hero}" ORDER BY tag')
    if len(result) == 0:
      raise custom_exceptions.HeroNotFound(hero)
    world = result[0][5]
    if self.parent is None:
      self.parent = HeroWorldMessage(world, None, **attributes)
    self.hero = hero
    self.link = result[0][6]
    self.introduction = result[0][7]
    self.abilities = []
    self.child_emojis = []
    self.ability_emojis = [] # match child_emojis to ability name
    self.extra_info = []
    for ability, abilityType, unlock, shortDescription, tag, _, _, _ in result:
      if tag < -2:
        continue
      elif tag == -2: # melee spell
        self.child_emojis.append(letter_emojis["M"]) 
        self.ability_emojis.append(ability)
        self.extra_info.append(f"{letter_emojis['M']} Melee")
      elif tag == -1: # ranged spell
        self.child_emojis.append(letter_emojis["R"]) 
        self.ability_emojis.append(ability)
        self.extra_info.append(f"{letter_emojis['R']} Ranged")
      else: # other spells
        self.child_emojis.append(num_emojis[tag+1]) 
        self.ability_emojis.append(ability)
        if abilityType == "Active":
          activeTag = " (Active)"
        else:
          activeTag = ""
        if unlock:
          unlockTag = f" ({unlock})"
        else:
          unlockTag = ""
        title = f"{num_emojis[tag+1]} {ability}{activeTag}{unlockTag}"
        self.abilities.append((title, shortDescription, tag))
    
  async def transfer_to_child(self, emoji):
    ability = self.ability_emojis[self.child_emojis.index(emoji)]
    return HeroAbilityMessage(self.hero, ability, self)
    
  async def get_embed(self):
    embed = discord.Embed(title=f"**{self.hero}**", description=self.introduction,
                          url=self.link, timestamp=datetime.utcnow(), colour=discord.Colour.blue())
    for title, shortDescription, tag in self.abilities:
      embed.add_field(name=f"{title}", value=shortDescription, inline=False)
    if len(self.extra_info) > 0:
      embed.add_field(name=f"For more information:", value=" ".join(self.extra_info), inline=False)
    emoji = self.context.bot.get_emoji(self.context.guild, self.hero)
    if emoji is not None:
      embed.set_thumbnail(url=emoji.url)
      embed.set_footer(text="HERO CARD", icon_url=emoji.url)
    else:
      embed.set_footer(text="HERO CARD")
    return embed
    
class HeroAbilityMessage(DetermInteractiveMessage):
  def __init__(self, hero, ability, parent=None, **attributes):
    super().__init__(parent, **attributes)
    if self.parent is None:
      self.parent = HeroIndividualMessage(hero, None, **attributes)
    self.inherited = True # this is the bottom interface, inherit its parent
    db = self.context.bot.db[self.context.guild.id]
    result = db.query(f'SELECT upgrade, info, type, url FROM abilityDetail NATURAL JOIN ability WHERE ability="{ability}" AND hero="{hero}" ORDER BY upgrade')
    if len(result) == 0:
      raise custom_exceptions.AbilityNotFound(hero, ability)
    self.hero = hero
    self.ability = ability
    self.atype = result[0][2]
    self.url = result[0][3]
    self.upgrades = []
    for row in result:
      upgrade = row[0]
      if not upgrade:
        upgrade = "Basic"
      if upgrade.startswith("R"):
        upgrade = upgrade.replace("R","Rank ", 1)
      elif upgrade.startswith("Lv"):
        upgrade = upgrade.replace("Lv","Level ", 1)
      upgradeInfo = row[1]
      if upgrade == "Basic" and len(result) == 1:
        self.upgrades.append(("\u200B", upgradeInfo))
      else:
        self.upgrades.append((f"__{upgrade}__:", upgradeInfo))
    
  async def transfer_to_child(self, emoji):
    pass    
    
  async def get_embed(self):
    embed = discord.Embed(title=f"**{self.ability}**", 
      timestamp=datetime.utcnow(), colour=discord.Colour.blue(), 
      description=f"Type: {self.atype}")
    emoji = self.context.bot.get_emoji(self.context.guild, self.hero)
    if emoji is not None:
      embed.set_thumbnail(url=emoji.url)
    if self.url:
      embed.set_footer(text="ABILITY CARD", icon_url=self.url)
    else:
      embed.set_footer(text="ABILITY CARD")
    for upgrade in self.upgrades:
      embed.add_field(name=upgrade[0], value=upgrade[1], inline=False)
    return embed

