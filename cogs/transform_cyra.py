from datetime import datetime
import discord
from discord.ext import commands, tasks
import time

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
        was_cyra = await self.bot.transform(guild)
        title = "Cyra/Elara Auto-Transformed"
        fields = {"Direction":"Cyra transforms to Elara" if was_cyra else "Elara transforms to Cyra"}
        await self.bot.log_admin(guild, title=title, fields=fields)
      except Exception as error:
        await self.bot.on_task_error("Cyra/Elara auto transformation", error, guild)

  @auto_transform.before_loop
  async def before_auto_transform(self):
      await self.bot.wait_until_ready()
      
  def get_auto_transform(self, guild):
    auto_transform = self.bot.get_setting(guild, "AUTO_TRANSFORM")
    if auto_transform == "ON":
      return True
    else:
      return False

  @commands.group(
    name="transform",
    brief="Transforms to Cyra/Elara",
    case_insensitive = True,
    invoke_without_command=True
  )
  @commands.is_owner()
  @commands.cooldown(1, 600, commands.BucketType.guild)
  async def _transform(self, context):
    was_cyra = await self.bot.transform(context.guild)
    await context.send(f"*Elara is here to reap chaos.*" if was_cyra else f"*Cyra has taken control back.*")
    title = "User Transformed Cyra/Elara"
    fields = {"User":f"{context.author.mention}\n{context.author}",
              "Direction":"Cyra transforms to Elara" if was_cyra else "Elara transforms to Cyra"}
    await self.bot.log_admin(context.guild, title=title, fields=fields, timestamp=context.message.created_at)
  @_transform.error
  async def _transform_error(self, context, error):
    if isinstance(error, commands.CommandOnCooldown):
      await context.send(f"Skill is on cooldown, please try again in {round(error.retry_after)}s.")
    elif isinstance(error, commands.CheckFailure):
      await context.send(f"Sorry {context.author.mention}, but you do not have permission to transform Cyra/Elara.")
    else:
      await context.send(f"Sorry {context.author.mention}, something unexpected happened during my transformation.")
      
  @_transform.command(
    name="energy",
    brief="Shows the energy stored",
  )
  @commands.is_owner()
  async def _energy(self, context):
    await context.send(f"```Energy points stored: {self.bot.energy[context.guild.id]}```")
  @_energy.error
  async def _energy_error(self, context, error):
    await context.send(f"Sorry {context.author.mention}, something unexpected happened when looking for energy points.")
    
  @_transform.command(
    name="time",
    brief="Shows the last transform time",
  )
  @commands.is_owner()
  async def _trans_time(self, context):
    last_time = self.bot.last_transform[context.guild.id]
    await context.send(f"```Last transform/reboot time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.bot.last_transform[context.guild.id]))} UTC```")
  @_trans_time.error
  async def _trans_time_error(self, context, error):
    await context.send(f"Sorry {context.author.mention}, something unexpected happened when looking for the last transform time.")

def setup(bot):
  bot.add_cog(TransformationCog(bot))
  print("Added transformation.")

