import random
import discord
from discord.ext import commands
import time
import string
from base.modules.settings_manager import DefaultSetting
import modules.custom_exceptions as custom_exceptions
from base_bot import BaseBot, dynamic_prefix
from modules.cyra_constants import emoji_keys, bot_state, hero_list
import glob

class CyraBot(BaseBot):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def get_emoji(self, guild, key):
    return discord.utils.get(guild.emojis, name=emoji_keys[key])
    
  def get_nick(self, guild):
    nick = guild.me.nick
    if not nick:
      nick = self.user.name
    return nick
    
  def get_state(self, name):
    if isinstance(name, discord.Guild):
      name = self.get_nick(name).lower()
    if name in bot_state:
      return bot_state[name]
    return bot_state["_default"]
  
  def is_willing_to_answer(self, context):
    if self.get_nick(context.guild).lower() == "elara":
      #If the nick is Elara, there is a chance she will refuse to answer.
      if context.command.qualified_name == "help":
        return True
      if context.author.id in self.owner_ids:
        return False #Bot owners are immune to Elaras chaos
      chance = self.get_setting(context.guild, "ELARA_REFUSE_CHANCE")/100.0
      if random.random() < chance:
        responses = [
          "I do not need to answer you!", "I'm busy sowing the seeds of chaos. Don't disturb me.", 
          "Get lost.", "Haha, I pulled your command into darkness, more chaos is coming!",
          "Succumb to entropy, puny mortal.", "I received your command and chose to ignore it.",
          "Stop telling me what to do, you're not my mom.",
          "Aww, did your command get lost in all the chaos?", "How... amusing",
          "Did you honestly believe you'd get the results you were looking for? How naive.",
          "How about you do the work once in a while?",
          "Command invalid. Just kidding. I'm not in the mood for work.",
          f"Input:{context.message.content}\nOutput: Chaos."
        ]
        raise custom_exceptions.ElaraRefuseToAnswer(random.choice(responses))
      else:
        return True
    else:
      return True
      
  async def respond_to_error(self, context, error):
    # general error handler, used in hero/infomation cog
    if hasattr(context.command, "on_error"):
      # This prevents any commands with local handlers being handled here.
      return
    if isinstance(error, custom_exceptions.ElaraRefuseToAnswer):
      msg = f"{error}\n||*Elara destroyed your command, maybe you should try one more time?*||"
    else:
      state = self.get_state(context.guild)
      if isinstance(error, commands.CommandOnCooldown):
        msg = state["cooldown_msg"]
      elif isinstance(error, custom_exceptions.HeroNotFound):
        msg = state["nohero_msg"]
      elif isinstance(error, custom_exceptions.AbilityNotFound):
        if error.hero.lower() == self.get_nick(context.guild).lower():
          msg = state["noability_msg_self"]
        else:
          msg = state["noability_msg_other"]
      elif isinstance(error, custom_exceptions.DataNotFound):
        msg = state["nodata_msg"]
      elif isinstance(error, commands.UserInputError):
        msg = state["badinput_msg"]
      elif isinstance(error, commands.CheckFailure):
        msg = state["noaccess_msg"]
      else:
        msg = state["unexpected_msg"]
    #Send response
    await context.send(msg.format(context=context, error=error))

  async def transform(self, guild: discord.Guild, name, change_avatar=True, skin:int=None):
    if change_avatar:
      # get all possible avatars
      avatar_files = glob.glob(f"avatar/{name.title()}*.png")
      if avatar_files: # chooce a random skin
        avatar_file = None
        if skin is not None:
          expect_file = f"avatar/{name.title()}{skin}.png"
          if expect_file in avatar_files: avatar_file = expect_file
        if avatar_file is None: avatar_file = random.choice(avatar_files)
        with open(avatar_file, "rb") as avatar:
          await self.user.edit(avatar=avatar.read())
    state = self.get_state(name)
    nickname = name.title()
    await guild.me.edit(nick=nickname)
    admin_role = self.get_admin_role(guild)
    mod_role = self.get_mod_role(guild)
    bot_role = self.get_bot_role(guild)
    if bot_role is not None:
      bot_role_name = nickname
      await self.set_setting(guild, "BOT_ROLE_NAME", bot_role_name)
      await bot_role.edit(name=bot_role_name, color=state["color"])
    if mod_role is not None:
      mod_role_name = f"{nickname}'s {state['mod_role']}"
      await self.set_setting(guild, "MOD_ROLE_NAME", mod_role_name)
      await mod_role.edit(name=mod_role_name)
    if admin_role is not None:
      admin_role_name = f"{nickname}'s {state['admin_role']}"
      await self.set_setting(guild, "ADMIN_ROLE_NAME", admin_role_name)
      await admin_role.edit(name=admin_role_name)
    
  async def init_bot(self, guild):
    # overrides the method: check nick name, add Cyra-specific variables
    await super().init_bot(guild)
    #if self.get_nick(guild).lower() not in hero_list:
    #  await guild.me.edit(nick="Cyra")

  async def on_command_error(self, context, error):
    if isinstance(error, commands.CommandNotFound):
      state = self.get_state(context.guild)
      await context.send(state["nocommand_msg"].format(context=context, error=error))
    #Log the error.
    await super().on_command_error(context, error)
    
  async def on_guild_join(self, guild):
    await super().on_guild_join(guild)
    
  async def on_ready(self):
    await super().on_ready()
    
  def load_all_cogs(self):
    super().load_all_cogs()
    self.load_cogs("cogs.general_information","cogs.stats_infomation","cogs.data_fetching", "cogs.transform_cyra", "cogs.leaderboard")

  async def on_guild_remove(self, guild):
    await super().on_guild_remove(guild)
  
  def initialize_default_settings(self):
    super().initialize_default_settings()
    bot_name = "Cyra"
    self.default_settings["MOD_ROLE_NAME"].default = f"{bot_name}'s {bot_state[bot_name.lower()]['mod_role']}"
    self.default_settings["ADMIN_ROLE_NAME"].default = f"{bot_name}'s {bot_state[bot_name.lower()]['admin_role']}"
    self.default_settings["BOT_ROLE_NAME"].default = f"{bot_name}"
    self.default_settings["ELARA_REFUSE_CHANCE"] = DefaultSetting(name="ELARA_REFUSE_CHANCE", default=10, description="chance to ignore command", 
      transFun=lambda x: float(x), checkFun=lambda x: x>=0, checkDescription="a non-negative number")
    self.default_settings["SEARCH_LIMIT"] = DefaultSetting(name="SEARCH_LIMIT", default=11, description="max num of entries by a query", 
      transFun=lambda x: int(x), checkFun=lambda x: 0<x<=11, checkDescription="an integer between 1 and 11")
    self.default_settings["LEVEL_EXTRA_TIME"] = DefaultSetting(name="LEVEL_EXTRA_TIME", default=30, description="time to enter/exit a level", 
      transFun=lambda x: float(x), checkFun=lambda x: x>=0, checkDescription="a non-negative number")
    self.default_settings["AUTO_TRANSFORM"] = DefaultSetting(name="AUTO_TRANSFORM", default="ON", description="on/off auto transform", 
      transFun=lambda x: x.upper(), checkFun=lambda x: x in ["ON", "OFF"], checkDescription="either ON or OFF")

  def create_tables(self, guild):
    super().create_tables(guild)
    if "leaderboard" not in self.db[guild.id]:
      self.db[guild.id].create_table("leaderboard", ["playerid", "season", "week"], playerid="int", season="int", week="int", 
                                     hero1="txt", hero2="txt", hero3="txt", kill="int", time="real", group_rank="int", gm_rank="int")
    if "player_info" not in self.db[guild.id]:
      self.db[guild.id].create_table("player_info", "playerid", playerid="int", gameid="txt", flag="txt")
    if "blessed_hero" not in self.db[guild.id]:
      self.db[guild.id].create_table("blessed_hero", ["season", "week"], season="int", week="int", hero="txt")
  
  async def close(self):
    await super().close()

    
if __name__ == "__main__":
  import os
  import dotenv
  from base.modules.interactive_help import InteractiveHelpCommand
  import logging.config
  logging.config.fileConfig("logging.conf")
  #Loading the secret key.
  dotenv.load_dotenv()
  TOKEN = os.getenv("DISCORD_TOKEN")
  APPA = int(os.getenv("APPA_ID"))
  SIN = int(os.getenv("SIN_ID"))
  #SERVER = int(os.getenv("SERVER_ID"))
  cog_categories = {
    "Administration":["Database Commands", "Settings Management Commands", "Data Fetching Commands", "Administration Commands"],
    "Moderation":["Message Management Commands", "User Management Commands", "Channel Management Commands", "Moderation Commands", "Role Management Commands"],
    "Information":["Stats Commands", "Information Commands", "Leaderboard Commands"],
    "Miscellaneous":["Transformation Commands", "Command Management", "General Commands"]
  }
  intents = discord.Intents.default()
  intents.members = True
  bot = CyraBot(
    command_prefix=dynamic_prefix,
    owner_ids=set([APPA, SIN]),
    case_insensitive = True,
    help_command = InteractiveHelpCommand(cog_categories),
    intents=intents,
    #server_id = SERVER
  )
  bot.run(TOKEN)
