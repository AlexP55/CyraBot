import random
import discord
from discord.ext import commands
import time
import string
from base.modules.settings_manager import DefaultSetting
import modules.custom_exceptions as custom_exceptions
from base_bot import BaseBot
from modules.cyra_constants import emoji_keys

class CyraBot(BaseBot):

  def get_emoji(self, guild, key):
    return discord.utils.get(guild.emojis, name=emoji_keys[key])

  async def is_cyra(self, guild: discord.Guild):
    if guild.me.nick == "Cyra":
      return True
    elif guild.me.nick == "Elara":
      return False
    else: # reset to Cyra
      self.set_setting(guild, "BOT_ROLE_NAME", "Cyra")
      await guild.me.edit(nick="Cyra")
      return True
  
  def is_willing_to_answer(self, context):
    if context.guild.me.nick == "Elara":
      #If the nick is Elara, there is a chance she will refuse to answer.
      if context.message.content.startswith("?help"):
        return True
      if context.author.id in self.owner_ids:
        return False #Bot owners are immune to Elaras chaos
      try:
        chance = float(self.get_setting(context.guild, "ELARA_REFUSE_CHANCE"))/100.0
      except:
        chance = self.default_settings["ELARA_REFUSE_CHANCE"].default
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
        ]
        responses.append(f"Input:{context.message.content}\nOutput: Chaos")
        raise custom_exceptions.ElaraRefuseToAnswer(random.choice(responses))
      else:
        return True
    else:
      return True
      
  async def finish_info_command(self, context):
    self.energy[context.guild.id][0] = self.energy[context.guild.id][0] + 1
      
  async def respond_to_error(self, context, error):
    # general error handler, used in hero/infomation cog
    if hasattr(context.command, "on_error"):
      # This prevents any commands with local handlers being handled here.
      return
    if context.guild.me.nick == "Cyra":
      if isinstance(error, commands.CommandOnCooldown):
        msg = f"Skill is on cooldown, I should have it ready in {round(error.retry_after)}s."
      elif isinstance(error, custom_exceptions.HeroNotFound):
        msg = f"Emm... None of my colleagues is called **{error.item}**."
      elif isinstance(error, custom_exceptions.AbilityNotFound):
        if error.hero.lower() == "cyra":
          msg = f"Emm... I don't think I am able to use **{error.ability}**."
        else:
          msg = f"Emm... I don't think **{error.hero}** is able to use **{error.ability}**."
      elif isinstance(error, custom_exceptions.DataNotFound):
        msg = f"Sorry, I want to help but I don't know anything about **{error.category} {error.item}**."
      elif isinstance(error, commands.UserInputError):
        msg = f"{context.author.mention}, I'm not sure I understand those arguments.\nPlease refer to `?help {context.command.qualified_name}` for more information."
      elif isinstance(error, commands.CheckFailure):
        msg = f"I'm sorry, you do not have permission to use this command. Please ask my masters."
      else:
        msg = f"Elara stopped me from executing that command. Maybe try something else?\nPlease refer to `?help {context.command.qualified_name}` for information on my commands."
    elif context.guild.me.nick == "Elara":
      if isinstance(error, commands.CommandOnCooldown):
        msg = f"Do not rush me mortal! I cannot use this skill so often. ({round(error.retry_after)}s remains)"
      elif isinstance(error, custom_exceptions.HeroNotFound):
        msg = f"Who is **{error.item}**? Is that a new nickname?"
      elif isinstance(error, custom_exceptions.AbilityNotFound):
        if error.hero.lower() == "elara":
          msg = f"**{error.ability}** sounds cool. Maybe I should learn it from now."
        else:
          msg = f"**{error.ability}** sounds cool. Maybe **{error.hero}** should learn it from now."
      elif isinstance(error, custom_exceptions.DataNotFound):
        msg = f"Tell you a secret: **{error.category} {error.item}** will be the next spoiler.\nJust kidding."
      elif isinstance(error, custom_exceptions.ElaraRefuseToAnswer):
        msg = f"{error}\n||*Elara destroyed your command, maybe you should try one more time?*||"
      elif isinstance(error, commands.UserInputError):
        msg = f"{context.author.mention}, a smart command with awful arguments. Study the `?help {context.command.qualified_name}`, mortal.\n"
      elif isinstance(error, commands.CheckFailure):
        msg = f"Why are you using this command without permission? Watch yourself!"
      else:
        msg = f"Cyra stopped me from executing that command. It's too dangerous, even for myself.\nRefer to `?help {context.command.qualified_name}` for information on my commands."
    else:
      msg = "I cannot process your command, please refer to `?help [command]` for more information"
    #Send response
    await context.send(msg)
    self.energy[context.guild.id][1] = self.energy[context.guild.id][1] + 1

  async def transform(self, guild: discord.Guild):
    is_cyra = await self.is_cyra(guild)
    bot_category = self.get_bot_category(guild)
    admin_role = self.get_admin_role(guild)
    mod_role = self.get_mod_role(guild)
    bot_role = self.get_bot_role(guild)
    if is_cyra:
      if guild.id == self.main_server:
        with open("avatar/Elara.png", "rb") as avatar:
          await self.user.edit(avatar=avatar.read())
      await guild.me.edit(nick="Elara")
      if mod_role is not None:
        mod_role_name = f"{guild.me.nick}'s Ravager"
        await self.set_setting(guild, "MOD_ROLE_NAME", mod_role_name)
        await mod_role.edit(name=mod_role_name)
      if bot_role is not None:
        bot_role_name = guild.me.nick
        await self.set_setting(guild, "BOT_ROLE_NAME", bot_role_name)
        await bot_role.edit(name=bot_role_name, color=discord.Colour.dark_purple())
    else:
      if guild.id == self.main_server:
        with open("avatar/Cyra.png", "rb") as avatar:
          await self.user.edit(avatar=avatar.read())
      await guild.me.edit(nick="Cyra")
      if mod_role is not None:
        mod_role_name = f"{guild.me.nick}'s Enforcer"
        await self.set_setting(guild, "MOD_ROLE_NAME", mod_role_name)
        await mod_role.edit(name=mod_role_name)
      if not bot_role is None:
        bot_role_name = guild.me.nick
        await self.set_setting(guild, "BOT_ROLE_NAME", bot_role_name)
        await bot_role.edit(name=bot_role_name, color=discord.Colour.red())
    if admin_role is not None:
      admin_role_name = f"{guild.me.nick}'s Master"
      await self.set_setting(guild, "ADMIN_ROLE_NAME", admin_role_name)
      await admin_role.edit(name=admin_role_name)
    if bot_category is not None:
      bot_category_name = f"{guild.me.nick}s-bot-corner"
      await self.set_setting(guild, "BOT_CATEGORY_NAME", bot_category_name)
      await bot_category.edit(name=bot_category_name)
    self.energy[guild.id][0] = 0
    self.energy[guild.id][1] = 0
    self.last_transform[guild.id] = time.time()
    return is_cyra
    
  async def init_bot(self, guild):
    # overrides the method: check nick name, add Cyra-specific variables
    await super().init_bot(guild)
    if guild.me.nick not in ["Cyra", "Elara"]:
      await guild.me.edit(nick="Cyra")
    self.energy[guild.id] = [0,0]
    self.last_transform[guild.id] = time.time()

  async def on_command_error(self, context, error):
    ignored = (commands.CommandOnCooldown, )
    if isinstance(error, ignored):
      return
    if isinstance(error, commands.CommandNotFound):
      if context.guild.me.nick == "Cyra":
        await context.send(
          f"{context.author.mention} I have my dignity as a goddess and what you ask is beneath me. "
          f"Refer to `?help` to see how I can serve you."
        )
      elif context.guild.me.nick == "Elara":
        await context.send(
          f"{context.author.mention}, **do not try to fool me** with your fake command. Refer to `?help` to get a taste of the darkness."
        )
      else:
        await context.send(
          f"Command not found, please refer to `?help` for more information"
        )
    #Log the error.
    await super().on_command_error(context, error)
    
  async def on_guild_join(self, guild):
    await super().on_guild_join(guild)
    
  async def on_ready(self):
    self.energy = {}
    self.last_transform = {}
    await super().on_ready()
    
  def load_all_cogs(self):
    super().load_all_cogs()
    self.load_cogs("cogs.general_information","cogs.stats_infomation","cogs.data_fetching", "cogs.transform_cyra")

  async def on_guild_remove(self, guild):
    await super().on_guild_remove(guild)
  
  def initialize_default_settings(self):
    super().initialize_default_settings()
    bot_name = "Cyra"
    self.default_settings["MOD_ROLE_NAME"].default = f"{bot_name}'s Enforcer"
    self.default_settings["ADMIN_ROLE_NAME"].default = f"{bot_name}'s Master"
    self.default_settings["BOT_ROLE_NAME"].default = f"{bot_name}"
    self.default_settings["BOT_CATEGORY_NAME"].default = f"{bot_name}s-bot-corner"
    self.default_settings["ELARA_REFUSE_CHANCE"] = DefaultSetting(name="ELARA_REFUSE_CHANCE", default=10, description="chance to ignore command", 
      transFun=lambda x: float(x), checkFun=lambda x: x>=0, checkDescription="a non-negative number")
    self.default_settings["SEARCH_LIMIT"] = DefaultSetting(name="SEARCH_LIMIT", default=11, description="max num of entries by a query", 
      transFun=lambda x: int(x), checkFun=lambda x: 0<x<=11, checkDescription="an integer between 1 and 11")
    self.default_settings["AUTO_TRANSFORM"] = DefaultSetting(name="AUTO_TRANSFORM", default="ON", description="on/off auto transform", 
      transFun=lambda x: x.upper(), checkFun=lambda x: x in ["ON", "OFF"], checkDescription="either ON or OFF")
  
  async def close(self):
    await super().close()
    
  def set_main_server(self, id):
    self.main_server = id

    
if __name__ == "__main__":
  import os
  import dotenv
  from base.modules.interactive_help import InteractiveHelpCommand
  #Loading the secret key.
  dotenv.load_dotenv()
  TOKEN = os.getenv("DISCORD_TOKEN")
  APPA = os.getenv("APPA_ID")
  SIN = os.getenv("SIN_ID")
  SERVER = os.getenv("SERVER_ID")
  cog_categories = {
    "Administration":["Database Commands", "Settings Management Commands", "Data Fetching Commands", "Administration Commands"],
    "Moderation":["Message Management Commands", "User Management Commands", "Channel Management Commands", "Moderation Commands"],
    "Information":["Stats Commands", "Information Commands"],
    "Miscellaneous":["Transformation Commands", "Command Management", "General Commands"]
  }
  async def dynamic_prefix(bot, message):
    if message.type != discord.MessageType.default:
      return
    if hasattr(message, "guild"):
      return "?"
    else: #in DMs the bot can respond to prefix-less messages
      return "?", ""
  bot = CyraBot(
    command_prefix="?",
    owner_ids=set([APPA, SIN]),
    case_insensitive = True,
    help_command = InteractiveHelpCommand(cog_categories)
  )
  bot.set_main_server(SERVER)
  bot.run(TOKEN)
