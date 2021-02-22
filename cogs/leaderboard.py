import discord
from discord.ext import commands
from modules.cyra_converter import hero_emoji_converter, find_hero, TournamentTimeConverter
from base.modules.basic_converter import UnicodeEmoji
from base.modules.access_checks import has_mod_role, mod_role_check
from base.modules.constants import CACHE_PATH as path, num_emojis, arrow_emojis, letter_emojis, empty_space
from base.modules.interactive_message import InteractiveMessage
from datetime import datetime, timedelta
import enum
import json
import typing
import logging

logger = logging.getLogger(__name__)


async def fetch_msg(guild, channelid, messageid):
  channel = guild.get_channel(channelid)
  try:
    return await channel.fetch_message(messageid)
  except:
    return None
    
def size_limit_grouping(lines, size_limits, separator="\n"):
  ind = -1
  output = [""] * len(size_limits)
  while lines:
    new_line = lines.pop(0)
    if ind < 0 or len(output[ind]) + len(new_line) + len(separator) > size_limits[ind]:
      ind += 1
      if ind >= len(size_limits):
        lines.insert(1, new_line)
        break
      output[ind] = new_line
      assert len(output[ind]) <= size_limits[ind]
    else:
      output[ind] = f"{output[ind]}{separator}{new_line}"
  return output

class LeaderboardCog(commands.Cog, name="Leaderboard Commands"):
  embed_size_group = [2048, 1024, 1024, 1024]

  def __init__(self, bot):
    self.bot = bot
    self.params = {}
    try:
      with open(f"{path}/leaderboard.json") as f:
        data = json.load(f)
        self.season = data["season"]
        self.week = data["week"]
        self.messages = {}
        for guildid, messages in data["messages"].items():
          if not messages:
            continue
          self.messages[int(guildid)] ={
            "all": {"channel": messages["all"]["channel"], "message":messages["all"]["message"]},
            "season": {"channel": messages["season"]["channel"], "message":messages["season"]["message"]},
            "week": {"channel": messages["week"]["channel"], "message":messages["week"]["message"]},
          }
    except:
      self.season = 1
      self.week = 1
      self.messages = {}
    for guild in self.bot.guilds:
      self.init_guild(guild)
      
  def init_guild(self, guild):
    if guild.id not in self.messages:
      self.messages[guild.id] = {}
      
  def get_distict_season_week(self, guild):
    return self.bot.db[guild.id].query("SELECT DISTINCT season, week FROM leaderboard ORDER BY season, week")
    
  @property
  def season(self):
    return self.params["season"]
    
  @season.setter
  def season(self, value):
    self.params["season"] = value
    
  @property
  def week(self):
    return self.params["week"]
    
  @week.setter
  def week(self, value):
    self.params["week"] = value
    
  @property
  def messages(self):
    return self.params["messages"]
    
  @messages.setter
  def messages(self, value):
    self.params["messages"] = value
    
  def cog_unload(self):
    try:
      with open(f'{path}/leaderboard.json', 'w') as f:
        json.dump(self.params, f)
    except:
      pass

  #Default error handler for this cog, can be overwritten with a local error handler.
  async def cog_command_error(self, context, error):
    await self.bot.respond_to_error(context, error)

  @commands.group(
    name="ldb",
    brief="Shows leaderboard",
    case_insensitive = True,
    invoke_without_command=True,
    help="Shows an interactive leaderboard of GMs of discord.",
    aliases=["leaderboard"]
  )
  async def _ldb(self, context):
    timeout = self.bot.get_setting(context.guild, "ACTIVE_TIME") * 60
    guild = InteractiveLeaderboard(self, context=context, timeout=timeout)
    await guild.start()
    
  @_ldb.command(
    name="info",
    brief="Shows current season and week",
    help="Shows current season and week.",
  )
  @has_mod_role()
  async def _ldb_info(self, context):
    await context.send(f"Current season: {self.season}\nCurrent week: {self.week}")
    
  @_ldb.command(
    name="submit",
    brief="Submits a GM run",
    help="Submits a GM run, the info will be updated on dynamic leaderboard.",
  )
  @has_mod_role()
  async def _ldb_submit(self, context, player:discord.Member, heroes:commands.Greedy[hero_emoji_converter],
                        kill:int=None, time:TournamentTimeConverter=None, group_rank:int=None, gm_rank:int=None):
    heroes = [str(hero) for hero in heroes]
    if len(heroes) < 3:
      heroes += [None] * (3-len(heroes))
    else:
      heroes = heroes[0:3]
    self.bot.db[context.guild.id].insert_or_update("leaderboard", player.id, self.season, self.week, *heroes, 
                                                   kill, time.total_seconds() if time else None, group_rank, gm_rank)
    await context.send(f"GM score of {player} submitted successfully!")
    await self.update_dynamic_leaderboard(context)
    
  @_ldb.command(
    name="delete",
    brief="Deletes a GM run",
    help="Deletes a GM run, the info will be updated on dynamic leaderboard.",
    aliases=["del"]
  )
  @has_mod_role()
  async def _ldb_delete(self, context, player:discord.Member):
    self.bot.db[context.guild.id].delete_row("leaderboard", [player.id, self.season, self.week])
    await context.send(f"GM score of {player} deleted successfully!")
    await self.update_dynamic_leaderboard(context)
    
  @_ldb.command(
    name="register",
    brief="Registers player info",
    help="Registers player info to be displayed on leaderboard.",
  )
  async def _ldb_register(self, context, gameid, player:typing.Optional[discord.Member], flag:typing.Optional[UnicodeEmoji]):
    if player is None or not mod_role_check(context):
      player = context.author
    self.bot.db[context.guild.id].insert_or_update("player_info", player.id, gameid, flag)
    await context.send(f"Player info of {player} registered successfully!")
    
  @_ldb.command(
    name="blessed",
    brief="Updates blessed hero",
    help="Updates the blessed hero for the current or another week.",
    aliases=["bless"],
  )
  @has_mod_role()
  async def _ldb_blessed(self, context, hero:find_hero, week:int=None):
    if week is not None and week <= 0:
      await context.send("Week number must be a positive integer!")
      return
    self.bot.db[context.guild.id].insert_or_update("blessed_hero", self.season, self.week if week is None else week, hero)
    await context.send(f"Season {self.season} week {self.week} blessed hero {hero.title()} updated successfully!")
    
  @_ldb.command(
    name="season",
    brief="Sets a new season",
    help="Sets a new tournament season.",
  )
  @has_mod_role()
  async def _ldb_season(self, context, season:int=None):
    if season is not None and season <= 0:
      await context.send("Season number must be a positive integer!")
      return
    self.season = self.season + 1 if season is None else season
    self.week = 1
    await context.send(f"Tournament season is set to {self.season}!")
    
  @_ldb.command(
    name="week",
    brief="Sets a new week",
    help="Sets a new tournament week.",
  )
  @has_mod_role()
  async def _ldb_week(self, context, week:int=None):
    if week is not None and week <= 0:
      await context.send("Week number must be a positive integer!")
      return
    self.week = self.week + 1 if week is None else week
    await context.send(f"Tournament week is set to {self.week}!")
    
  @_ldb.command(
    name="post",
    brief="Posts dynamic leaderboard",
    help="Posts the current dynamic leaderboard.",
  )
  @has_mod_role()
  async def _ldb_post(self, context, channel:discord.TextChannel=None):
    if channel is not None:
      await self.update_dynamic_leaderboard(channel)
    else:
      await self.update_dynamic_leaderboard(context)
    await context.send("Dynamic leaderboard updated successfully!")
    
  async def update_dynamic_leaderboard(self, context):
    guild = context.guild
    all_message, season_message, week_message = await self.look_for_msg(guild)
    all_embed = self.get_season_leaderboard(guild, None)
    season_embed = self.get_season_leaderboard(guild)
    week_embed = self.get_week_leaderboard(guild)
    if all_message is None:
      all_message = await context.send(embed=all_embed)
      self.messages[guild.id]["all"] = {
        "channel":all_message.channel.id, "message":all_message.id
      }
    else:
      await all_message.edit(embed=all_embed)
    if season_message is None:
      season_message = await context.send(embed=season_embed)
      self.messages[guild.id]["season"] = {
        "channel":season_message.channel.id, "message":season_message.id
      }
    else:
      await season_message.edit(embed=season_embed)
    if week_message is None:
      week_message = await context.send(embed=week_embed)
      self.messages[guild.id]["week"] = {
        "channel":week_message.channel.id, "message":week_message.id
      }
    else:
      await week_message.edit(embed=week_embed)
    
  async def look_for_msg(self, guild):
    if "all" in self.messages[guild.id]:
      all_info = self.messages[guild.id]["all"]
      all_message = await fetch_msg(guild, all_info["channel"], all_info["message"])
    else:
      all_message = None
    if "season" in self.messages[guild.id]:
      season_info = self.messages[guild.id]["season"]
      season_message = await fetch_msg(guild, season_info["channel"], season_info["message"])
    else:
      season_message = None
    if "week" in self.messages[guild.id]:
      week_info = self.messages[guild.id]["week"]
      week_message = await fetch_msg(guild, week_info["channel"], week_info["message"])
    else:
      week_message = None
    return all_message, season_message, week_message
    
  def get_season_leaderboard(self, guild, season=0):
    if season is not None:
      if season <= 0:
        season = self.season
      where_clause = f"season={season}"
    else:
      where_clause = "TRUE"
    # db query
    leaderboard_query = (f"SELECT playerid, season, week, kill, time, MAX(season*100+week), hero1, hero2, hero3, COUNT(playerid) AS gm_num "
                         f"FROM leaderboard WHERE {where_clause} GROUP BY playerid")
    result = self.bot.db[guild.id].query(f"SELECT ldb.playerid, gameid, flag, hero1, hero2, hero3, gm_num "
                           f"FROM ({leaderboard_query}) AS ldb LEFT JOIN player_info on ldb.playerid=player_info.playerid "
                           f"ORDER BY gm_num DESC, season ASC, week ASC, kill DESC NULLS LAST, time ASC NULLS LAST")
    # return the seasonly leaderboard embed
    table = [["⬛", "⬛", "Game ID", "⬛⬛⬛", "GMs", "Member"]]
    rank = 0
    for playerid, gameid, flag, hero1, hero2, hero3, gm_num in result:
      rank += 1
      r_emoji = self.get_rank_emoji(guild, rank)
      member = guild.get_member(playerid)
      name = gameid if gameid else (member.display_name if member else "???")
      if flag is None:
        flag = "🏁"
      heroes = "".join([hero if hero is not None else "⬛" for hero in [hero1, hero2, hero3]])
      mention = str(member) if member is not None else ""
      table.append([r_emoji, flag, name, heroes, str(gm_num), mention])
    name_maxlen = max([len(table[i][2]) for i in range(len(table))])
    gm_num_maxlen = max([len(table[i][4]) for i in range(len(table))])
    #mention_maxlen = max([len(table[i][5]) for i in range(len(table))])
    lines = [f"{r_emoji} {flag} `{name:<{name_maxlen}}` {heroes} ` {gm_num:<{gm_num_maxlen}}` ` {mention}`"
             for r_emoji, flag, name, heroes, gm_num, mention in table]
    lines.insert(1, "")
    
    gm_emoji = self.bot.get_emoji(guild, "gm")
    descript_emoji = gm_emoji if gm_emoji else '🏆'
    header = f"GM @ Season {season}" if season is not None else f"GM Since 2-21-2021"
    header = f"{descript_emoji} **{header}** {descript_emoji}\n"
    
    lines.insert(0, header)
    
    # grouping the lines by size limit
    group = size_limit_grouping(lines, self.embed_size_group)
    description = group[0]
    
    embed = discord.Embed(title=f"Discord GM Seasonal Leaderboard" if season is not None else f"Discord GM Leaderboard",
                          colour=discord.Colour.gold(), timestamp=datetime.utcnow(), description=description)
    for i in range(1, len(group)):
      if group[i]:
        embed.add_field(name=empty_space, value=group[i], inline=False)
    if lines: # there are remainding lines now showing
      embed.add_field(name=empty_space, value=f"{len(lines)} user(s) not showing up in the table.", inline=False)
    
    footer_emoji = self.bot.get_emoji(guild, "meteor")
    embed.set_footer(text="Seasonal GM" if season is not None else "GM Summary", icon_url=footer_emoji.url if footer_emoji else discord.Embed.Empty)
    return embed
    
  def get_week_leaderboard(self, guild, season=0, week=0):
    if season <= 0:
      season = self.season
    if week <= 0:
      week = self.week
    # db query
    blessed = self.bot.db[guild.id].select("blessed_hero", [season, week])
    blessed = self.bot.get_emoji(guild, blessed["hero"]) if blessed else None
    leaderboard_query = (f"SELECT playerid, hero1, hero2, hero3, kill, time, group_rank, gm_rank "
                         f"FROM leaderboard WHERE season={season} AND week={week}")
    result = self.bot.db[guild.id].query(f"SELECT ldb.playerid, gameid, flag, hero1, hero2, hero3, kill, time, group_rank, gm_rank "
                           f"FROM ({leaderboard_query}) AS ldb LEFT JOIN player_info on ldb.playerid=player_info.playerid "
                           f"ORDER BY kill DESC NULLS LAST, time ASC NULLS LAST")
    # return the weekly leaderboard embed
    table = [["⬛", "⬛", "Game ID", "⬛⬛⬛", "Kill", "Time", "Member"]]
    rank = 0
    for playerid, gameid, flag, hero1, hero2, hero3, kill, time, group_rank, gm_rank in result:
      rank += 1
      r_emoji = self.get_rank_emoji(guild, rank)
      member = guild.get_member(playerid)
      name = gameid if gameid else (member.display_name if member else "???")
      if flag is None:
        flag = "🏁"
      heroes = "".join([hero if hero is not None else "⬛" for hero in [hero1, hero2, hero3]])
      mention = str(member) if member is not None else ""
      if time is None:
        time = "???"
      else:
        minutes, seconds = divmod(time, 60)
        time = f"{minutes:02.0f}:{seconds:06.3f}"
      kill = "???" if kill is None else str(kill)
      table.append([r_emoji, flag, name, heroes, kill, time, mention])
    name_maxlen = max([len(table[i][2]) for i in range(len(table))])
    kill_maxlen = max([len(table[i][4]) for i in range(len(table))])
    time_maxlen = max([len(table[i][5]) for i in range(len(table))])
    #mention_maxlen = max([len(table[i][6]) for i in range(len(table))])
    lines = [f"{r_emoji} {flag} `{name:<{name_maxlen}}` {heroes} ` {kill:<{kill_maxlen}}` ` {time:<{time_maxlen}}` ` {mention}`"
             for r_emoji, flag, name, heroes, kill, time, mention in table]
    lines.insert(1, "")
    gm_emoji = self.bot.get_emoji(guild, "gm")
    descript_emoji = gm_emoji if gm_emoji else '🏆'
    header = f"{descript_emoji} **GM @ Season {season} Week {week}** {descript_emoji}\n"
    if blessed is not None:
      header = f"{header}Blessed hero: {blessed}\n"
    
    lines.insert(0, header)
    
    # grouping the lines by size limit
    group = size_limit_grouping(lines, self.embed_size_group)
    description = group[0]
    embed = discord.Embed(title=f"Discord GM Weekly Leaderboard", colour=discord.Colour.gold(), 
                          timestamp=datetime.utcnow(), description=description)
    for i in range(1, len(group)):
      if group[i]:
        embed.add_field(name=empty_space, value=group[i], inline=False)
    if lines: # there are remainding lines now showing
      embed.add_field(name=empty_space, value=f"{len(lines)} user(s) not showing up in the table.", inline=False)
      
    footer_emoji = self.bot.get_emoji(guild, "meteor")
    embed.set_footer(text="Weekly GM", icon_url=footer_emoji.url if footer_emoji else discord.Embed.Empty)
    return embed
    
  def get_rank_emoji(self, guild, rank):
    if rank <= 1:
      r_emoji = self.bot.get_emoji(guild, "gm")
    elif rank == 2:
      r_emoji = self.bot.get_emoji(guild, "legendary")
    elif rank == 3:
      r_emoji = self.bot.get_emoji(guild, "master")
    elif rank <= 5:
      r_emoji = self.bot.get_emoji(guild, "diamond")
    elif rank <= 7:
      r_emoji = self.bot.get_emoji(guild, "gold")
    elif rank <= 10:
      r_emoji = self.bot.get_emoji(guild, "silver")
    else:
      r_emoji = self.bot.get_emoji(guild, "bronze")
    if r_emoji is None:
      if rank < len(num_emojis):
        r_emoji = num_emojis[rank]
      else:
        r_emoji = "🟦"
    return r_emoji
    
class InteractiveLeaderboard(InteractiveMessage):

  class InfoType(enum.Enum):
    all = 0
    season = 1
    week = 2
    
  def __init__(self, leaderboard_cog, parent=None, **attributes):
    super().__init__(parent, **attributes)
    self.cog = leaderboard_cog
    self.info_type = InteractiveLeaderboard.InfoType.all
    self.child_emojis = [letter_emojis["A"], letter_emojis["S"], letter_emojis["W"]]
    self.season_week_comb = self.cog.get_distict_season_week(self.context.guild)
    if self.season_week_comb:
      self.index = len(self.season_week_comb) - 1
      if len(self.season_week_comb) > 1:
        self.child_emojis += [arrow_emojis["backward"], arrow_emojis["forward"]]
    else:
      self.index = None
        
  @property
  def season(self):
    if self.index is not None:
      return self.season_week_comb[self.index][0]
    else:
      return 0
      
  @property
  def week(self):
    if self.index is not None:
      return self.season_week_comb[self.index][1]
    else:
      return 0
      
      
  async def transfer_to_child(self, emoji):
    if emoji == letter_emojis["A"]:
      if self.info_type != InteractiveLeaderboard.InfoType.all:
        self.info_type = InteractiveLeaderboard.InfoType.all
        return self
    elif emoji == letter_emojis["S"]:
      if self.info_type != InteractiveLeaderboard.InfoType.season:
        self.info_type = InteractiveLeaderboard.InfoType.season
        return self
    elif emoji == letter_emojis["W"]:
      if self.info_type != InteractiveLeaderboard.InfoType.week:
        self.info_type = InteractiveLeaderboard.InfoType.week
        return self
    elif self.index is not None and self.info_type != InteractiveLeaderboard.InfoType.all:
      ind = self.index
      season, week = self.season_week_comb[ind]
      if emoji == arrow_emojis["backward"]:
        ind -= 1
        if self.info_type == InteractiveLeaderboard.InfoType.season:
          while ind >= 0:
            if self.season_week_comb[ind][0] < season:
              break
            ind -= 1
      elif emoji == arrow_emojis["forward"]:
        ind += 1
        if self.info_type == InteractiveLeaderboard.InfoType.season:
          while ind < len(self.season_week_comb):
            if self.season_week_comb[ind][0] > season:
              break
            ind += 1
      if 0 <= ind < len(self.season_week_comb):
        self.index = ind
        return self
    return None
    
  async def get_embed(self):
    if self.info_type == InteractiveLeaderboard.InfoType.all:
      embed = self.cog.get_season_leaderboard(self.context.guild, None)
    elif self.info_type == InteractiveLeaderboard.InfoType.season:
      embed = self.cog.get_season_leaderboard(self.context.guild, self.season)
    elif self.info_type == InteractiveLeaderboard.InfoType.week:
      embed = self.cog.get_week_leaderboard(self.context.guild, self.season, self.week)
    instruction = f"{letter_emojis['A']} All  {letter_emojis['S']} Seasonly  {letter_emojis['W']} Weekly"
    if len(self.season_week_comb) > 1 and self.info_type != InteractiveLeaderboard.InfoType.all:
      instruction = f"{instruction}\n{arrow_emojis['backward']}{arrow_emojis['forward']} Change Season/Week"
    embed.add_field(name="For Other Info:", value=instruction, inline=False)
    return embed
    
def setup(bot):
  bot.add_cog(LeaderboardCog(bot))
  logging.info("Added Leaderboard cog.")
