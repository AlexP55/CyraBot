import random
import traceback
import time
import json
import re
import sys
from datetime import datetime

import discord
from discord.ext import commands

from base.modules.custom_commands import add_cmd_from_row
from base.modules.db_manager import Database
from base.modules.settings_manager import Settings
from base.modules.settings_manager import DefaultSetting

class BaseBot(commands.Bot):

  games = [
    "The Legend of Zelda: A Link to the Past","The Legend of Zelda: Ocarina of Time","The Legend of Zelda: Majora's Mask","The Legend of Zelda: The Wind Waker",
    "Super Mario 64","Super Mario Galaxy","Pokemon Red","Pokemon Blue","Pokemon Gold","Pokemon Silver",
    "Final Fantasy I","Final Fantasy II","Final Fanatasy III","Final Fantasy IV","Final Fantasy V","Final Fanatasy VI",
    "Final Fantasy VII","Final Fantasy VIII","Final Fantasy IX","Final Fantasy X","Final Fantasy XII","Final Fantasy XIII",
    "Diablo III","Halo 3: ODST","Halo: Reach","Super Smash Bros. Melee","Kingdom Hearts","Kingdom Hearts II",
    "Ōkami","Assassin's Creed","Assassin's Creed II","Assassin's Creed III", "Halo: Combat Evolved",
    "Dark Souls","Dark Souls II","Dark Souls III","Bloodborne", "Red Dead Redemption",
    "The Witcher II: Assassins of Kings","The Witcher III: The Wild Hunt", "World of Warcraft",
    "Realm Defense", "League of Legends", "Mass Effect", "Chrono Trigger", "Tetris",
  ]

  anime = [
    "Fullmetal Alchemist: Brotherhood","Fullmetal Alchemist","Attack on Titan","Akame ga KILL!", "Elfen Lied",
    "Dragon Ball","Steins;Gate","Overlord","Death Parade","Death Note","Angel Beats!", "Vinland Saga",
    "Dr. Stone","Fate/stay night","Fate/Stay Night: Unlimited Blade Works","Clannad","Violet Evergarden","Accel World",
    "The Promised Neverland", "Kami no Tou", 
  ]

  async def find_prefix(self, message):
    prefix = await self.get_prefix(message)
    if type(prefix) == list:
      for pre in prefix:
        if message.startswith(pre):
          return pre
      else:
        return None
    return prefix

  def get_channel(self, guild, **kwargs):
    return discord.utils.get(guild.text_channels, **kwargs)

  def get_bot_name(self, guild):
    if guild.me.nick is None:
      return guild.me.name
    return guild.me.nick
    
  async def log_error(self, guild, *, title, description=None, timestamp=None, fields:dict=None):
    if not self.get_setting(guild, "ERROR_LOG") == "ON":
      return
    embed = self._create_embed(title, description, discord.Colour.red(), timestamp, fields)
    embed.set_footer(text="ERROR LOG")
    await self.get_log(guild, "error-log").send(embed=embed)
    
  async def log_mod(self, guild, *, title, description=None, timestamp=None, fields:dict=None):
    if not self.get_setting(guild, "MOD_LOG") == "ON":
      return
    embed = self._create_embed(title, description, discord.Colour.green(), timestamp, fields)
    embed.set_footer(text="MOD LOG")
    await self.get_log(guild, "mod-log").send(embed=embed)

  async def log_admin(self, guild, *, title, description=None, timestamp=None, fields:dict=None):
    if not self.get_setting(guild, "ADMIN_LOG") == "ON":
      return
    embed = self._create_embed(title, description, discord.Colour.blue(), timestamp, fields)
    embed.set_footer(text="ADMIN LOG")
    await self.get_log(guild, "admin-log").send(embed=embed)

  async def log_audit(self, guild, *, title, description=None, timestamp=None, fields:dict=None):
    if not self.get_setting(guild, "AUDIT_LOG") == "ON":
      return
    embed = self._create_embed(title, description, discord.Colour.gold(), timestamp, fields)
    embed.set_footer(text="AUDIT LOG")
    await self.get_log(guild, "audit-log").send(embed=embed)

  def _create_embed(self, title, description=None, colour=discord.Colour.from_rgb(54,57,63), timestamp=None, fields:dict=None):
    if timestamp is None:
      timestamp = datetime.utcnow()
    embed = discord.Embed(title=title, description=description, colour=colour, timestamp=timestamp)
    if fields is not None:
      for key, value in fields.items():
        if key and value:
          embed.add_field(name=f"{key}:", value=f"{value}", inline=False)
    return embed

  def get_setting(self, guild, setting_name):
    try:
      value = self.settings[guild.id].get(setting_name)
    except Exception as e:
      if setting_name in self.default_settings:
        value = self.default_settings[setting_name].default
      else:
        raise e
    if setting_name in self.default_settings:
      try:
        value = self.default_settings[setting_name].transform_setting(value)
      except:
        value = self.default_settings[setting_name].default
    return value

  async def set_setting(self, guild, setting_name, value, context=None):
    # type check and adapt the settings in the bot's guild if there is a change in settings db
    if setting_name in self.default_settings and context is not None:
      value = await self.default_settings[setting_name].adapt_setting(value, context)
    self.settings[guild.id].set(setting_name, value)
    return value

  def add_setting(self, guild, setting_name, value, description=None):
    self.settings[guild.id].add(setting_name, value)
    if description is not None:
      self.add_setting_description(guild, setting_name, description)

  def add_setting_description(self, guild, setting_name, description):
    self.settings[guild.id].add_description(setting_name, description)

  def rm_setting(self, guild, setting_name):
    self.settings[guild.id].rm(setting_name)


  async def init_bot(self, guild):
    if guild.me.nick is None:
      await guild.me.edit(nick="A Bot")
    if guild.id not in self.db:
      self.db[guild.id] = Database(guild.id)
    if guild.id not in self.user_stats:
      self.user_stats[guild.id] = {}
    if guild.id not in self.settings:
      self.settings[guild.id] = Settings(self.db[guild.id])
      self.add_default_settings(guild)
    await self.create_roles(guild)
    await self.create_logs(guild)
    self.create_tables(guild)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for cog in self.cogs.values():
      # you can initialze your cog during a guild join if you have init_guild() function for guild
      if callable(getattr(cog, "init_guild", None)):
        cog.init_guild(guild)
    self.intialized[guild.id] = True
    print(f"({time}) {self.user} has connected to: {guild.name} ({guild.id})")
    try:
      await self.log_admin(guild, title="Bot connected")
    except:
      pass
    
  async def load_custom_commands(self, guild):
    #Add all stores user_commands
    cmds = self.db[guild.id].select("user_commands")
    if cmds is not None:
      cmds.sort(key=lambda cmd: cmd["cmdname"])
      for cmd in cmds:
        try:
          await add_cmd_from_row(self, guild, cmd)
        except Exception as e:
          print(f"Error when adding command {cmd['cmdname']}: {e}")

  def get_log(self, guild, name):
    bot_category = self.get_bot_category(guild)
    if bot_category is None:
      return None
    return discord.utils.get(guild.text_channels, name=name, category_id=bot_category.id)

  def get_mod_role(self, guild):
    name = self.get_setting(guild, "MOD_ROLE_NAME")
    return discord.utils.get(guild.roles, name=name)
    
  def get_admin_role(self, guild):
    name = self.get_setting(guild, "ADMIN_ROLE_NAME")
    return discord.utils.get(guild.roles, name=name)

  def get_bot_role(self, guild):
    name = self.get_setting(guild, "BOT_ROLE_NAME")
    return discord.utils.get(guild.roles, name=name)

  def get_cmd_role(self, guild):
    name = self.get_setting(guild, "CMD_ROLE_NAME")
    return discord.utils.get(guild.roles, name=name)

  def get_mute_role(self, guild):
    name = self.get_setting(guild, "MUTE_ROLE_NAME")
    return discord.utils.get(guild.roles, name=name)

  def get_bot_category(self, guild):
    name = self.get_setting(guild, "BOT_CATEGORY_NAME")
    return discord.utils.get(guild.categories, name=name)

  async def set_random_status(self):
    n = random.randint(0,1)
    if n == 0:
      await self.change_presence(activity=discord.Game(name=random.choice(self.games)))
    elif n == 1:
      await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(self.anime)))

  def update_user_stats(self, guild):
    db = self.db[guild.id]
    for userid, stat in self.user_stats[guild.id].items():
      if stat["change"] is True:
        prev = db.select("user_statistics", userid)
        if prev is None:
          db.insert_or_update("user_statistics", userid,
                              stat["messages"], stat["commands"], stat["words"],
                              stat["reactions"], stat["reacts_to_own"])
        else:
          db.insert_or_update("user_statistics", userid,
                              prev["total_messages"]+stat["messages"],
                              prev["total_commands"]+stat["commands"],
                              prev["total_words"]+stat["words"],
                              prev["total_reacts"]+stat["reactions"],
                              prev["reacts_to_own"]+stat["reacts_to_own"]
          )
    self.user_stats[guild.id] = {}#clear stats

  #This global command error handler just adds the embed to the error log.
  #Any additional stuff should be done before calling this handler from the subclass.
  async def on_command_error(self, context, error):
    title = f"A {error.__class__.__name__} occured"
    if hasattr(error, "original"):
      error = error.original
    fields = {"User":f"{context.author.mention}\n{context.author}",
              "Channel":f"{context.message.channel.mention}",
              "Command":f"{context.message.content}",
             f"{error.__class__.__name__}":f"{error}"}
    await self.log_error(context.guild, title=title, fields=fields, timestamp=context.message.created_at)
  
  # the error handler for task, need to be called in try except block in each task
  async def on_task_error(self, task, error, guild):
    title = f"A {error.__class__.__name__} occured"
    if hasattr(error, "original"):
      error = error.original
    fields = {"Task":task,
             f"{error.__class__.__name__}":f"{error}"}
    await self.log_error(guild, title=title, fields=fields)
    
  async def on_error(self, event, *args, **kwargs):
    error = sys.exc_info()[1]
    if len(args) > 0:
      if isinstance(args[0], list):
        first_arg = args[0][0]
      else:
        first_arg = args[0]
      if isinstance(first_arg, discord.Guild):
        guild = first_arg
      else:
        if isinstance(first_arg, discord.Reaction):
          first_arg = first_arg.message.channel
        elif isinstance(first_arg, discord.Message):
          first_arg = first_arg.channel
        if hasattr(first_arg, "guild"):
          guild = first_arg.guild
        elif hasattr(fist_arg, "guild_id"):
          guild = self.get_guild(fist_arg.guild_id)
        else:
          guild = None
    else:
      guild = None
    if guild is None:
      guild = self.main_server
    if guild is not None:
      title = f"A {error.__class__.__name__} occured"
      if hasattr(error, "original"):
        error = error.original
      fields = {"Event":event,
               f"{error.__class__.__name__}":f"{error}"}
      await self.log_error(guild, title=title, fields=fields)
    else:
      await super().on_error(event, *args, **kwargs)

  def create_tables(self, guild):
    if "user_warnings" not in self.db[guild.id]:
      self.db[guild.id].create_table("user_warnings", "userid", userid="int", username="txt", count="int", expires="real")
    if "users_muted" not in self.db[guild.id]:
      self.db[guild.id].create_table("users_muted", "userid", userid="int", expires="real")
    if "user_statistics" not in self.db[guild.id]:
      self.db[guild.id].create_table("user_statistics", "userid", userid="int", total_messages="int", total_commands="int", total_words="int", total_reacts="int", reacts_to_own="int")
    if "user_commands" not in self.db[guild.id]:
      self.db[guild.id].create_table("user_commands", "cmdname", cmdname="txt", message="txt", attributes="txt", isgroup="int_not_null", lock="int_not_null", glob="int_not_null", perm="int_not_null")
    if "messages" not in self.db[guild.id]:
      self.db[guild.id].create_table("messages", "mid", mid="int", time="real", aid="int", author="txt", cid="int", channel="txt", content="txt", embeds="txt", files="txt")


  async def create_logs(self, guild):
    bot_category = self.get_bot_category(guild)
    if bot_category is None:
      bot_cat_name = self.get_setting(guild, "BOT_CATEGORY_NAME")
      bot_category = await guild.create_category(bot_cat_name)
    if discord.utils.get(guild.text_channels, name="bot-commands", category_id=bot_category.id) is None:
      await guild.create_text_channel(
        "bot-commands",
        topic="Want to use the bots' commands? This is the right place.",
        category=bot_category,
        position=0,
      )
    #Channel permissions for the bot
    permissions = {
      guild.me: discord.PermissionOverwrite(
        create_instant_invite=True, manage_channels=True, manage_roles=True, manage_webhooks=True, read_messages=True,
        send_messages=True, send_tts_messages=True, manage_messages=True, embed_links=True, 
        attach_files=True, read_message_history=True, mention_everyone=True, use_external_emojis=True, add_reactions=True
      )
    }
    #Restrict access to @everyone
    permissions[guild.default_role] = discord.PermissionOverwrite(
      create_instant_invite=False, manage_channels=False, manage_roles=False, manage_webhooks=False, read_messages=False,
      send_messages=False, send_tts_messages=False, manage_messages=False, embed_links=False, 
      attach_files=False, read_message_history=False, mention_everyone=False, use_external_emojis=False, add_reactions=False
    )
    #Channel permissions for the bot owners
    for owner_id in self.owner_ids:
      owner = guild.get_member(owner_id)
      if owner is not None:
        permissions[owner] = discord.PermissionOverwrite(
          create_instant_invite=False, manage_channels=True, manage_roles=True, manage_webhooks=False, read_messages=True,
          send_messages=True, send_tts_messages=False, manage_messages=False, embed_links=False, 
          attach_files=False, read_message_history=True, mention_everyone=False, use_external_emojis=False, add_reactions=True
        )
    #Add permissions for admin role
    admin_role = self.get_admin_role(guild)
    permissions[admin_role] = discord.PermissionOverwrite(
      create_instant_invite=False, manage_channels=False, manage_roles=False, manage_webhooks=False, read_messages=True,
      send_messages=False, send_tts_messages=False, manage_messages=False, embed_links=False, 
      attach_files=False, read_message_history=True, mention_everyone=False, use_external_emojis=False, add_reactions=True
    )
    error_log = discord.utils.get(guild.text_channels, name="error-log", category_id=bot_category.id)
    if error_log is None:
      await guild.create_text_channel(
        "error-log",
        topic="An error log.",
        category=bot_category,
        position=1,
        overwrites=permissions,
        reason="A channel to log all bot errors."
      )
    else:
      await error_log.edit(overwrites=permissions)
    admin_log = discord.utils.get(guild.text_channels, name="admin-log", category_id=bot_category.id)
    if admin_log is None:
      await guild.create_text_channel(
        "admin-log",
        topic="An administration log.",
        category=bot_category,
        position=3,
        overwrites=permissions,
        reason="A channel to log all administration actions"
      )
    else:
      await admin_log.edit(overwrites=permissions)
    #Before creating the mod log, add the permissions.
    mod_role = self.get_mod_role(guild)
    permissions[mod_role] = discord.PermissionOverwrite(
      create_instant_invite=False, manage_channels=False, manage_roles=False, manage_webhooks=False, read_messages=True,
      send_messages=False, send_tts_messages=False, manage_messages=False, embed_links=False, 
      attach_files=False, read_message_history=True, mention_everyone=False, use_external_emojis=False, add_reactions=True
    )
    mod_log = discord.utils.get(guild.text_channels, name="mod-log", category_id=bot_category.id)
    if mod_log is None:
      await guild.create_text_channel(
        "mod-log",
        topic="A moderation log.",
        category=bot_category,
        position=2,
        overwrites=permissions,
        reason="A channel to log all moderation actions"
      )
    else:
       await mod_log.edit(overwrites=permissions)
    audit_log = discord.utils.get(guild.text_channels, name="audit-log", category_id=bot_category.id)
    if audit_log is None:
      await guild.create_text_channel(
        "audit-log",
        topic="A log for certain events with user information.",
        category=bot_category,
        position=4,
        overwrites=permissions,
        reason="A channel to log all specific events"
      )
    else:
       await audit_log.edit(overwrites=permissions)

  async def create_roles(self, guild):
    bot_role = self.get_bot_role(guild)
    if bot_role is None:
      bot_role = await guild.create_role(
        name=self.get_setting(guild, "BOT_ROLE_NAME"),
        permissions=discord.Permissions(
          kick_members=True, ban_members=True, manage_channels=True, create_instant_invite=True,
          add_reactions=True, view_channel=True, send_messages=True, send_tts_messages=True, manage_messages=True,
          embed_links=True, attach_files=True, read_message_history=True, mention_everyone=True, use_external_emojis=True,
          change_nickname=True, manage_nicknames=True, manage_roles=True, manage_emojis=True,
        ),
        colour=discord.Colour.red(),
        hoist=True,
        mentionable=True
      )
    await guild.me.add_roles(bot_role)
    admin_role = self.get_admin_role(guild)
    if admin_role is None:
      admin_role = await guild.create_role(
        name=self.get_setting(guild, "ADMIN_ROLE_NAME"),
        permissions=discord.Permissions(
          #administrator=True,
          kick_members=True, ban_members=True, manage_channels=True, create_instant_invite=True,
          add_reactions=True, view_channel=True, send_messages=True, send_tts_messages=True, manage_messages=True,
          embed_links=True, attach_files=True, read_message_history=True, mention_everyone=True, use_external_emojis=True,
          change_nickname=True, manage_nicknames=True, manage_roles=True, manage_emojis=True,
        ),
        colour=discord.Colour.blue(),
        hoist=True,
        mentionable=True,
        reason="Role is needed for the administration log."
      )
    mod_role = self.get_mod_role(guild)
    if mod_role is None:
      mod_role = await guild.create_role(
        name=self.get_setting(guild, "MOD_ROLE_NAME"),
        permissions=discord.Permissions(
          kick_members=True, ban_members=True, manage_channels=True, create_instant_invite=True,
          add_reactions=True, view_channel=True, send_messages=True, send_tts_messages=True, manage_messages=True,
          embed_links=True, attach_files=True, read_message_history=True, mention_everyone=True, use_external_emojis=True,
          change_nickname=True, manage_nicknames=True, manage_roles=True, manage_emojis=True,
        ),
        colour=discord.Colour.green(),
        hoist=True,
        mentionable=True,
        reason="Role is needed for the moderation log."
      )
    command_master = self.get_cmd_role(guild)
    if command_master is None:
      command_master = await guild.create_role(
        name=self.get_setting(guild, "CMD_ROLE_NAME"),
        permissions=discord.Permissions(
          add_reactions=True, view_channel=True, send_messages=True
        ),
        colour=discord.Colour.light_grey(),
        hoist=True,
        mentionable=True
      )
    mute_role = self.get_mute_role(guild)
    if mute_role is None:
      mute_role = await guild.create_role(
        name=self.get_setting(guild, "MUTE_ROLE_NAME"),
        permissions=discord.Permissions(
          create_instant_invite=False, manage_channels=False, manage_roles=False, manage_webhooks=False, view_channel=True,
          send_messages=False, send_tts_messages=False, manage_messages=False, embed_links=False, 
          attach_files=False, read_message_history=True, mention_everyone=False, use_external_emojis=False, add_reactions=False,
          priority_speaker=False, stream=False, connect=False, speak=False, mute_members=False, deafen_members=False,
          move_members=False, use_voice_activation=False
        ),
        colour=discord.Colour.light_grey(),
        hoist=False,
        mentionable=False
      )
      mute_channel_permissions = discord.PermissionOverwrite(
        create_instant_invite=False, manage_channels=False, manage_roles=False, manage_webhooks=False, view_channel=True,
        send_messages=False, send_tts_messages=False, manage_messages=False, embed_links=False, 
        attach_files=False, read_message_history=True, mention_everyone=False, use_external_emojis=False, add_reactions=False,
        priority_speaker=False, stream=False, connect=False, speak=False, mute_members=False, deafen_members=False,
        move_members=False, use_voice_activation=False
      )
      #Restrict access to channels
      for channel in guild.channels:
        everyone_permissions = channel.overwrites_for(guild.default_role)
        if everyone_permissions is None or everyone_permissions.pair[1].view_channel is True:   #Deny-Pair
          #Skip private channels, we do not want Muted people to suddenly have access to the channel
          continue
        try:
          await channel.set_permissions(mute_role, overwrite=mute_channel_permissions)
        except:
          pass

  async def on_guild_channel_create(self, channel):
    everyone_permissions = channel.overwrites_for(channel.guild.default_role)
    if everyone_permissions is None or everyone_permissions.pair()[1].view_channel is True:
      #Skip private channels, we do not want Muted people to suddenly have access to the channel
      return
    mute_permissions = discord.PermissionOverwrite(
      create_instant_invite=False, manage_channels=False, manage_roles=False, manage_webhooks=False, view_channel=True,
      send_messages=False, send_tts_messages=False, manage_messages=False, embed_links=False, 
      attach_files=False, read_message_history=True, mention_everyone=False, use_external_emojis=False, add_reactions=False,
      priority_speaker=False, stream=False, connect=False, speak=False, mute_members=False, deafen_members=False,
      move_members=False, use_voice_activation=False
    )
    mute_role = self.get_mute_role(channel.guild)
    try:
      await channel.set_permissions(mute_role, overwrite=mute_permissions)
    except:
      pass

  def adjust_user_stats(self, guild, user, msg, cmd, wrd, rct, own):
    if hasattr(user, "id"):
      id = user.id
    else: #passed an id directly
      id = user
    if guild.id not in self.user_stats:
      self.user_stats[guild.id] = {}
    user_stats = self.user_stats[guild.id]
    if id not in user_stats:
      user_stats[id] = {"messages":0,"commands":0,"words":0,"reactions":0,"reacts_to_own":0,"change":False}
    stats = user_stats[id]
    stats["messages"] += msg
    stats["commands"] += cmd
    stats["words"] += wrd
    stats["reactions"] += rct
    stats["reacts_to_own"] += own
    if sum([msg, cmd, wrd, rct, own]) != 0:
      stats["change"] = True


  async def on_reaction_add(self, reaction, user):
    if hasattr(reaction.message, "guild") and hasattr(reaction.message.guild, "id"):
      if reaction.message.author.id == user.id:
        self.adjust_user_stats(reaction.message.guild, user, 0, 0, 0, 1, 1)
      else:
        self.adjust_user_stats(reaction.message.guild, user, 0, 0, 0, 1, 0)

  async def on_reaction_remove(self, reaction, user):
    if hasattr(reaction.message, "guild") and hasattr(reaction.message.guild, "id"):
      if reaction.message.author.id == user.id:
        self.adjust_user_stats(reaction.message.guild, user, 0, 0, 0, -1, -1)
      else:
        self.adjust_user_stats(reaction.message.guild, user, 0, 0, 0, -1, 0)

  async def on_message(self, message):
    if message.type != discord.MessageType.default:
      return # ignores a system message
    if hasattr(message, "guild") and hasattr(message.guild, "id"): #only guild messages are parsed
      if message.content != "":
        prefix = await self.find_prefix(message)
        if prefix is not None:
          prefix_match = re.match(f"({re.escape(prefix)}+)", message.content)
          if prefix_match is not None: #command found
            prefix_count = len(prefix_match.group(0))/len(prefix)
            if prefix_count == 1: #bot commands should not increase words
              cmd = 1
              wrd = 0
            else: #multiple ? are not counted as a command
              cmd = 0
              wrd = len(message.content.split())
          else:
            prefix_count = 0
            cmd = 0
            wrd = len(message.content.split())
        else: #Prefix is None, if multiple prefixes were not found in the message
          prefix_count = 0
          cmd = 0
          wrd = len(message.content.split())
      else: #ignore empty message
        return
      self.adjust_user_stats(message.guild, message.author, 1, cmd, wrd, 0, 0)         
      #now process commands(only for guild messages)
      if prefix_count == 1:
        await self.process_commands(message)

  async def on_guild_join(self, guild):
    await self.init_bot(guild)
    await self.load_custom_commands(guild)

  async def on_ready(self):
    self.intialized = {}
    if not hasattr(self, "db"):
      self.db = {}
    if not hasattr(self, "user_stats"):
      self.user_stats = {}
    if not hasattr(self, "settings"):
      self.settings = {}
    if not hasattr(self, "default_settings"):
      self.initialize_default_settings()
    for guild in self.guilds:
      await self.init_bot(guild)
    #Loading base extensions.
    @self.check # add a global check to the bot
    def check_initialized(context):
      if context.guild.id not in context.bot.intialized or not context.bot.intialized[context.guild.id]:
        raise commands.CheckFailure("Guild {context.guild.name} is not initialized")
      return True
    self.load_all_cogs()
    for guild in self.guilds:
      await self.load_custom_commands(guild) # make sure the custom commands are loaded after cog is loaded
    self.start_at = time.time()
    
  def load_all_cogs(self):
    self.load_cogs("base.cogs.administration", "base.cogs.database_management",
                   "base.cogs.user_management", "base.cogs.message_management",
                   "base.cogs.settings_management", "base.cogs.secret_channels",
                   "base.cogs.command_management", "base.cogs.channel_management")


  def load_cogs(self, *args, **kwargs):
    for extension in args:
      try:
        self.load_extension(extension)
      except:
        print(f"Could not load extension: {extension}")
        traceback.print_exc()

  async def on_guild_remove(self, guild):
    pass # Placeholder
    
  async def delete_roles(self, guild):
    mod_role = self.get_mod_role(guild)
    if mod_role is not None:
      await mod_role.delete()
    admin_role = self.get_admin_role(guild)
    if admin_role is not None:
      await admin_role.delete()
    bot_role = self.get_bot_role(guild)
    if bot_role is not None:
      await bot_role.delete()
    cmd_role = self.get_cmd_role(guild)
    if cmd_role is not None:
      await cmd_role.delete()
    mute_role = self.get_mute_role(guild)
    if mute_role is not None:
      await mute_role.delete()

  async def delete_logs(self, guild):
    #Get the bot category
    bot_category = self.get_bot_category(guild)
    #Deleting all channels that were created with the bot
    if bot_category is not None:
      command_channel = discord.utils.get(guild.text_channels, name="bot-commands", category_id=bot_category.id)
      if command_channel is not None:
        await command_channel.delete()
      error_log = self.get_log(guild, "error-log")
      if error_log is not None:
        await error_log.delete()
      mod_log = self.get_log(guild, "mod-log")
      if mod_log is not None:
        await mod_log.delete()
      admin_log = self.get_log(guild, "admin-log")
      if not admin_log is None:
        await admin_log.delete()
      audit_log = self.get_log(guild, "audit-log")
      if not audit_log is None:
        await audit_log.delete()
      await bot_category.delete()
    mod_queue = discord.utils.get(guild.categories, name=f"{guild.me.name}s-queue")
    if mod_queue is not None:
      await mod_queue.delete()
      
  async def change_bot_related_name(self, context, key, value):
    if key == "MOD_ROLE_NAME":
      role = self.get_mod_role(context.guild)
    elif key == "ADMIN_ROLE_NAME":
      role = self.get_admin_role(context.guild)
    elif key == "BOT_ROLE_NAME":
      role = self.get_bot_role(context.guild)
    elif key == "BOT_CATEGORY_NAME":
      role = self.get_bot_category(context.guild)
    elif key == "CMD_ROLE_NAME":
      role = self.get_cmd_role(context.guild)
    elif key == "MUTE_ROLE_NAME":
      role = self.get_mute_role(context.guild)
    else:
      raise LookupError(f"could not set {key} because the corresponding role/channel does not exist.")
    embed = discord.Embed(title="Forced Rename", colour=discord.Colour.blue(), timestamp=context.message.created_at)
    embed.add_field(name=f"{key}:", value=value, inline=False)
    embed.set_footer(text="ADMIN LOG")
    await self.get_log(context.guild, "admin-log").send(content=None, embed=embed)
    await role.edit(name=value)
    
  def initialize_default_settings(self):
    bot_name = self.user.name
    self.default_settings = {}
    self.default_settings["MAX_WARNINGS"] = DefaultSetting(name="MAX_WARNINGS", default=4, description="max allowed warnings", 
      transFun=lambda x: int(x), checkFun=lambda x: x>0, checkDescription="a positive integer")
    self.default_settings["WARN_DURATION"] = DefaultSetting(name="WARN_DURATION", default=5, description="warning expiry (day)", 
      transFun=lambda x: float(x), checkFun=lambda x: x>0, checkDescription="a positive number")
    self.default_settings["MUTE_DURATION"] = DefaultSetting(name="MUTE_DURATION", default=1, description="mute expiry (day)", 
      transFun=lambda x: float(x), checkFun=lambda x: x>0, checkDescription="a positive number")
    self.default_settings["MOD_ROLE_NAME"] = DefaultSetting(name="MOD_ROLE_NAME", default=f"{bot_name}'s Enforcer", description="gives mod commands", 
      adaptFun=lambda value, context: self.change_bot_related_name(context, "MOD_ROLE_NAME", value))
    self.default_settings["ADMIN_ROLE_NAME"] = DefaultSetting(name="ADMIN_ROLE_NAME", default=f"{bot_name}'s Master", description="gives admin commands", 
      adaptFun=lambda value, context: self.change_bot_related_name(context, "ADMIN_ROLE_NAME", value))
    self.default_settings["BOT_ROLE_NAME"] = DefaultSetting(name="BOT_ROLE_NAME", default=f"{bot_name} Role", description="role the bot claims", 
      adaptFun=lambda value, context: self.change_bot_related_name(context, "BOT_ROLE_NAME", value))
    self.default_settings["CMD_ROLE_NAME"] = DefaultSetting(name="CMD_ROLE_NAME", default="Command Master", description="gives command editing access", 
      adaptFun=lambda value, context: self.change_bot_related_name(context, "CMD_ROLE_NAME", value))
    self.default_settings["MUTE_ROLE_NAME"] = DefaultSetting(name="MUTE_ROLE_NAME", default="Muted", description="revokes posting access", 
      adaptFun=lambda value, context: self.change_bot_related_name(context, "MUTE_ROLE_NAME", value))
    self.default_settings["BOT_CATEGORY_NAME"] = DefaultSetting(name="BOT_CATEGORY_NAME", default=f"{bot_name}s-bot-corner", description="category for logs", 
      adaptFun=lambda value, context: self.change_bot_related_name(context, "BOT_CATEGORY_NAME", value))
    self.default_settings["NUM_DELETE_CACHE"] = DefaultSetting(name="NUM_DELETE_CACHE", default=10, description="num of restorable deleted messages", 
      transFun=lambda x: int(x), checkFun=lambda x: x>=0, checkDescription="a non-negative integer")
    self.default_settings["MODMAIL_EXPIRY"] = DefaultSetting(name="MODMAIL_EXPIRY", default=15, description="modmail expiry (min)", 
      transFun=lambda x: float(x), checkFun=lambda x: x>0, checkDescription="a positive number")
    self.default_settings["AUTO_MODMAIL"] = DefaultSetting(name="AUTO_MODMAIL", default="ON", description="on/off modmail auto deletion", 
      transFun=lambda x: x.upper(), checkFun=lambda x: x in ["ON", "OFF"], checkDescription="either ON or OFF", 
      adaptFun=lambda value, context: self.get_cog("General Commands").change_auto_delete(value, context.guild))
    self.default_settings["AUTO_UPDATE"] = DefaultSetting(name="AUTO_UPDATE", default="ON", description="on/off slaps/stats auto update", 
      transFun=lambda x: x.upper(), checkFun=lambda x: x in ["ON", "OFF"], checkDescription="either ON or OFF")
    self.default_settings["ERROR_LOG"] = DefaultSetting(name="ERROR_LOG", default="ON", description="on/off error logging", 
      transFun=lambda x: x.upper(), checkFun=lambda x: x in ["ON", "OFF"], checkDescription="either ON or OFF")
    self.default_settings["ADMIN_LOG"] = DefaultSetting(name="ADMIN_LOG", default="ON", description="on/off admin logging",
      transFun=lambda x: x.upper(), checkFun=lambda x: x in ["ON", "OFF"], checkDescription="either ON or OFF")
    self.default_settings["MOD_LOG"] = DefaultSetting(name="MOD_LOG", default="ON", description="on/off mod logging", 
      transFun=lambda x: x.upper(), checkFun=lambda x: x in ["ON", "OFF"], checkDescription="either ON or OFF")
    self.default_settings["AUDIT_LOG"] = DefaultSetting(name="AUDIT_LOG", default="ON", description="on/off audit logging", 
      transFun=lambda x: x.upper(), checkFun=lambda x: x in ["ON", "OFF"], checkDescription="either ON or OFF")
    self.default_settings["ACTIVE_TIME"] = DefaultSetting(name="ACTIVE_TIME", default=2, description="interactive message active time", 
      transFun=lambda x: float(x), checkFun=lambda x: x>0, checkDescription="a positive number")
  
  def add_default_settings(self, guild):
    #Add default settings for allowed settings
    for key, setting in self.default_settings.items():
      if key not in self.settings[guild.id]:
        self.add_setting(guild, key, setting.default, setting.description)
        
  async def reset_settings(self, context):
    guild = context.guild
    for key, setting in self.default_settings.items():
      if key in self.settings[guild.id]:
        current_setting = self.get_setting(guild, key)
        if not current_setting == setting.default:
          await self.set_setting(guild, key, setting.default, context)
        self.add_setting_description(guild, key, setting.description)
      else:
        self.add_setting(guild, key, setting.default, setting.description)
      
  async def close(self):
    if self.is_closed():
      return
    await super().close() # this method unloads all the cogs
    for guild in self.guilds:
      self.update_user_stats(guild)
    for k,db in self.db.items():
      db.close()
    print("The bot client is completely closed")
    
  def set_main_server(self, id):
    self.main_server_id = id
    
  @property
  def main_server(self):
    if not hasattr(self, "main_server_id"):
      return None
    return self.get_guild(self.main_server_id)

if __name__ == "__main__":
  import os
  import dotenv
  from base.modules.interactive_help import InteractiveHelpCommand
  #loading the secret key for this bot
  dotenv.load_dotenv()
  TOKEN = os.getenv("DISCORD_TOKEN")
  APPA = int(os.getenv("APPA_ID"))
  SIN = int(os.getenv("SIN_ID"))
  SERVER = int(os.getenv("SERVER_ID"))
  cog_categories = {
    "Administration":["Database Commands", "Settings Management Commands", "Administration Commands"],
    "Moderation":["Message Management Commands", "User Management Commands", "Channel Management Commands", "Moderation Commands"],
    "Miscellaneous":["Command Management", "General Commands"]
  }
  async def dynamic_prefix(bot, message):
    if message.type != discord.MessageType.default:
      return
    if hasattr(message, "guild"):
      return "?"
    else: #in DMs the bot can respond to prefix-less messages
      return "?", ""
  bot = BaseBot(
    command_prefix="?",
    owner_ids=set([APPA, SIN]),
    case_insensitive = True,
    help_command = InteractiveHelpCommand(cog_categories)
  )
  bot.set_main_server(SERVER)
  bot.run(TOKEN)
