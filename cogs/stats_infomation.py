import discord
from discord.ext import commands
import modules.stats as stats
import modules.custom_exceptions as custom_exceptions
import modules.interactive_hero_guide as hero_guide
import modules.interactive_tower_guide as tower_guide
import modules.interactive_stats_guide as stats_guide
from modules.cyra_converter import find_hero, find_ability, toWorld
from modules.cyra_constants import max_level
from base.modules.message_helper import num_emojis, multiple_choice
import asyncio
import string
import typing
import logging

logger = logging.getLogger(__name__)

vague_search_tag_rank = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7']
vague_search_tag_game = ['active', 'passive1', 'passive2', 'passive3']


#An extension for hero commands.
class StatsCog(commands.Cog, name="Stats Commands"):
  def __init__(self, bot):
    self.bot = bot
    
  def get_search_limit(self, guild):
    return self.bot.get_setting(guild, "SEARCH_LIMIT")
    
  async def cog_before_invoke(self, context):
    self.bot.is_willing_to_answer(context)

  #Default error handler for this cog, can be overwritten with a local error handler.
  async def cog_command_error(self, context, error):
    await self.bot.respond_to_error(context, error)
    
  def get_active_time(self, guild):
    return self.bot.get_setting(guild, "ACTIVE_TIME")
    
  @commands.group(
    name="guide",
    help="Shows an interactive guide which can be navigated with reactions.",
    brief="Shows hero guide",
    case_insensitive = True,
    hidden=True,
    invoke_without_command=True
  )
  async def _guide(self, context, world:typing.Optional[toWorld], hero:find_hero=None):
    await context.invoke(self.bot.get_command("guide hero"), world, hero)
        
  @_guide.command(
    name="hero",
    help="Shows a hero guide which can be navigated with reactions.",
    brief="Shows hero guide",
    case_insensitive = True,
    invoke_without_command=True
  )
  async def _hero_guide(self, context, world:typing.Optional[toWorld], hero:find_hero=None):
    timeout = self.get_active_time(context.guild) * 60
    if hero is not None:
      guide = hero_guide.HeroIndividualMessage(hero, context=context, timeout=timeout)
    elif world is not None:
      guide = hero_guide.HeroWorldMessage(world, context=context, timeout=timeout)
    else:
      guide = hero_guide.HeroRootMessage(context=context, timeout=timeout)
    await guide.start()

  @_guide.command(
    name="tower",
    help="Shows a tower guide which can be navigated with reactions.",
    brief="Shows tower guide",
    case_insensitive = True,
    invoke_without_command=True
  )
  async def _tower_guide(self, context, world:typing.Optional[toWorld]):
    timeout = self.get_active_time(context.guild) * 60
    if world is None:
      guide = tower_guide.TowerRootMessage(context=context, timeout=timeout)
    else:
      guide = tower_guide.TowerWorldMessage(world, context=context, timeout=timeout)
    await guide.start()
        
  @commands.command(
    help="Shows information about one hero.\nSpecial thanks to NFdragon#7195 for collecting the data.",
    usage="<hero>",
    brief="Shows hero details"
  )
  async def hero(self, context, *, heroName:find_hero=None):
    await context.invoke(self.bot.get_command("guide hero"), None, heroName)

    
  @commands.command(
    help='Shows information about an ability. Vague searches on abilities such as "melee" "ranged" "rank1" "active" "passive2" are supported. To check the exact name of an ability, use `hero` command\nSpecial thanks to NFdragon#7195 for collecting the data.',
    brief="Shows ability details",
    usage="<hero> <ability>",
    aliases=["spell", "skill"]
  )
  async def ability(self, context, heroName:find_hero=None, *, abilityName:find_ability=None):
    if abilityName is None:
      await context.invoke(self.bot.get_command("hero"), heroName=heroName)
      return
    db = self.bot.db[context.guild.id]
    searchLimit = self.get_search_limit(context.guild)
    # first, search for candidate abilities
    if abilityName.split(" ", 1)[0] in vague_search_tag_rank:
      where_clause = f'ability in (SELECT DISTINCT ability FROM abilityDetail WHERE hero="{heroName}" and upgrade LIKE "{abilityName}%")'
    elif abilityName in vague_search_tag_game:
      gid = vague_search_tag_game.index(abilityName)
      where_clause = f'tag={gid}'
    else: # non-vague search
      where_clause = f'ability LIKE "%{abilityName}%" OR keyword LIKE "%{abilityName}%"'
    result = db.query(f'SELECT ability FROM ability WHERE hero="{heroName}" AND ({where_clause}) ORDER BY tag LIMIT {searchLimit}')
    if len(result) == 0:
      raise custom_exceptions.AbilityNotFound(string.capwords(heroName), string.capwords(abilityName))
    elif len(result) == searchLimit: # too many results
      prefix = self.bot.get_guild_prefix(context.guild) if context.guild else context.prefix
      await context.send(
        f'There are more than {searchLimit-1} abilities that match your input name, '
        f'please input a more accurate name to narrow down the search: `{prefix}ability {heroName.replace(" ","")} <ability>`'
      )
      return
    elif len(result) > 1:
      prefix = self.bot.get_guild_prefix(context.guild) if context.guild else context.prefix
      abilities = [f"{num_emojis[i+1]} `{prefix}ability {heroName.replace(' ', '')} {result[i][0]}`" for i in range(len(result))]
      content = f"There are {len(result)} results that match your keyword, please make a choice by reacting:\n" + '\n'.join(abilities)
      response, msg = await multiple_choice(context, content, num=len(result))
      if response is None:
        return
      valid_row = result[response]
    else:
      valid_row = result[0]
      msg = None
    # send an interactive message
    timeout = self.get_active_time(context.guild) * 60
    guide = hero_guide.HeroAbilityMessage(heroName, valid_row[0], context=context, timeout=timeout)
    await guide.start(msg)
      

  @commands.command(
    help="Displays or compares the stats of a hero at different levels and ranks, [rank] [level] must have the format [num] or [num]->[num], for example, to display Fee at rank 5 lv30, use:\n`{prefix}stats fee 5 30`\nTo compare Fee at rank 5 lv 30 with she at rank 5 lv 35, use:\n`{prefix}statscmp fee 5 30->35`",
    brief="Shows or compares stats",
    aliases=["stat", "statscmp", "statcmp"]
  )
  async def stats(self, context, unit:find_hero, rank, level):
    try:
      if "->" in rank:
        rank = rank.split("->")
        rank1, rank2 = int(rank[0]), int(rank[1])
      else:
        rank1, rank2 = int(rank), int(rank)
    except ValueError:
      raise commands.BadArgument("passed hero rank has an invalid format.")
    try:
      if "->" in level:
        level = level.split("->")
        level1, level2 = int(level[0]), int(level[1])
      else:
        level1, level2 = int(level), int(level)
    except ValueError:
      raise commands.BadArgument("passed hero level has an invalid format.")
    if (not 0 < level1 <= max_level) or (not 0 < level2 <= max_level):
      await context.send(f"Level of {string.capwords(unit)} must be between 1 and {max_level}.")
      return
    result = self.bot.db[context.guild.id].select("hero", unit)
    if result is None:
      raise custom_exceptions.HeroNotFound(string.capwords(unit))
    minRank, maxRank = result["minRank"], result["maxRank"]
    if (not minRank <= rank1 <= maxRank) or (not minRank <= rank2 <= maxRank):
      await context.send(f"Rank of {string.capwords(unit)} must be between rank {minRank} and rank {maxRank}.")
      return
    timeout = self.get_active_time(context.guild) * 60
    if rank1 == rank2 and level1 == level2:
      # display the stats
      guide = stats_guide.StatsMessage(unit, rank1, level1, result, context=context, timeout=timeout)
    else:
      # compare the stats
      guide = stats_guide.StatsCmpMessage(unit, rank1, level1, rank2, level2, result, context=context, timeout=timeout)
    await guide.start()
      
  @commands.command(
    help="Shows information about one enemy.\nSpecial thanks to NFdragon#7195 for collecting the data.",
    brief="Shows enemy details",
    usage="[world] <name>"
  )
  async def enemy(self, context, world:typing.Optional[toWorld], *, enemy=None):
    # check world argument
    if world is not None and (world <= 0 or world >= 8):
      raise custom_exceptions.DataNotFound("World", world)
    searchLimit = self.get_search_limit(context.guild)
    where_clause = []
    if enemy:
      enemy = enemy.lower()
      if enemy in ["bird", "birds", "fly", "air", "flying"]: # aliases for "flying"
        where_clause.append(f'remark="flying"')
      elif enemy in ["boss"]:
        where_clause.append(f'remark="boss"')
      else:
        where_clause.append(f'enemy LIKE "%{enemy}%"')
    if world:
      where_clause.append(f'enemy.world={world}')
    where_clause = " AND ".join(where_clause) if where_clause else True
    result = self.bot.db[context.guild.id].query(
      f"SELECT enemy, enemy.world, type, hp, physicalArmor, magicalArmor, moveSpeed, castSpeed, normalDamage, specialDamage, dodge, abilities, remark, buff, url "
      f"FROM enemy JOIN buff ON buff.unit='enemy' AND enemy.world=buff.world WHERE {where_clause} LIMIT {searchLimit}"
    )
    if len(result) == 0:
      raise custom_exceptions.DataNotFound(f"W{world} Enemy" if world is not None else "Enemy", string.capwords(enemy))
    elif len(result) == searchLimit: # too many results
      prefix = self.bot.get_guild_prefix(context.guild) if context.guild else context.prefix
      await context.send(
        f"There are more than {searchLimit-1} enemies that match your input name, "
        f"please input a more accurate name to narrow down the search: `{prefix}{context.command.qualified_name} {context.command.signature}`"
      )
      return
    elif len(result) > 1:
      prefix = self.bot.get_guild_prefix(context.guild) if context.guild else context.prefix
      enemies = [f"{num_emojis[i+1]} `{prefix}enemy w{result[i][1]} {result[i][0]}`" for i in range(len(result))]
      content = f"There are {len(result)} results that match your keyword, please make a choice by reacting:\n" + '\n'.join(enemies)
      response, msg = await multiple_choice(context, content, num=len(result))
      if response is None:
        return
      valid_row = result[response]
    else:
      valid_row = result[0]
      msg = None
    enemy, world, etype, hp, pa, ma, ms, cs, nd, sd, dg, abilities, remark, buff, url = valid_row
    if etype == "G":
      etype = "Ground"
    elif etype == "F":
      etype = "Flying"
    else:
      etype = "Unknown"
    _stats = {}
    if hp >= 0:
      _stats["HealthPoints"] = hp
    else: # HP is a must-print
      _stats["HealthPoints"] = "UNKNOWN"
    if pa > 0:
      _stats["PhysicalArmor"] = f"{pa:.0%}"
    if ma > 0:
      _stats["MagicalArmor"] = f"{ma:.0%}"
    if ms >= 0:
      _stats["MoveSpeed"] = ms
    else: # MS is a must-print
      _stats["MoveSpeed"] = "UNKNOWN"
    if cs >= 0 and cs != 1:
      _stats["CastSpeed"] = cs
    if nd >= 0:
      _stats["NormalDamage"] = nd
    else: # ND is a must-print
      _stats["NormalDamage"] = "UNKNOWN"
    if sd > 0:
      _stats["SpecialDamage"] = sd
    if dg > 0:
      _stats["Dodge"] = f"{dg}%"
    statsMsg = "\n".join([f"`{key:<13} = {value:<6}`" for key, value in _stats.items()])
    embed = discord.Embed(
      title=f"**{enemy}**", 
      timestamp=context.message.created_at, 
      description=f"World {world} {etype} Enemy"
    )
    embed.add_field(name="__Stats__:", value=statsMsg, inline=False)
    embed.add_field(name="__Abilities__:", value=abilities, inline=False)
    if (not remark == "boss") and buff:
      embed.add_field(name="__Extra Buffs__:", value=f"{string.capwords(enemy)} receives {buff}", inline=False)
    if url:
      embed.set_thumbnail(url=url)
    embed.set_footer(text=f"WORLD {world} ENEMY")
    if msg is not None:
      await msg.clear_reactions()
      await msg.edit(content=None, embed=embed)
    else:
      await context.send(embed=embed)
        
  @commands.command(
    help="Shows information about one tower.",
    brief="Shows tower details",
    usage="[world] <name>"
  )
  async def tower(self, context, world:typing.Optional[toWorld], *, tower=None):
    # check world argument
    if world is not None and (world <= 0 or world >= 8):
      raise custom_exceptions.DataNotFound("World", world) 
    if tower is None:
      await context.invoke(self.bot.get_command("guide tower"), world)
      return
    tower = tower.lower()
    searchLimit = self.get_search_limit(context.guild)
    if world is None:
      if tower in ["barrack"]:
        where_clause = f'type="{tower}"'
      else:
        where_clause = f'tower LIKE "%{tower}%"'
    else:
      if tower in ["barrack"]:
        where_clause = f'type="{tower}" AND tower.world={world}'
      else:
        where_clause = f'tower LIKE "%{tower}%" AND tower.world={world}'
    result = self.bot.db[context.guild.id].query(
      f"SELECT tower.tower, tower.world, basic, starUpgrade, lvUpgrade, leftBranchName, leftBranch, rightBranchName, rightBranch, reinforcement, buff, url "
      f"FROM tower JOIN buff ON tower.type=buff.unit AND tower.world=buff.world WHERE {where_clause} LIMIT {searchLimit}"
    )
    if len(result) == 0:
      raise custom_exceptions.DataNotFound(f"W{world} Tower" if world is not None else "Tower", string.capwords(tower))
    elif len(result) == searchLimit: # too many results
      prefix = self.bot.get_guild_prefix(context.guild) if context.guild else context.prefix
      await context.send(
        f"There are more than {searchLimit-1} towers that match your input name, "
        f"please input a more accurate name to narrow down the search: `{prefix}{context.command.qualified_name} {context.command.signature}`"
      )
      return
    elif len(result) > 1:
      prefix = self.bot.get_guild_prefix(context.guild) if context.guild else context.prefix
      towers = [f"{num_emojis[i+1]} `{prefix}tower w{result[i][1]} {result[i][0]}`" for i in range(len(result))]
      content = f"There are {len(result)} results that match your keyword, please make a choice by reacting:\n" + '\n'.join(towers)
      response, msg = await multiple_choice(context, content, num=len(result))
      if response is None:
        return
      valid_row = result[response]
    else: # send an interactive message
      valid_row = result[0]
      msg = None
    timeout = self.get_active_time(context.guild) * 60
    tower = valid_row[0]
    world = valid_row[1]
    towerInfo = valid_row[2:]
    guide = tower_guide.TowerIndividualMessage(world, tower, context=context, timeout=timeout, towerInfo=towerInfo)
    await guide.start(msg)
      

  @commands.group(
    name="basic",
    brief="Shows basic terms",
    case_insensitive = True,
    invoke_without_command=True
  )
  async def _basic(self, context):
    await context.send_help("basic")
  
  @_basic.command(
    name="damage",
    brief="Basic terms about damage",
  )
  async def _basic_damage(self, context):
    embed = discord.Embed(title="Damage", timestamp=context.message.created_at)
    embed.add_field(name="- Normal Damage (ND):", value="A basic attribute of a unit, usually contributes to damage of normal attacks.", inline=False)
    embed.add_field(name="- Special Damage (SD):", value="Spell damage in game, a basic attribute of a unit, usually contributes to damage of special attacks.", inline=False)
    embed.add_field(name="- Physical Damage (PD):", value="A kind of damage that can be reduced by physical armor.", inline=False)
    embed.add_field(name="- Magical Damage (MD):", value="A kind of damage that can be reduced by magical armor.", inline=False)
    embed.add_field(name="- True Damage (TD):", value="A kind of damage that cannot be reduced by any kind of armor.", inline=False)
    embed.add_field(name="- Percentage Damage (%):", value="A kind of damage that reduces percentage of HP, ignoring dodge and armor.", inline=False)
    embed.set_footer(text="BASIC: DAMAGE")
    await context.send(embed=embed)
  
  @_basic.command(
    name="speed",
    brief="Basic terms about speed",
  )
  async def _basic_speed(self, context):
    embed = discord.Embed(title="Speed", timestamp=context.message.created_at)
    embed.add_field(name="- Move Speed (MS):", value="Movement speed of a unit, maximum is 3.25.", inline=False)
    embed.add_field(name="- Caste Speed (CS):", value="Speed of how fast the spell cooldowns finish, maximum is 3.25 (except towers).", inline=False)
    embed.add_field(name="- Play Speed (PS):", value="Animation speed. Speed for casting animations, maximum is 3.25 (except towers).", inline=False)
    embed.set_footer(text="BASIC: SPEED")
    await context.send(embed=embed)
    
  @_basic.command(
    name="armor",
    brief="Basic terms about armor",
  )
  async def _basic_armor(self, context):
    embed = discord.Embed(title="Armor", timestamp=context.message.created_at)
    embed.add_field(name="- Physical Armor (PA):", value="An armor that reduces physical damage received by some percentage, enemies' armor can go negative but allies' cannot.", inline=False)
    embed.add_field(name="- Magical Armor (MA):", value="An armor that reduces magical damage received by some percentage, enemies' armor can go negative but allies' cannot.", inline=False)
    embed.set_footer(text="BASIC: ARMOR")
    await context.send(embed=embed)
	
  @_basic.command(
    name="ability",
    brief="Basic terms about abilities",
    aliases=["spell", "skill"]
  )
  async def _basic_ability(self, context):
    embed = discord.Embed(title="Ability", timestamp=context.message.created_at, description="Spells can be categorized into following types based on how they are triggered:")
    embed.add_field(name="- Active Spells:", value="Spells that are cast by the player.", inline=False)
    embed.add_field(name="- Passive Spells:", value="Spells that are cast automatically. Passive spells include melee passives, which can be cast when engaged in melee, and ranged passives, which can be cast when unengaged.", inline=False)
    embed.add_field(name="- Buff/Aura Spells:", value="Spells that are triggered automatically without cast action.", inline=False)
    embed.set_footer(text="BASIC: ABILITY")
    await context.send(embed=embed)
    
  @commands.command(
    name="item",
    help="Shows information about one power item",
    brief="Shows power item",
    aliases=["consumable"]
  )
  async def _item(self, context, *, name=None):
    if name is None:
      await context.send_help("item")
      return
    name = name.lower()
    if name in ["armageddon"]:
      name = "armageddon"
      cooldown = 20
      description = "Deals `600 TD + 50% hp` damage to 20 non-boss enemies, and `10% hp` damage to all bosses."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/b/b5/Armageddon_Consumable.png/revision/latest?cb=20200822204546"
    elif name in ["fire potion", "fire", "bomb"]:
      name = "fire potion"
      cooldown = 10
      description = "Deals `400 TD` to enemies in AOE range 2."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/9/92/Bomb_Consumable.png/revision/latest?cb=20200822204547"
    elif name in ["freeze potion", "freeze"]:
      name = "freeze potion"
      cooldown = 60
      description = "Freeze all enemies for 5s."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/4/40/Freeze_Consumable.png/revision/latest?cb=20200822204547"
    elif name in ["freeze potion lv2", "freeze lv2", "freeze2"]:
      name = "freeze potion lv2"
      cooldown = 60
      description = "Freeze all enemies for 7.5s."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/4/40/Freeze_Consumable.png/revision/latest?cb=20200822204547"
    elif name in ["gold boost", "gold"]:
      name = "gold boost"
      cooldown = 30
      description = "Instantly grants 500 coins."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/0/0c/Coin_Consumable.png/revision/latest?cb=20200822204547"
    elif name in ["healing potion", "heal potion", "healing", "heal"]:
      name = "healing potion"
      cooldown = 5
      description = "Revives dead heroes, and in 15s heals allies in AOE range 3 `150 HP`."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/2/2a/Revive_Consumable.png/revision/latest?cb=20200822204547"
    elif name in ["meteor"]:
      name = "meteor"
      cooldown = 30
      description = (
        f"Instantly kills all non-boss enemies in AOE range 4, deals `9% hp` damage to bosses, and summons 2 lava golems.\n"
        f"After that, drops 5 more small meteors to random enemies with AOE range 1 and same damage effect.\n"
        f"Lava golems has 400 hp, and deals `42 TD + 10% hp` damage on a non-boss enemy, or `1% hp` damage on a boss every 1s, last 20s."
      )
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/1/18/Inferno_Consumable.png/revision/latest?cb=20200822204547"
    elif name in ["summon potion", "summon"]:
      name = "summon potion"
      cooldown = 5
      description = "Summons a lava golem with 200 hp, dealing `42 TD + 10% hp` damage on a non-boss enemy, or `1.25% hp` damage on a boss every 1s."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/3/3d/Summon_Consumable.png/revision/latest?cb=20200822204547"
    else:
      raise custom_exceptions.DataNotFound("Item", string.capwords(name))
    embed = discord.Embed(title=f"**{string.capwords(name)}**", timestamp=context.message.created_at, description=f"Cooldown: {cooldown}s")
    embed.add_field(name="Effects:", value=description, inline=False)
    if url:
      embed.set_footer(text="ITEM", icon_url=url)
    else:
      embed.set_footer(text="ITEM")
    await context.send(embed=embed)
    
  @commands.command(
    name="buff",
    help="Shows information about one buff/debuff",
    brief="Shows buff/debuff",
    aliases=["debuff"]
  )
  async def _buff(self, context, *, name=None):
    if name is None:
      await context.send_help("buff")
      return
    name = name.lower()
    if name in ["haste"]:
      name = "haste"
      description = "Increase the speed of a unit by some percentage value."
      stack = "Most of the hastes from different sources stack with each other, except:\n1) Haste x1.5 from towers, but theoretically we cannot use towers from different worlds at the same time so not a problem\n2) Haste x1.5 from enemies, this usually is not a problem either\nAnd it's also worth mentioning that the haste x1.5 from enemies' aura stacks with haste x1.5 from tower's aura."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/2/27/Haste.jpg/revision/latest?cb=20200822214559"
    elif name in ["slow"]:
      name = "slow"
      description = "Decrease the speed of a unit by some percentage value."
      stack = "There are 4 kinds of slows and they stack with each other.\n1) The most common slow by 50% with a clock on top\n2) Slow by 25% from Sethos' R6 sandstorm\n3) Move speed x0.4 from Smoulder's r4 aura\n4) Slow from Shamiko"
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/5/54/Slow.jpg/revision/latest?cb=20200822214559"
    elif name in ["cold"]:
      name = "cold"
      description = "Decrease the move speed by 50% and the animation speed by 25%. The slow on animation speed may stop some heroes from casting special spells."
      stack = "The speed reduction stacks with slow buffs."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/7/70/Cold.jpg/revision/latest?cb=20200822214558"
    elif name in ["decrepit", "decrepify"]:
      name = "decrepit"
      description = "Decrease the speed and reduce the armor of a unit. This includes a decrepit from Yan (speed x0.35, armor -0.25) and a stronger version from W4 Small Golem (speed x0.25, armor -0.5)."
      stack = "The speed reduction stacks with slow buff and the armor reduction stacks with armor buff."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/e/e6/Decrepify.jpg/revision/latest?cb=20200822214559"
    elif name in ["poison", "venom"]:
      name = "poison"
      description = "Ignores the shield points and deals damage (usually magical or true damage) over time. This includes a normal poison which deals `(3+0.05 ND) TD` every 0.42s and others from heroes."
      stack = "There are several different poison buffs with different damage multipliers, and they stack with each other. For example venom from Sethos stacks with posion from Mabyn."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/8/87/Poison.jpg/revision/latest?cb=20200822214559"
    elif name in ["burn", "burning"]:
      name = "burn"
      description = "Deals `(2+0.05 ND) PD` every 0.4s."
      stack = "There is only one kind of burn buff so they cannot stack even they are from different sources."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/8/8c/Burn.jpg/revision/latest?cb=20200822214559"
    elif name in ["bleed", "bleeding"]:
      name = "bleed"
      description = "Deals `(2+0.05 ND) PD` every 0.33s while moving."
      stack = "There is only one kind of bleed buff so they cannot stack even they are from different sources."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/7/72/Bleed.jpg/revision/latest?cb=20200822215031"
    elif name in ["shield", "armor"]:
      name = "shield"
      description = "Gives some max shield points and increase the armor of a unit."
      stack = "Shield buffs from different sources stack with each other, but because they only gives max shield points, the shield points won't be restored if the unit loses some shield in battle."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/4/43/Shield.jpg/revision/latest?cb=20200822214557"
    elif name in ["armor break", "break armor"]:
      name = "armor break"
      description = "Reduce the armor of a unit. Could be a percentage reduce (e.g. x0.5) or a value reduce (e.g. -0.2)."
      stack = "The armor breaks with different values can stack with each other. For example, a unit can receive x0.5 and x0.7 armor break and totally the armor will be x0.35."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/0/02/Armor_break.jpg/revision/latest?cb=20200822214559"
    elif name in ["terror", "terrify"]:
      name = "terror"
      description = "Makes a unit to move backward, but the unit is still able to attack."
      stack = "Terror from Shamiko/Elara/Mabyn are literally different, but they may interfere each other due to some bug."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/4/48/Terror.jpg/revision/latest?cb=20200822214558"
    elif name in ["blind"]:
      name = "blind"
      description = "Increase the miss chance of a unit by 50%."
      stack = "All blinds buffs are the same and cannot stack."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/7/7b/Blind.jpg/revision/latest?cb=20200822214559"
    elif name in ["curse", "silence"]:
      name = "curse/silence"
      description = "Stops a unit from attacking or casting, also stops the cooldowns. This buff is either from W2 Heretic or W4 Pyromancer Tower."
      stack = ""
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/9/97/Curse.jpg/revision/latest?cb=20200822214558"
    elif name in ["stun", "freeze", "shock", "cocoon", "paralysis", "bind"]:
      name = "stun/freeze/shock/..."
      description = "Stuns a unit so it cannot do anything."
      stack = "Buffs with different names can stack with each other, but with the same name a buff will only replace an older one."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/a/a7/Stun.jpg/revision/latest?cb=20200822214559"
    elif name in ["cloak"]:
      name = "cloak"
      description = "Make a unit invisible to most of the ranged attacks, but it may be damaged from AOE effect, and will be revealed by melee engagement."
      stack = ""
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/5/56/Cloak.jpg/revision/latest?cb=20200822214559"
    elif name in ["spirit curse"]:
      name = "spirit curse"
      description = "Reduce the damage by 25% and deals `(5+0.05 ND) TD` every 0.42s."
      stack = "This cursed poison can stack with other poisons."
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/8/85/Spirit_curse.jpg/revision/latest?cb=20200822214559"
    elif name in ["polymorph", "poly", "polymorphism"]:
      name = "polymorph"
      description = "Reduce the HP to 1/4, move speed to 1/2, remove all armor, and silence the unit."
      stack = ""
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/e/e0/Polymorph.jpg/revision/latest?cb=20200901022035"
    elif name in ["charm"]:
      name = "charm"
      description = "Make the enemy fight for you. Your units can benifit from aura of the enemy. Some charmed enemies don't engage in melee, including W3 Mummy, W4 Magic Book & Cloud Sunfish, W6 Origami Crane & Harpy."
      stack = ""
      url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/d/de/Charm.jpg/revision/latest?cb=20200901023011"
    else:
      raise custom_exceptions.DataNotFound("Buff", string.capwords(name))
    embed = discord.Embed(title=f"**{string.capwords(name)}**", timestamp=context.message.created_at)
    if description:
      embed.add_field(name="Effects:", value=description, inline=False)
    if stack:
      embed.add_field(name="Stack information:", value=stack, inline=False)
    embed.set_footer(text="BUFF/DEBUFF")
    if url:
      embed.set_thumbnail(url=url)
    await context.send(embed=embed)

#This function is needed for the load_extension routine.
def setup(bot):
  bot.add_cog(StatsCog(bot))
  logging.info("Added stats cog.")

