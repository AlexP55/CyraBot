from datetime import datetime
import discord
from discord.ext import commands, tasks
import time
import logging

logger = logging.getLogger(__name__)

class TransformationCog(commands.Cog, name="Transformation Commands"):
  def __init__(self, bot):
    self.bot = bot
    self.auto_transform.start()
    
  def cog_unload(self):
    self.auto_transform.cancel()
  
  @tasks.loop(hours=2)
  async def auto_transform(self):
    if self.auto_transform.current_loop == 0: # don't transform at the first time
      return
    for guild_id, db in self.bot.db.items():
      guild = discord.utils.get(self.bot.guilds, id=guild_id)
      if not self.get_auto_transform(guild):
        continue
      try:
        logger.debug(f"Transforming in {guild.name} ({guild.id}).")
        was_cyra = await self.bot.transform(guild)
        before, after = ("Cyra", "Elara") if was_cyra else ("Elara", "Cyra")
        await self.bot.log_message(guild, "ADMIN_LOG",
          user=self.bot.user, action="auto transformed",
          description=f"Direction: {before} -> {after}"
        )
        logger.debug(f"Finished Transforming in {guild.name} ({guild.id}).")
      except Exception as error:
        await self.bot.on_task_error("Cyra/Elara auto transformation", error, guild)

  #@auto_transform.error
  #async def auto_transform_error(self, error):
    #TODO: Add logging via logging module

  @auto_transform.before_loop
  async def before_auto_transform(self):
      await self.bot.wait_until_ready()
      
  def get_auto_transform(self, guild):
    auto_transform = self.bot.get_setting(guild, "AUTO_TRANSFORM")
    if auto_transform == "ON":
      return True
    else:
      return False

  @commands.command(
    name="transform",
    brief="Transforms to Cyra/Elara",
  )
  @commands.is_owner()
  @commands.cooldown(1, 600, commands.BucketType.guild)
  async def _transform(self, context):
    was_cyra = await self.bot.transform(context.guild)
    await context.send(f"*Elara is here to reap chaos.*" if was_cyra else f"*Cyra has taken control back.*")
    before, after = ("Cyra", "Elara") if was_cyra else ("Elara", "Cyra")
    await self.bot.log_message(context.guild, "ADMIN_LOG",
      user=context.author, action="was transformed", target=self.bot.user,
      description=f"Direction: {before} -> {after}",
      timestamp=context.message.created_at
    )
  @_transform.error
  async def _transform_error(self, context, error):
    if isinstance(error, commands.CommandOnCooldown):
      await context.send(f"Skill is on cooldown, please try again in {round(error.retry_after)}s.")
    elif isinstance(error, commands.CheckFailure):
      await context.send(f"Sorry {context.author.mention}, but you do not have permission to transform Cyra/Elara.")
    else:
      await context.send(f"Sorry {context.author.mention}, something unexpected happened during my transformation.")

def setup(bot):
  bot.add_cog(TransformationCog(bot))
  logging.info("Added transformation.")

