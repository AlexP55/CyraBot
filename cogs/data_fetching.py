import discord
from discord.ext import commands
from base.modules.access_checks import has_admin_role
import xlrd
from base.modules.constants import DB_PATH as path

class SheetReader:
  def __init__(self, db, file_name="db.xlsx"):
    self.db = db
    self.book = xlrd.open_workbook(f"{path}/{file_name}")

  def fetchHero(self):
    sheet = self.book.sheet_by_name("hero")
    if sheet is None:
      print("Warning, no hero sheet found")
      return
    if not sheet.ncols == 24:
      raise Exception("Hero sheet columns do not match")
    self.db.delete_table("hero")
    self.db.create_table("hero", "name", name="txt", world="int", baseHP="int", drankHP="int", dlvHP="int", dranklvHP="int",
                    baseND="int", drankND="int", dlvND="int", dranklvND="int", baseSD="int", drankSD="int", dlvSD="int", dranklvSD="int",
                    baseArmor="real", drankArmor="real", Shield="int", MoveSpeed="real", Dodge="int", ReviveTime="int", minRank="int", maxRank="int", 
                    introduction="txt", link="txt")
    self.insertSheet(sheet, "hero")

  def fetchAbility(self):
    sheet = self.book.sheet_by_name("ability")
    if sheet is None:
      print("Warning, no ability sheet found")
      return
    if not sheet.ncols == 9:
      raise Exception("Ability sheet columns do not match")
    self.db.delete_table("ability")
    self.db.create_table("ability", ["ability", "hero"], ability="txt_not_null", hero="txt_not_null", type="txt_not_null", unlock="txt_not_null",
                    shortDescription="txt_not_null", addition="txt_not_null", tag="int_not_null", keyword="txt_not_null", url="txt_not_null")
    self.insertSheet(sheet, "ability")

  def fetchAbilityDetail(self):
    sheet = self.book.sheet_by_name("abilityDetail")
    if sheet is None:
      print("Warning, no abilityDetail sheet found")
      return
    if not sheet.ncols == 4:
      raise Exception("AbilityDetail sheet columns do not match")
    self.db.delete_table("abilityDetail")
    self.db.create_table("abilityDetail", ["ability", "hero", "upgrade"],  ability="txt_not_null", hero="txt_not_null",
                    upgrade="txt_not_null", info="txt_not_null")
    self.insertSheet(sheet, "abilityDetail")

  def fetchLevels(self):
    sheet = self.book.sheet_by_name("levels")
    if sheet is None:
      print("Warning, no levels sheet found")
      return
    if not sheet.ncols == 5:
      raise Exception("Levels sheet columns do not match")
    self.db.delete_table("levels")
    self.db.create_table("levels", "level", level="txt", name="txt", handicap="txt", tappable="txt", link="txt")
    self.insertSheet(sheet, "levels")

  def fetchQuotes(self):
    sheet = self.book.sheet_by_name("quotes")
    if sheet is None:
      print("Warning, no quotes sheet found")
      return
    if not sheet.ncols == 3:
      raise Exception("Quotes sheet columns do not match")
    self.db.delete_table("quotes")
    self.db.create_table("quotes", "id", id="int", hero="txt", quote="txt")
    self.insertSheet(sheet, "quotes")
    
  def fetchEnemy(self):
    sheet = self.book.sheet_by_name("enemy")
    if sheet is None:
      print("Warning, no enemy sheet found")
      return
    if not sheet.ncols == 14:
      raise Exception("Enemy sheet columns do not match")
    self.db.delete_table("enemy")
    self.db.create_table("enemy", ["enemy", "world"], enemy="txt", world="int", type="txt", hp="int", physicalArmor="real", magicalArmor="real", moveSpeed="real", castSpeed="real", normalDamage="int", specialDamage="int", dodge="int", abilities="txt", remark="txt", url="txt")
    self.insertSheet(sheet, "enemy")
    
  def fetchTower(self):
    sheet = self.book.sheet_by_name("tower")
    if sheet is None:
      print("Warning, no tower sheet found")
      return
    if not sheet.ncols == 14:
      raise Exception("Tower sheet columns do not match")
    self.db.delete_table("tower")
    self.db.create_table("tower", ["tower", "world"], tower="txt", world="int", type="txt", description1="txt", description2="txt", basic="txt", starUpgrade="txt", lvUpgrade="txt", leftBranchName="txt", leftBranch="txt", rightBranchName="txt", rightBranch="txt", reinforcement="txt", url="txt")
    self.insertSheet(sheet, "tower")
    
  def fetchBuff(self):
    sheet = self.book.sheet_by_name("buff")
    if sheet is None:
      print("Warning, no buff sheet found")
      return
    if not sheet.ncols == 3:
      raise Exception("Buff sheet columns do not match")
    self.db.delete_table("buff")
    self.db.create_table("buff", ["world", "unit"], world="int", unit="txt", buff="txt")
    self.insertSheet(sheet, "buff")

  def insertSheet(self, sheet, table):
    for rowx in range(1, sheet.nrows):
      # ignore the first row:
      tup = self.tupleFromRow(sheet, rowx)
      if tup is None:
        continue
      self.db.insert_or_update(table, *tup)

  def tupleFromRow(self, sheet, rowx):
    if sheet.cell_type(rowx, 0) == xlrd.XL_CELL_EMPTY:
      return None
    cellList = []
    for colx in range(sheet.ncols):
      if sheet.cell_type(rowx, colx) == xlrd.XL_CELL_EMPTY:
        # empty cell to empty string
        cellList.append("")
      elif sheet.cell_type(rowx, colx) == xlrd.XL_CELL_NUMBER:
        # number, do nothing
        cellList.append(sheet.cell_value(rowx, colx))
      else:
        # text, strip
        cellList.append(f"{sheet.cell_value(rowx, colx).strip()}")
    return cellList

# An extension for data fetching commands.
class FetchCog(commands.Cog, name="Data Fetching Commands"):
  def __init__(self, bot):
    self.bot = bot
    
  async def cog_command_error(self, context, error):
    if hasattr(context.command, "on_error"):
      # This prevents any commands with local handlers being handled here.
      return
    if isinstance(error, commands.CheckFailure):
      await context.send(f"Sorry {context.author.mention}, but you do not have permission to fetch data.")
    elif isinstance(error, commands.MaxConcurrencyReached):
      await context.send(f"Sorry {context.author.mention}, but only {error.number} user(s) per guild can execute `{context.prefix}{context.command.qualified_name}` at the same time!")
    else:
      await context.send(f"Sorry {context.author.mention}, something unexpected happened while fetching data.")

  @commands.group(
    name="fetch",
    brief="Update table(s) in DB",
    case_insensitive = True,
    invoke_without_command=True
  )
  @has_admin_role()
  async def _fetch(self, context):
    await context.send_help("fetch")
  
  @_fetch.command(
    name="all",
    brief="Fetch all tables from exel sheet",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_all(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching hero data...```")
    reader.fetchHero()
    await context.send(f"```Fetching ability data...```")
    reader.fetchAbility()
    await context.send(f"```Fetching abilityDetail data...```")
    reader.fetchAbilityDetail()
    await context.send(f"```Fetching enemy data...```")
    reader.fetchEnemy()
    await context.send(f"```Fetching tower data...```")
    reader.fetchTower()
    await context.send(f"```Fetching levels data...```")
    reader.fetchLevels()
    await context.send(f"```Fetching buff data...```")
    reader.fetchBuff()
    await context.send(f"```Fetching quotes data...```")
    reader.fetchQuotes()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "all tables")

  @_fetch.command(
    name="hero",
    brief="Fetch hero table",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_hero(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching hero data...```")
    reader.fetchHero()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "hero")

  @_fetch.command(
    name="ability",
    brief="Fetch ability table",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_ability(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching ability data...```")
    reader.fetchAbility()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "ability")

  @_fetch.command(
    name="abilityDetail",
    brief="Fetch abilityDetail table",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_abilitydetail(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching abilityDetail data...```")
    reader.fetchAbilityDetail()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "abilityDetail")

  @_fetch.command(
    name="levels",
    brief="Fetch levels table",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_levels(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching levels data...```")
    reader.fetchLevels()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "levels")

  @_fetch.command(
    name="quotes",
    brief="Fetch quotes table",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_quotes(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching quotes data...```")
    reader.fetchQuotes()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "quotes")
    
  @_fetch.command(
    name="enemy",
    brief="Fetch enemy table",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_enemy(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching enemy data...```")
    reader.fetchEnemy()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "enemy")
    
  @_fetch.command(
    name="tower",
    brief="Fetch tower table",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_tower(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching tower data...```")
    reader.fetchTower()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "tower")
    
  @_fetch.command(
    name="buff",
    brief="Fetch buff table",
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_buff(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching buff data...```")
    reader.fetchBuff()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "buff")
      
  async def send_fetch_log(self, context, sheetname):
    await self.bot.log_message(context.guild, "ADMIN_LOG", 
      user=context.author, action="updated a table",
      description=f"**Table:** {sheetname}", timestamp=context.message.created_at
    )

#This function is needed for the load_extension routine.
def setup(bot):
  bot.add_cog(FetchCog(bot))
  print("Added data fetching cog.")
