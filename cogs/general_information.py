import discord
from discord.ext import commands
import random
import modules.custom_exceptions as custom_exceptions
import typing
from modules.cyra_converter import find_hero, toLevelWorld, toWorld, toMode, find_achievement, numberComparisonConverter, find_farmable_achievement
from modules.cyra_constants import facts, elixir_cost, elixir_cost_hero, max_level, tappables
from base.modules.basic_converter import BoolConverter
from base.modules.interactive_message import InteractiveSelectionMessage, InteractiveEndMessage
import modules.interactive_level_guide as level_guide
import logging

logger = logging.getLogger(__name__)


class InfoCog(commands.Cog, name="Information Commands"):
  def __init__(self, bot):
    self.bot = bot
    
  async def cog_before_invoke(self, context):
    self.bot.is_willing_to_answer(context)

  #Default error handler for this cog, can be overwritten with a local error handler.
  async def cog_command_error(self, context, error):
    await self.bot.respond_to_error(context, error)
    
  def get_search_limit(self, guild):
    return self.bot.get_setting(guild, "SEARCH_LIMIT")

  @commands.group(
    brief="Shows info on elixir",
    case_insensitive = True,
    invoke_without_command=True,
    usage="[hero] [lvStart=1] [lvEnd=lvStart+1]",
    help="Shows general elixir information or calculates how many elixirs are required to upgrade a hero.\nExample: `{prefix}elixir fee 1 30` or `{prefix}elixir fee 1->30`"
  )
  async def elixir(self, context, hero:find_hero=None, lvStart:numberComparisonConverter=1, lvEnd=-1):
    if hero is None:
      prefix = self.bot.get_guild_prefix(context.guild) if context.guild else context.prefix
      elixir_str = self.bot.get_emoji(context.guild, 'elixir')
      elixir_str = elixir_str if elixir_str else ""
      await context.send(
        f"Elixir {elixir_str} is a resource in Realm Defense.\n"
        f"It's main purpose is to level up your heroes.\n"
        f"It can be obtained from the Elixir Mine and as rewards from Mabyn's Wheel, Tournaments and Shattered Realms.\n"
        f"For info on the Elixir Mine, use the `{prefix}elixir mine` command.\n"
        f"To show the elixir cost for upgrading a hero, use `{prefix}elixir <hero> <lvStart> <lvEnd>`"
      )
      return
    if isinstance(lvStart, tuple):
      lvEnd = lvStart[1]
      lvStart = lvStart[0]
    if lvEnd <= lvStart:
      lvEnd = lvStart + 1
    if lvStart <= 0 or lvEnd > max_level:
      await context.send(f"Level of {hero} must be between 1 and {max_level}.")
      return
    cost = elixir_cost(hero, lvStart, lvEnd)
    hero_str = self.bot.get_emoji(context.guild, hero)
    hero_str = hero_str if hero_str else hero
    elixir_str = self.bot.get_emoji(context.guild, 'elixir')
    elixir_str = elixir_str if elixir_str else "elixirs"
    await context.send(
      f"Upgrading {hero_str} from level {lvStart} to {lvEnd} costs:\n"
      f"{cost} {elixir_str}"
    )
    
  @elixir.command(
    name="upgrade",
    brief="Shows which level can be upgraded to",
    help="Shows which level can be upgraded to given the amount of elixirs.",
    aliases=["up"]
  )
  async def _elixir_up(self, context, hero:find_hero, numElixir:int, lvStart:int=1):
    if lvStart <= 0 or lvStart >= max_level:
      await context.send(f"Starting level of {hero} must be between 1 and {max_level-1}.")
      return
    cost_list = elixir_cost_hero[hero]
    cost = 0
    for lv in range(lvStart, len(cost_list)+1):
      if cost + cost_list[lv-1] > numElixir:
        break
      cost += cost_list[lv-1]
    else:
      lv += 1
    hero_str = self.bot.get_emoji(context.guild, hero)
    hero_str = hero_str if hero_str else hero
    elixir_str = self.bot.get_emoji(context.guild, 'elixir')
    elixir_str = elixir_str if elixir_str else "elixirs"
    reply = (f"You are able to upgrade {hero_str} from lv{lvStart} to lv{lv}, "
             f"with {numElixir-cost} {elixir_str} remaining.")
    if lv < len(cost_list):
      reply = f"{reply}\nThe next level needs {cost_list[lv-1]} {elixir_str}."
    await context.send(reply)
    
  @elixir.command(
    brief="Shows info on elixir mine",
  )
  async def mine(self, context):
    gem_str = self.bot.get_emoji(context.guild, 'gem')
    gem_str = gem_str if gem_str else "gems"
    elixir_str = self.bot.get_emoji(context.guild, 'elixir')
    elixir_str = elixir_str if elixir_str else "elixirs"
    await context.send(
      f"Elixir Mine can be unlocked in World 1.\n"
      f"It has a total of 10 levels.\n"
      f"Level  1:    0 {gem_str} (  5{elixir_str}/hour, Capacity:   40{elixir_str})\n"
      f"Level  2:   50 {gem_str} ( 15{elixir_str}/hour, Capacity:  120{elixir_str})\n"
      f"Level  3:  300 {gem_str} ( 30{elixir_str}/hour, Capacity:  240{elixir_str})\n"
      f"Level  4:  600 {gem_str} ( 45{elixir_str}/hour, Capacity:  360{elixir_str})\n"
      f"Level  5: 1000 {gem_str} ( 75{elixir_str}/hour, Capacity:  600{elixir_str})\n"
      f"Level  6: 1500 {gem_str} (105{elixir_str}/hour, Capacity:  840{elixir_str})\n"
      f"Level  7: 2000 {gem_str} (140{elixir_str}/hour, Capacity: 1260{elixir_str})\n"
      f"Level  8: 2500 {gem_str} (180{elixir_str}/hour, Capacity: 2520{elixir_str})\n"
      f"Level  9: 4000 {gem_str} (250{elixir_str}/hour, Capacity: 4000{elixir_str})\n"
      f"Level 10: 6000 {gem_str} (315{elixir_str}/hour, Capacity: 7560{elixir_str})"
    )

  @commands.command(
    name="level",
    brief="Shows a selected level",
    aliases=["lvl","lv"]
  )
  async def _level(self, context, world:typing.Optional[toLevelWorld], level=None):
    timeout = self.bot.get_setting(context.guild, "ACTIVE_TIME") * 60
    if not world and not level:
      guild = level_guide.LevelRootMessage(context=context, timeout=timeout)
    elif not level:
      guild = level_guide.LevelWorldMessage(world, context=context, timeout=timeout)
    else:
      level = level.title()
      guild = level_guide.LevelIndividualMessage(level, context=context, timeout=timeout)
    await guild.start()
    
  @commands.group(
    name="achieve",
    brief="Farms achievements",
    case_insensitive = True,
    invoke_without_command=True,
    aliases=["achievement"],
    help="Shows which way is the best to farm achievements/daily missions. This command assumes you will spend time on entering and exiting a level, and the results are based on the time efficiency. If you want the results to be based on absolute number, input true at the end of argument.\nFor example, to show which level is the fastest to farm 200 goblins, use:\n`{prefix}achieve goblin 200`\nTo show which level is has the highest spider kills per second, use:\n`{prefix}achieve spider`\nTo make the results based on absolute kills, use:\n`{prefix}achieve spider true`\nTo show which w6 legendary level is the fastest to complete, use:\n`{prefix}achieve w6 legendary fast`\nTo show where to find a specific tappable trap, use:\n`{prefix}achieve trap`"
  )
  async def _achieve(self, context, world:typing.Optional[toWorld], mode:typing.Optional[toMode], achievement:find_achievement="Fast", 
                     num:typing.Optional[int]=None, sort_by_absolute:typing.Optional[bool]=None):
    # check world argument
    if world is not None and (world <= 0 or world >= 8):
      raise custom_exceptions.DataNotFound("World", world)
    if world == 7 and achievement == "Slime": # extra parsing for w7 slime
      achievement = "W7_Slime"
    timeout = self.bot.get_setting(context.guild, "ACTIVE_TIME") * 60
    if achievement in tappables:
      if achievement == "Tappable":
        where_clause = [f'LENGTH(tappable)>0']
      elif achievement == "Mercenary Board":
        where_clause = [f'extra LIKE "%{achievement}%"']
      else:
        where_clause = [f'tappable LIKE "%{achievement}%"']
      if world:
        where_clause.append(f"world={world}")
      where_clause = " AND ".join(where_clause) if where_clause else "TRUE"
      searchLimit = self.bot.get_setting(context.guild, "SEARCH_LIMIT")
      result = self.bot.db[context.guild.id].query(f"SELECT * FROM levels WHERE ({where_clause}) LIMIT {searchLimit}")
      if len(result) == 0:
        raise custom_exceptions.DataNotFound("Achievement", f"{achievement} in W{world}" if world else achievement)
      elif len(result) == searchLimit: # too many results
        await context.send(
          f'There are more than {searchLimit-1} levels that match your input condition, '
          f'please input a more accurate condition to narrow down the search'
        )
        return
        
      def getInteractiveMessage(ind, parent=None):
        row = result[0]
        if parent is None:
          return level_guide.LevelIndividualMessage(row[0], context=context, timeout=timeout, dbrow=row)
        else:
          return level_guide.LevelIndividualMessage(row[0], parent=parent, dbrow=row)
        
      if len(result) > 1:
        levels = [f"`W{result[i][1]} lv.{result[i][0]:<5} {result[i][2]}`" for i in range(len(result))]
        content = f"You can complete the mission **{achievement}** in below levels, react to see the details of a level:"
        guide = InteractiveSelectionMessage(selections=levels, transfer=getInteractiveMessage, description=content, 
          colour=discord.Colour.green(), context=context, timeout=timeout)
        await guide.start()
      else:
        guide = getInteractiveMessage(0)
        await guide.start()
    else:
      guide = level_guide.LevelAchievementMessage(achievement, num, context=context, timeout=timeout, world=world, mode=mode, sort_by_absolute=sort_by_absolute)
      await guide.start()
      
  @_achieve.command(
    name="plan",
    brief="Optimizes achievement farming",
    usage="[world] [mode] <achievements> <num>... [sort_by_absolute]",
  )
  async def _achieve_plan(self, context, world:typing.Optional[toWorld], mode:typing.Optional[toMode], *args):
    if len(args) < 2:
      raise commands.BadArgument("Invalid input, must input an achievementand a number")
    achievements = []
    nums = []
    sort_by_absolute = False
    args = list(args)
    while len(args) > 1:
      try:
        achievement = find_farmable_achievement(args.pop(0))
        if world == 7 and achievement == "Slime": # extra parsing for w7 slime
          achievement = "W7_Slime"
        achievements.append(achievement)
        nums.append(int(args.pop(0)))
      except Exception as e:
        if isinstance(e, commands.BadArgument):
          raise e
        else:
          raise commands.BadArgument("Invalid input, must input a number after each achievement")
    if args:
      try:
        sort_by_absolute = BoolConverter(args.pop(0))
      except:
        pass
    timeout = self.bot.get_setting(context.guild, "ACTIVE_TIME") * 60
    guide = level_guide.AchievementPlanMessage(achievements, nums, context=context, timeout=timeout, world=world, mode=mode, sort_by_absolute=sort_by_absolute)
    await guide.start()

  @commands.command(
    brief="Displays link to wiki",
  )
  async def wiki(self, context):
#    await context.send(f"Wiki: https://realm-defense-hero-legends-td.fandom.com/wiki/Realm_Defense:_Hero_Legends_TD_Wiki")
    embed = discord.Embed(title="Realm Defense Wiki", url="https://realm-defense-hero-legends-td.fandom.com/wiki/Realm_Defense:_Hero_Legends_TD_Wiki",
                          description="The fandom wiki for Realm Defense.")
    embed.set_image(url="https://vignette.wikia.nocookie.net/realm-defense-hero-legends-td/images/2/27/RealmDefenseBanner.jpg/revision/latest?cb=20191107143646")
    await context.send(content=None, embed=embed)


  @commands.group(
    brief="Shows info on leagues",
    case_insensitive = True,
    invoke_without_command=True,
    aliases=["league"]
  )
  async def leagues(self, context):
    embed = discord.Embed(title="Tournament Leagues")
    embed.add_field(name="Bronze League:",   value="Top 3/15 promote to Silver League.",   inline=False)
    embed.add_field(name="Silver League:",   value="Top 3/15 promote to Gold League.",     inline=False)
    embed.add_field(name="Gold League:",     value="Top 3/20 promote to Platinum League.", inline=False)
    embed.add_field(name="Platinum League:", value="Top 3/25 promote to Diamond League.",  inline=False)
    embed.add_field(name="Diamond League:",  value="Top 5/30 promote to Master League.",   inline=False)
    embed.add_field(name="Master League:",   value="Top 5/30 promote to Legend League.",   inline=False)
    embed.add_field(name="Legend League:",   value="Top 3/50 earn a grandmaster title.",   inline=False)
    prefix = self.bot.get_guild_prefix(context.guild) if context.guild else context.prefix
    embed.add_field(name="For rewards:",   value=f"`{prefix}league reward <league>`",   inline=False)
    embed.set_footer(text="LEAGUES CARD")
    await context.send(content=None, embed=embed)
#    await context.send(
#      f"Bronze:   Top 3(of 15) promote\n"
#      f"Silver:   Top 3(of 15) promote\n"
#      f"Gold:     Top 3(of 20) promote\n"
#      f"Platinum: Top 3(of 25) promote\n"
#      f"Diamond:  Top 5(of 30) promote\n"
#      f"Master:   Top 5(of 30) promote\n"
#      f"Legend:   Top 3(of 50) earn GM"
#    )

  @leagues.command(
    name="reward",
    brief="Shows tournament rewards",
    aliases=["rewards"],
    help='Shows tournament rewards of a league.\nSpecial thanks to NFdragon#7195 for collecting the data.',
  )
  async def league_reward(self, context, league=None):
    if league is None:
      await context.send_help("leagues reward")
      return
    guild = context.guild
    gem_emoji = self.bot.get_emoji(guild, "gem")
    if gem_emoji is None:
      gem_emoji = "__Gems__"
    elixir_emoji = self.bot.get_emoji(guild, "elixir")
    if elixir_emoji is None:
      elixir_emoji = "__Elixirs__"
    medal_emoji = self.bot.get_emoji(guild, "medal")
    if medal_emoji is None:
      medal_emoji = "__Medals__"
    if league.lower() in ["bronze"]:
      league = "Bronze League"
      description = "Top 3 of 15 get promoted."
      rewards = {"1st place":f"140 {gem_emoji}, 700 {elixir_emoji}, 20 {medal_emoji}",
        "2nd place":f"120 {gem_emoji}, 500 {elixir_emoji}, 10 {medal_emoji}",
        "3rd place":f"100 {gem_emoji}, 300 {elixir_emoji}, 5 {medal_emoji}",
        "4th through 6th place":f"20 {gem_emoji}, 300 {elixir_emoji}, 3 {medal_emoji}",
        "7th through 10th place":f"10 {gem_emoji}, 100 {elixir_emoji}, 1 {medal_emoji}"}
      icon = self.bot.get_emoji(guild, "bronze")
    elif league.lower() in ["silver"]:
      league = "Silver League"
      description = "Top 3 of 15 get promoted."
      rewards = {"1st place":f"140 {gem_emoji}, 700 {elixir_emoji}, 30 {medal_emoji}",
        "2nd place":f"120 {gem_emoji}, 500 {elixir_emoji}, 20 {medal_emoji}",
        "3rd place":f"100 {gem_emoji}, 300 {elixir_emoji}, 10 {medal_emoji}",
        "4th through 6th place":f"20 {gem_emoji}, 300 {elixir_emoji}, 5 {medal_emoji}",
        "7th through 10th place":f"15 {gem_emoji}, 100 {elixir_emoji}, 3 {medal_emoji}"}
      icon = self.bot.get_emoji(guild, "silver")
    elif league.lower() in ["gold"]:
      league = "Gold League"
      description = "Top 3 of 20 get promoted."
      rewards = {"1st place":f"190 {gem_emoji}, 1400 {elixir_emoji}, 40 {medal_emoji}",
        "2nd place":f"170 {gem_emoji}, 1200 {elixir_emoji}, 30 {medal_emoji}",
        "3rd place":f"150 {gem_emoji}, 1000 {elixir_emoji}, 20 {medal_emoji}",
        "4th through 6th place":f"30 {gem_emoji}, 1000 {elixir_emoji}, 10 {medal_emoji}",
        "7th through 10th place":f"20 {gem_emoji}, 500 {elixir_emoji}, 5 {medal_emoji}"}
      icon = self.bot.get_emoji(guild, "gold")
    elif league.lower() in ["platinum","plat"]:
      league = "Platinum League"
      description = "Top 3 of 25 get promoted."
      rewards = {"1st place":f"300 {gem_emoji}, 1600 {elixir_emoji}, 50 {medal_emoji}",
        "2nd place":f"250 {gem_emoji}, 1200 {elixir_emoji}, 40 {medal_emoji}",
        "3rd place":f"200 {gem_emoji}, 1000 {elixir_emoji}, 30 {medal_emoji}",
        "4th through 6th place":f"30 {gem_emoji}, 1000 {elixir_emoji}, 15 {medal_emoji}",
        "7th through 10th place":f"20 {gem_emoji}, 800 {elixir_emoji}, 10 {medal_emoji}"}
      icon = self.bot.get_emoji(guild, "platinum")
    elif league.lower() in ["diamond", "dia"]:
      league = "Diamond League"
      description = "Top 5 of 30 get promoted."
      rewards = {"1st place":f"300 {gem_emoji}, 3000 {elixir_emoji}, 75 {medal_emoji}",
        "2nd and 3rd place":f"250 {gem_emoji}, 2400 {elixir_emoji}, 60 {medal_emoji}",
        "4th and 5th place":f"200 {gem_emoji}, 2000 {elixir_emoji}, 50 {medal_emoji}",
        "6th through 10th place":f"40 {gem_emoji}, 1800 {elixir_emoji}, 25 {medal_emoji}",
        "11th through 15th place":f"25 {gem_emoji}, 1200 {elixir_emoji}, 15 {medal_emoji}"}
      icon = self.bot.get_emoji(guild, "diamond")
    elif league.lower() in ["master"]:
      league = "Master League"
      description = "Top 5 of 30 get promoted."
      rewards = {"1st place":f"300 {gem_emoji}, 5000 {elixir_emoji}, 100 {medal_emoji}",
        "2nd and 3rd place":f"250 {gem_emoji}, 3600 {elixir_emoji}, 90 {medal_emoji}",
        "4th and 5th place":f"200 {gem_emoji}, 3000 {elixir_emoji}, 80 {medal_emoji}",
        "6th through 10th place":f"40 {gem_emoji}, 1800 {elixir_emoji}, 40 {medal_emoji}",
        "11th through 15th place":f"25 {gem_emoji}, 1500 {elixir_emoji}, 20 {medal_emoji}"}
      icon = self.bot.get_emoji(guild, "master")
    elif league.lower() in ["legend", "legendary", "grandmaster", 'gm']:
      league = "Legendary League"
      gm_emoji = self.bot.get_emoji(guild, "gm")
      if gm_emoji is not None:
        description = f"Top 3 of 50 get Grandmaster title {gm_emoji}."
      else:
        description = f"Top 3 of 50 get Grandmaster title."
      rewards = {"1st place":f"500 {gem_emoji}, 12000 {elixir_emoji}, 500 {medal_emoji}",
        "2nd place":f"400 {gem_emoji}, 6000 {elixir_emoji}, 400 {medal_emoji}",
        "3rd place":f"300 {gem_emoji}, 4500 {elixir_emoji}, 300 {medal_emoji}",
        "4th through 6th place":f"50 {gem_emoji}, 4000 {elixir_emoji}, 80 {medal_emoji}",
        "7th through 10th place":f"30 {gem_emoji}, 3000 {elixir_emoji}, 40 {medal_emoji}",
        "11th through 25th place":f"25 {gem_emoji}, 1800 {elixir_emoji}, 20 {medal_emoji}"}
      icon = self.bot.get_emoji(guild, "legendary")
    else:
      await context.send(f"There is no league called {league}.")
      return
    embed = discord.Embed(title=league, description=description)
    for position, reward in rewards.items():
      embed.add_field(name=f"{position}:", value=f"{reward}", inline=False)
    embed.set_footer(text="LEAGUE REWARDS", icon_url=icon.url if icon else discord.Embed.Empty)
    await context.send(content=None, embed=embed)
    
  @commands.group(
    name="rand",
    brief="Shows some random things",
    aliases=["random"],
    case_insensitive = True,
    invoke_without_command=True
  )
  async def _rand(self, context):
    await context.send_help("rand")
    
  @_rand.command(
    name="fact",
    brief="Gets a random fact",
  )
  @commands.cooldown(1, 30, commands.BucketType.user)
  async def randfact(self, context):
    await context.send(
      f"{random.choice(facts)}"
    )

  @_rand.command(
    brief="Gets a random quote",
  )
  @commands.cooldown(1, 15, commands.BucketType.user)
  async def quote(self, context):
    result = self.bot.db[context.guild.id].query(f"SELECT * FROM quotes ORDER BY random() LIMIT 1")
    quote = result[0][2]
    hero = result[0][1]
    await context.send(
      f'"{quote}"\n\n'
      f'                  -*{hero}*'
    )
    
def setup(bot):
  bot.add_cog(InfoCog(bot))
  logging.info("Added information cog.")
