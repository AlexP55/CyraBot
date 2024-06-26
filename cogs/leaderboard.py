import discord
from discord.ext import commands
from modules.cyra_converter import hero_emoji_converter, find_hero, TournamentTimeConverter, deEmojify
from modules.cyra_serializable import LeaderboardEntry
from base.modules.basic_converter import UnicodeEmoji
from base.modules.access_checks import has_mod_role, mod_role_check
from base.modules.constants import CACHE_PATH as path, num_emojis, arrow_emojis, letter_emojis, empty_space
from base.modules.serializable_object import dump_json
from base.modules.interactive_message import InteractiveMessage
from datetime import datetime, timedelta
import enum
import json
import typing
import logging
import os

logger = logging.getLogger(__name__)


async def fetch_msg(guild, channelid, messageid):
  channel = guild.get_channel(channelid)
  try:
    return await channel.fetch_message(messageid)
  except:
    return None
    
def size_limit_join(lines, size_limit, separator="\n"):
  if len(lines[0]) > size_limit:
    return ""
  output = lines.pop(0)
  while lines:
    new_line = lines.pop(0)
    if len(output) + len(new_line) + len(separator) > size_limit:
      lines.insert(0, new_line)
      break
    else:
      output = f"{output}{separator}{new_line}"
  return output

class LeaderboardCog(commands.Cog, name="Leaderboard Commands"):
  embed_description_limit = 2048
  embed_field_limit = 1024
  embed_total_limit = 6000
  name_limit = 20

  def __init__(self, bot):
    self.bot = bot
    if not os.path.isdir(path):
      os.mkdir(path)
    self.params = LeaderboardEntry.from_json(f"{path}/leaderboard.json")
    if not self.params:
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
    dump_json(self.params, f'{path}/leaderboard.json')

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
    week = self.week if week is None else week
    self.bot.db[context.guild.id].insert_or_update("blessed_hero", self.season, week, hero)
    await context.send(f"Season {self.season} week {week} blessed hero {hero} updated successfully!")
    
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
    
  def get_season_leaderboard(self, guild, season=0, instruction=None):
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
                           f"ORDER BY gm_num DESC, season DESC, week DESC, kill DESC NULLS LAST, time ASC NULLS LAST")
    # return the seasonly leaderboard embed
    table = [[" ", "⬛", "Game ID", "⬛⬛⬛", "GMs", "Member"]]
    rank = 0
    for playerid, gameid, flag, hero1, hero2, hero3, gm_num in result:
      rank += 1
      #r_emoji = self.get_rank_emoji(guild, rank)
      member = guild.get_member(playerid)
      name = deEmojify(gameid if gameid else (member.display_name if member else "???"))
      if flag is None:
        flag = "🏁"
      heroes = "".join([hero if hero is not None else "⬛" for hero in [hero1, hero2, hero3]])
      mention = str(member) if member is not None else ""
      table.append([str(rank) if rank < 100 else "", flag, name[:self.name_limit], heroes, str(gm_num), mention])
    rank_maxlen = max([len(table[i][0]) for i in range(len(table))])
    name_maxlen = max([len(table[i][2]) for i in range(len(table))])
    gm_num_maxlen = max([len(table[i][4]) for i in range(len(table))])
    #mention_maxlen = max([len(table[i][5]) for i in range(len(table))])
    lines = [f"`{rank:<{rank_maxlen}}` {flag} `{name:<{name_maxlen}}` {heroes} ` {gm_num:<{gm_num_maxlen}}` ` {mention} `"
             for rank, flag, name, heroes, gm_num, mention in table]
    lines.insert(1, "")
    
    gm_emoji = self.bot.get_emoji(guild, "medal")
    descript_emoji = gm_emoji if gm_emoji else '🏆'
    header = f"GM @ Season {season}" if season is not None else f"GM Since 2-21-2021"
    header = f"{descript_emoji} **{header}** {descript_emoji}\n"
    
    lines.insert(0, header)
    
    # join the lines to get the description
    description = size_limit_join(lines, self.embed_description_limit)
    
    embed = discord.Embed(title=f"Discord GM Seasonal Leaderboard" if season is not None else f"Discord GM Leaderboard",
                          colour=discord.Colour.gold(), timestamp=datetime.utcnow(), description=description)
    footer_emoji = self.bot.get_emoji(guild, "gm")
    embed.set_footer(text="Seasonal GM" if season is not None else "GM Summary", icon_url=footer_emoji.url if footer_emoji else discord.Embed.Empty)
    if instruction:
      embed.add_field(name="For Other Info:", value=instruction, inline=False)
    
    self.add_embed_fields(embed, lines)
    return embed
    
  def get_week_leaderboard(self, guild, season=0, week=0, instruction=None):
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
    table = [[" ", "⬛", "Game ID", "⬛⬛⬛", "Kill", "Time", "Member"]]
    rank = 0
    for playerid, gameid, flag, hero1, hero2, hero3, kill, time, group_rank, gm_rank in result:
      rank += 1
      #r_emoji = self.get_rank_emoji(guild, rank)
      member = guild.get_member(playerid)
      name = deEmojify(gameid if gameid else (member.display_name if member else "???"))
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
      table.append([str(rank) if rank < 100 else "", flag, name[:self.name_limit], heroes, kill, time, mention])
    rank_maxlen = max([len(table[i][0]) for i in range(len(table))])
    name_maxlen = max([len(table[i][2]) for i in range(len(table))])
    kill_maxlen = max([len(table[i][4]) for i in range(len(table))])
    time_maxlen = max([len(table[i][5]) for i in range(len(table))])
    #mention_maxlen = max([len(table[i][6]) for i in range(len(table))])
    lines = [f"`{rank:<{rank_maxlen}}` {flag} `{name:<{name_maxlen}}` {heroes} ` {kill:<{kill_maxlen}}` ` {time:<{time_maxlen}}` ` {mention} `"
             for rank, flag, name, heroes, kill, time, mention in table]
    lines.insert(1, "")
    descript_emoji = self.bot.get_emoji(guild, "medal")
    descript_emoji = descript_emoji if descript_emoji else '🏆'
    header = f"{descript_emoji} **GM @ Season {season} Week {week}** {descript_emoji}\n"
    if blessed is not None:
      header = f"{header}Blessed hero: {blessed}\n"
    
    lines.insert(0, header)
    
    # join the lines to get the description
    description = size_limit_join(lines, self.embed_description_limit)

    embed = discord.Embed(title=f"Discord GM Weekly Leaderboard", colour=discord.Colour.gold(), 
                          timestamp=datetime.utcnow(), description=description)
    footer_emoji = self.bot.get_emoji(guild, "gm")
    embed.set_footer(text="Weekly GM", icon_url=footer_emoji.url if footer_emoji else discord.Embed.Empty)
    if instruction:
      embed.add_field(name="For Other Info:", value=instruction, inline=False)
    
    self.add_embed_fields(embed, lines)
    return embed
    
  def add_embed_fields(self, embed, lines):
    # add the fields to an embed
    save_size = 0 # the size to be saved to avoid exceeding size limit
    ind = 0
    if len(embed) + sum([len(line) for line in lines]) + 10 > self.embed_total_limit:
      # contents cannot be all fit in, need to save size for a field
      save_size += len(f"{len(lines)} player(s) not displayed in the table.") + len(empty_space)
    while lines:
      # compute the size of the current field
      remaining_size = self.embed_total_limit - len(embed) - len(empty_space) - save_size
      field_limit = min(self.embed_field_limit, remaining_size)
      new_field = size_limit_join(lines, field_limit)
      if new_field:
        embed.insert_field_at(ind, name=empty_space, value=new_field, inline=False)
        ind += 1
      if remaining_size <= self.embed_field_limit or not new_field:
        # no more size to add a new field
        break
    if lines:
      embed.insert_field_at(ind, name=empty_space, value=f"{len(lines)} player(s) not displayed in the table.", inline=False)
    
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
    instruction = f"{letter_emojis['A']} All  {letter_emojis['S']} Seasonly  {letter_emojis['W']} Weekly"
    if len(self.season_week_comb) > 1 and self.info_type != InteractiveLeaderboard.InfoType.all:
      instruction = f"{instruction}\n{arrow_emojis['backward']}{arrow_emojis['forward']} Change Season/Week"
    if self.info_type == InteractiveLeaderboard.InfoType.all:
      embed = self.cog.get_season_leaderboard(self.context.guild, None, instruction)
    elif self.info_type == InteractiveLeaderboard.InfoType.season:
      embed = self.cog.get_season_leaderboard(self.context.guild, self.season, instruction)
    elif self.info_type == InteractiveLeaderboard.InfoType.week:
      embed = self.cog.get_week_leaderboard(self.context.guild, self.season, self.week, instruction)
    return embed
    
def setup(bot):
  bot.add_cog(LeaderboardCog(bot))
  logging.info("Added Leaderboard cog.")
