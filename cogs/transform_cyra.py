import discord
from discord.ext import commands, tasks
from modules.cyra_converter import find_hero_from_text, hero_and_secret
from modules.cyra_serializable import TransformListEntry
from base.modules.constants import CACHE_PATH as path
from base.modules.serializable_object import dump_json
import logging
import json
import random
import os

logger = logging.getLogger(__name__)

class TransformationCog(commands.Cog, name="Transformation Commands"):
  def __init__(self, bot):
    self.bot = bot
    if not os.path.isdir(path):
      os.mkdir(path)
    info = TransformListEntry.from_json(f'{path}/transform_list.json')
    if not info:
      self.transform_list = ["cyra", "elara"]
      self.transform_interval = 2.0
    else:
      self.transform_list = info["list"]
      self.transform_interval = info["interval"]
    self.auto_transform = self.create_task()
    self.auto_transform.start()
    
  def cog_unload(self):
    self.auto_transform.cancel()
    dump_json({"list":self.transform_list, "interval":self.transform_interval}, f'{path}/transform_list.json')
    
  async def cog_command_error(self, context, error):
    if hasattr(context.command, "on_error"):
      # This prevents any commands with local handlers being handled here.
      return
    if isinstance(error, commands.CommandOnCooldown):
      await context.send(f"Skill is on cooldown, please try again in {round(error.retry_after)}s.")
    elif isinstance(error, commands.CheckFailure):
      await context.send(f"Sorry {context.author.mention}, but you do not have permission to transform the bot.")
    elif isinstance(error, commands.UserInputError):
      await context.send(f"Sorry {context.author.mention}, but I could not understand the arguments passed to `{context.command.qualified_name}`.")
    else:
      await context.send(f"Sorry {context.author.mention}, something unexpected happened during my transformation.")
  
  def create_task(self):
    @tasks.loop(hours=self.transform_interval)
    async def auto_transform():
      if self.auto_transform.current_loop == 0: # don't transform at the first time
        return
      after = None
      for guild_id, db in self.bot.db.items():
        guild = discord.utils.get(self.bot.guilds, id=guild_id)
        if not self.get_auto_transform(guild):
          continue
        try:
          logger.debug(f"Transforming in {guild.name} ({guild.id}).")
          before = self.bot.get_nick(guild).lower()
          if after is None:
            after = self.get_random_trans_hero(before)
            change_avatar = True
          else:
            change_avatar = False
          await self.bot.transform(guild, after, change_avatar=change_avatar)
          await self.bot.log_message(guild, "ADMIN_LOG",
            user=self.bot.user, action="auto transformed",
            description=f"Direction: {before.title()} -> {after.title()}"
          )
          logger.debug(f"Finished Transforming in {guild.name} ({guild.id}).")
        except Exception as error:
          await self.bot.on_task_error("Cyra/Elara auto transformation", error, guild)

    @auto_transform.before_loop
    async def before_auto_transform():
        await self.bot.wait_until_ready()
        
    return auto_transform
      
  def get_auto_transform(self, guild):
    auto_transform = self.bot.get_setting(guild, "AUTO_TRANSFORM")
    if auto_transform == "ON":
      return True
    else:
      return False
      
  def get_random_trans_hero(self, old_hero):
    try:
      list_temp = self.transform_list.copy()
      list_temp.remove(old_hero)
    except:
      pass
    if not list_temp:
      raise ValueError("There is no candidate hero to transform to.")
    return random.choice(list_temp)
    

  @commands.group(
    name="transform",
    brief="Transforms to another form",
    cooldown_after_parsing=True,
    case_insensitive = True,
    invoke_without_command=True
  )
  @commands.is_owner()
  @commands.cooldown(1, 600, commands.BucketType.guild)
  async def _transform(self, context, hero:hero_and_secret=None, skin_num:int=None):
    before = self.bot.get_nick(context.guild).lower()
    if before == hero:
      await context.send(f"I'm currently {before.title()} so no need to transform.")
      return
    if hero is None:
      hero = self.get_random_trans_hero(before)
    after = hero
    await self.bot.transform(context.guild, after, skin=skin_num)
    if after == "cyra":
      await context.send(f"*{after.title()} has taken control back.*")
    elif after == "elara":
      await context.send(f"*{after.title()} is here to reap chaos.*")
    else:
      await context.send(f"*{after.title()} just landed on RD server.*")
    await self.bot.log_message(context.guild, "ADMIN_LOG",
      user=context.author, action="was transformed", target=self.bot.user,
      description=f"Direction: {before.title()} -> {after.title()}",
      timestamp=context.message.created_at
    )
      
  @_transform.command(
    name="list",
    brief="Shows list of auto transformation"
  )
  @commands.is_owner()
  async def _list_transform(self, context):
    await context.send(f"Below is the list of heroes that can be auto-transformed to:```\n" + 
                        "\n".join([hero.title() for hero in self.transform_list]) + "```")
        
  @_transform.command(
    name="add",
    brief="Adds a hero to auto transformation"
  )
  @commands.is_owner()
  async def _add_transform(self, context, heroes:commands.Greedy[hero_and_secret]):
    added_heroes = []
    for hero in heroes:
      if hero not in self.transform_list:
        self.transform_list.append(hero)
        added_heroes.append(hero)
    if added_heroes:
      await context.send(f"Heroes added to the auto transformation:```\n" + 
                          "\n".join([hero.title() for hero in added_heroes]) + "```")
    else:
      await context.send(f"No heroes added to the auto transformation.")
        
  @_transform.command(
    name="remove",
    brief="Removes a hero to auto transformation",
    aliases=["rm"]
  )
  @commands.is_owner()
  async def _rm_transform(self, context, heroes:commands.Greedy[hero_and_secret]):
    removed_heroes = []
    msg = ""
    for hero in heroes:
      if hero in self.transform_list:
        if len(self.transform_list) <= 2:
          msg += f"Warning: Cannot remove {hero.title()} because the number of transformable heroes should be at least 2.\n"
          continue
        self.transform_list.remove(hero)
        removed_heroes.append(hero)
    if removed_heroes:
      msg += f"Heroes removed from the auto transformation:```\n" +  "\n".join([hero.title() for hero in removed_heroes]) + "```"
    else:
      msg += f"No heroes removed from the auto transformation."
    await context.send(msg)
    
  @_transform.command(
    name="time",
    brief="Sets auto transformation interval",
    aliases=["interval"]
  )
  @commands.is_owner()
  async def _time_transform(self, context, hours:float=None):
    if hours is None:
      await context.send(f"Current transform interval is: {self.transform_interval} hour(s).")
      return
    self.auto_transform.change_interval(hours=hours)
    self.transform_interval = hours
    await context.send(f"Transform interval is changed to {hours} hour(s), the interval will be applied after the current iteration is completed.")

def setup(bot):
  bot.add_cog(TransformationCog(bot))
  logging.info("Added transformation.")

