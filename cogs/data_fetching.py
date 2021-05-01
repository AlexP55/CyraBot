import discord
from discord.ext import commands
from base.modules.access_checks import has_admin_role
from modules.custom_exceptions import DataNotFound
import xlrd
from base.modules.constants import DB_PATH as path
from modules.cyra_constants import achievements, achievemets_dict
from modules.level_parser import parse_achievements, is_boss_level
import os
import json
import logging

logger = logging.getLogger(__name__)

class SheetReader:
  def __init__(self, db, file_name="db.xlsx"):
    self.db = db
    self.book = xlrd.open_workbook(f"{path}/{file_name}")

  def fetchHero(self):
    sheet = self.book.sheet_by_name("hero")
    if sheet is None:
      logging.warning("Warning, no hero sheet found")
      return
    expected = 25
    if not sheet.ncols == expected:
      raise Exception(f"Levels sheet columns do not match, expected {expected} but found {sheet.ncols}")
    self.db.delete_table("hero")
    self.db.create_table("hero", "name", name="txt", world="int", baseHP="int", drankHP="int", dlvHP="int", dranklvHP="int",
                    baseND="int", drankND="int", dlvND="int", dranklvND="int", baseSD="int", drankSD="int", dlvSD="int", dranklvSD="int",
                    basePhysicalArmor="real", drankPhysicalArmor="real", MagicalArmor="real", Shield="int", MoveSpeed="real", Dodge="int", 
                    ReviveTime="int", minRank="int", maxRank="int", introduction="txt", link="txt")
    self.insertSheet(sheet, "hero")

  def fetchAbility(self):
    sheet = self.book.sheet_by_name("ability")
    if sheet is None:
      logging.warning("Warning, no ability sheet found")
      return
    expected = 9
    if not sheet.ncols == expected:
      raise Exception(f"Levels sheet columns do not match, expected {expected} but found {sheet.ncols}")
    self.db.delete_table("ability")
    self.db.create_table("ability", ["ability", "hero"], ability="txt_not_null", hero="txt_not_null", type="txt_not_null", unlock="txt_not_null",
                    shortDescription="txt_not_null", addition="txt_not_null", tag="int_not_null", keyword="txt_not_null", url="txt_not_null")
    self.insertSheet(sheet, "ability")

  def fetchAbilityDetail(self):
    sheet = self.book.sheet_by_name("abilityDetail")
    if sheet is None:
      logging.warning("Warning, no abilityDetail sheet found")
      return
    expected = 4
    if not sheet.ncols == expected:
      raise Exception(f"Levels sheet columns do not match, expected {expected} but found {sheet.ncols}")
    self.db.delete_table("abilityDetail")
    self.db.create_table("abilityDetail", ["ability", "hero", "upgrade"],  ability="txt_not_null", hero="txt_not_null",
                    upgrade="txt_not_null", info="txt_not_null")
    self.insertSheet(sheet, "abilityDetail")

  def fetchLevels(self):
    sheet = self.book.sheet_by_name("levels")
    if sheet is None:
      logging.warning("Warning, no levels sheet found")
      return
    expected = 8
    if not sheet.ncols == expected:
      raise Exception(f"Levels sheet columns do not match, expected {expected} but found {sheet.ncols}")
    self.db.delete_table("levels")
    self.db.create_table("levels", "level", level="txt", world="int", name="txt", handicap="txt", task="txt", tappable="txt", link="txt", remark="txt")
    self.insertSheet(sheet, "levels")

  def fetchQuotes(self):
    sheet = self.book.sheet_by_name("quotes")
    if sheet is None:
      logging.warning("Warning, no quotes sheet found")
      return
    expected = 3
    if not sheet.ncols == expected:
      raise Exception(f"Levels sheet columns do not match, expected {expected} but found {sheet.ncols}")
    self.db.delete_table("quotes")
    self.db.create_table("quotes", "id", id="int", hero="txt", quote="txt")
    self.insertSheet(sheet, "quotes")
    
  def fetchEnemy(self):
    sheet = self.book.sheet_by_name("enemy")
    if sheet is None:
      logging.warning("Warning, no enemy sheet found")
      return
    expected = 14
    if not sheet.ncols == expected:
      raise Exception(f"Levels sheet columns do not match, expected {expected} but found {sheet.ncols}")
    self.db.delete_table("enemy")
    self.db.create_table("enemy", ["enemy", "world"], enemy="txt", world="int", type="txt", hp="int", physicalArmor="real", magicalArmor="real", moveSpeed="real", castSpeed="real", normalDamage="int", specialDamage="int", dodge="int", abilities="txt", remark="txt", url="txt")
    self.insertSheet(sheet, "enemy")
    
  def fetchTower(self):
    sheet = self.book.sheet_by_name("tower")
    if sheet is None:
      logging.warning("Warning, no tower sheet found")
      return
    expected = 14
    if not sheet.ncols == expected:
      raise Exception(f"Levels sheet columns do not match, expected {expected} but found {sheet.ncols}")
    self.db.delete_table("tower")
    self.db.create_table("tower", ["tower", "world"], tower="txt", world="int", type="txt", description1="txt", description2="txt", basic="txt", starUpgrade="txt", lvUpgrade="txt", leftBranchName="txt", leftBranch="txt", rightBranchName="txt", rightBranch="txt", reinforcement="txt", url="txt")
    self.insertSheet(sheet, "tower")
    
  def fetchBuff(self):
    sheet = self.book.sheet_by_name("buff")
    if sheet is None:
      logging.warning("Warning, no buff sheet found")
      return
    expected = 3
    if not sheet.ncols == expected:
      raise Exception(f"Levels sheet columns do not match, expected {expected} but found {sheet.ncols}")
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
      await context.send(f"Sorry {context.author.mention}, but only {error.number} user(s) per guild can execute `{context.command.qualified_name}` at the same time!")
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
    await context.send(f"```Fetching wave and achievement data...```")
    self.update_wave_achievement(context)
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "all tables")

  @_fetch.command(
    name="hero",
    brief="Fetch hero table",
    aliases=["heroes"]
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
    aliases=["abilities"]
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
    aliases=["abilityDetails"]
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
    name="level",
    brief="Fetch levels table",
    aliases=["levels"]
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
    name="quote",
    brief="Fetch quotes table",
    aliases=["quotes"]
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
    aliases=["enemies"]
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
    aliases=["towers"]
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
    aliases=["buffs"]
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_buff(self, context):
    reader = SheetReader(self.bot.db[context.guild.id])
    await context.send(f"```Fetching buff data...```")
    reader.fetchBuff()
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "buff")
    
  @_fetch.command(
    name="wave",
    brief="Fetch wave table",
    aliases=["waves, achievement, achievements"]
  )
  @commands.max_concurrency(1, commands.BucketType.guild)
  @has_admin_role()
  async def _fetch_wave(self, context):
    await context.send(f"```Fetching wave and achievement data...```")
    self.update_wave_achievement(context)
    await context.send(f"```Completed```")
    await self.send_fetch_log(context, "wave")
      
  async def send_fetch_log(self, context, sheetname):
    await self.bot.log_message(context.guild, "ADMIN_LOG", 
      user=context.author, action="updated a table",
      description=f"**Table:** {sheetname}", timestamp=context.message.created_at
    )
  
  def update_wave_achievement(self, context):
    db = self.bot.db[context.guild.id]
    db.delete_table("wave")
    db.create_table("wave", ["level", "mode"], level="txt", mode="txt", initial_gold="int", max_life="int", enemy_waves="txt")
    db.delete_table("achievement")
    achievement_columns = {achievement:"int" for achievement in achievements}
    db.create_table("achievement", ["level", "mode", "strategy"], level="txt", mode="txt", strategy="txt", time="real", gold="int", wave="int", **achievement_columns)
    directory = os.path.join(path, 'levels/')
    data = sorted(os.listdir(directory))
    for name in data:
      if not name.endswith(".txt"):
        continue
      try:
        with open(os.path.join(directory, name), "r") as f:
          parsed_level = json.load(f)
            
          # get level info
          lvname = name[:-4]
          name_split = lvname.split("_", 1)
          level = name_split[0]
          if len(name_split) > 1:
            mode = name_split[1]
          else:
            mode = ""
          result = db.select("levels", level)
          remark = result["remark"] if result else ""
          task = result["task"] if result else ""
          wave_num = len(parsed_level["enemy_waves"])
          
          # parse achievements info
          achieve_info = []
          if is_boss_level(level, mode, remark):
            # boss level, can skip the last wave by instantly killing the boss
            strategy = "Play as long as you can without killing the boss"
            time, achievement_count, gold = parse_achievements(parsed_level["enemy_waves"])
            achieve_info.append([strategy, time, gold+parsed_level["initial_gold"], achievement_count])
            if level not in ["180"]: # Raijin boss level is not skippable because of damage immunity
              strategy = "Kill the boss as fast as you can"
              time, achievement_count, gold = parse_achievements(parsed_level["enemy_waves"][:-1])
              achieve_info.append([strategy, time, gold+parsed_level["initial_gold"], achievement_count])
          elif remark == "boss rush": # SR boss levels, you can choose to skip waves
            for ind in range(0, 2**wave_num):
              valid_waves = [int(d) for d in bin(ind)[2:].zfill(wave_num)] # a list of 0's and 1's, indicating skip wave or not
              skipped_waves = []
              waves_info = []
              last_wave = -1
              for i in range(len(valid_waves)):
                if valid_waves[i]==0:
                  skipped_waves.append(str(i+1))
                else:
                  waves_info.append(parsed_level["enemy_waves"][i])
                  last_wave = i
              gold_valid = sum([parsed_level["enemy_waves"][i]["reward"] for i in range(last_wave)])
              if skipped_waves:
                strategy = f"Kill boss(es) in wave {', '.join(skipped_waves)} as fast as you can" 
              else:
                strategy = "Play as long as you can without killing the bosses"
              time, achievement_count, _ = parse_achievements(waves_info)
              achieve_info.append([strategy, time, gold_valid+parsed_level["initial_gold"], achievement_count])
          else:
            if level.startswith("A5-"):
              # these levels can be run as long as possible
              strategy = "Play as long as you can"
            else:
              strategy = "Kill all enemies as fast as you can"
            time, achievement_count, gold = parse_achievements(parsed_level["enemy_waves"])
            achieve_info.append([strategy, time, gold+parsed_level["initial_gold"], achievement_count])
            
          for strategy, time, gold, achievement_count in achieve_info:
            if mode == "campaign":
              if task == "bandit":
                achievement_count["bandit"] = 1
              elif task == "villager":
                achievement_count["villager"] = 1
            db.insert_or_update("achievement", level, mode, strategy, time, gold, wave_num, *achievement_count.values())
          
          parsed_level["enemy_waves"] = json.dumps(parsed_level["enemy_waves"])
          db.insert_or_update("wave", level, mode, *parsed_level.values())
      except Exception as e:
        logging.error(f"Error while reading wave data in file {name}.")
        raise e
        


#This function is needed for the load_extension routine.
def setup(bot):
  bot.add_cog(FetchCog(bot))
  logging.info("Added data fetching cog.")
