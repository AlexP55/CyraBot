import discord
from discord.ext import commands
import random
import customExceptions
import string

facts = [
  "The same buff will be replaced by a later one. Try stopping an enemy by a long stun, and attack it with heavy taiko, then it will wake up quickly.",
  "Hogan's pig Bacon can be slowed by a world-4 Time Construct when casting Battle Bacon (spinning axe); Azura's moon can be also slowed by a Time Construct when attacking it, though it has no effect to the damage.",
  "Koi's Waterfall spell has different cooldown in melee or not in melee. Try to keep him engaged for fast Waterfalls.",
  "Transform Koi right after he casts waterpond, then the waterponds will be as strong as waterfalls.",
  "Boomerang's right upgrade Sever Tendon is very useful. It not only slows enemies, but also doubles the attack speed and increases the damage.",
  "Bounce damage is relatively low in RD, because the damage source is the enemy from which the bounce occurs.",
  "Some towers including Pyromancer, Boomerang, and Blunderbuss have ghost units which consume the haste from Yan without any real effect. Move Yan away from them.",
  "There is a way for Yan to haste the tower unit without wasting the haste on the tower itself: Put Yan a little bit far away from the tower.",
  "Bunny Mama has very high HP, but she can still be killed, which requires heavy damage from tournament or high level RS. In contrast, Obsidian's rock buddies have nearly infinite HP.",
  "Some attacks are able to damage birds although they look like a ground attack. Try gathering birds with ground enemies by Narlax, and attack the group by Giant Caldera, the birds will be burned up.",
  "Bunny Mama always avoids a boss fight. Is she afraid?",
  "Lancelot's mind is not hasted with his body in a tower buff. He sometimes becomes clumsy and forgets to cast his passives.",
  "Fire spirits from Pyromancer are untargetable, but they can receive electric shield from Mana Blaster, letting them track and shock the enemies.",
  "Most of the spell cooldowns of a tower are reset to zero after upgrading.",
  "Leif's Sharpen Blade is more effective to the units with a low base damage and a high multiplier, such as towers in late worlds.",
  "Masamune and Maybn assassinate enemies. They will first engage with a stunned enemy when it's possible.",
  "Terrified enemies usually run back and don't engage in melee, but they will not ignore units like Connie's Bunny Mama, Maybn's bombs, Azura's charmed enemies.",
  "Allies have different ranges to engage in melee. Summons have the highest range, the second highest is from melee heroes and troops, and ranged heroes have the lowest.",
  "A multiplication buff to summons with inherited stats is not as strong as it looks. It only boosts stats except the inherited ones.",
  "Bosses are immune to most of the time buffs. Shamiko's Lovely Lullaby is the only buff to slow them.",
  "Dodge can avoid direct damage, but it can never avoid a buff or a percentage damage.",
  "Buffs to troop towers don't have any effect on their troops, not even on the respawn rate.",
  "Selling a tower returns 70% gold spent. Before calling the first wave this ratio is 100%, but rebuilding towers during this will not count towards achievements.",
  "Some of the charmed units including Mummy, Magic Book, Cloud Sunfish, Origami Crane and Harpy cannot engage in melee",
  "Don't use Shamiko's spell too fast. A unit will not receive a new buff if he/she already receive one in the last 6s even if it's a different buff."
]
facts.append(f"There are {len(facts)+1} random facts stored in this command. Did you find them all?")

elixir_cost_fee = [10,18,45,81,121,163,208,253,298,313,329,345,362,380,399,419,440,462,485,655,885,1194,1612,2177,2938,3967,5355,7230,9760,13176,17787,24013,32418,43764]
elixir_cost_lance = [0,36,65,117,210,378,380,382,384,404,423,444,466,490,514,540,567,595,625,844,1139,1537,2075,2802,3783,5106,6894,9307,12564,16961,22898,30912,41731,56337]
elixir_cost_1500 = [30,54,97,175,315,567,570,573,575,604,634,666,699,734,771,810,850,893,937,1265,1708,2306,3113,4203,5674,7660,10341,13960,18846,25442,34347,46368,62596,84505]
elixir_cost_3000 = [40,72,130,233,420,756,760,763,767,806,846,888,933,979,1028,1080,1134,1190,1250,1687,2278,3075,4151,5604,7565,10213,13787,18613,25128,33922,45795,61823,83462,112673]
elixir_cost_6000 = [50,90,162,292,525,945,950,954,959,1007,1057,1110,1166,1224,1285,1349,1417,1488,1562,2109,2847,3843,5189,7005,9456,12766,17234,23267,31410,42403,57244,77279,104327,140841]
elixir_cost_7500 = [60,108,194,350,630,1134,1139,1145,1151,1208,1269,1332,1399,1469,1542,1619,1700,1785,1875,2531,3416,4612,6226,8406,11348,15319,20681,27920,37691,50883,68693,92735,125192,169010]
elixir_cost_hero = {
  "fee":elixir_cost_fee,
  "lancelot":elixir_cost_lance,
  "smoulder":elixir_cost_3000,
  "efrigid":elixir_cost_3000,
  "hogan":elixir_cost_1500,
  "bolton":elixir_cost_1500,
  "obsidian":elixir_cost_3000,
  "masamune":elixir_cost_1500,
  "mabyn":elixir_cost_3000,
  "narlax":elixir_cost_7500,
  "sethos":elixir_cost_6000,
  "helios":elixir_cost_6000,
  "yan":elixir_cost_7500,
  "raida":elixir_cost_7500,
  "caldera":elixir_cost_7500,
  "leif":elixir_cost_7500,
  "koizuul":elixir_cost_7500,
  "azura":elixir_cost_7500,
  "normal connie":elixir_cost_1500,
  "connie":elixir_cost_1500,
  "shamiko":elixir_cost_7500,
  "cyra":elixir_cost_7500,
  "elara":elixir_cost_7500
}

class InfoCog(commands.Cog, name="Information Commands"):
  def __init__(self, bot):
    self.bot = bot
    
  async def cog_before_invoke(self, context):
    self.bot.is_willing_to_answer(context)
    
  async def cog_after_invoke(self, context):
    await self.bot.finish_info_command(context)

  #Default error handler for this cog, can be overwritten with a local error handler.
  async def cog_command_error(self, context, error):
    await self.bot.respond_to_error(context, error)
    
  @commands.command(
    brief="Info on GM title",
    description="Usage:",
    aliases=["grandmaster"],
  )
  async def gm(self, context):
    await context.send(
      f"Grandmaster is an in-game title. It can be obtained by the top 3 players in a legendary league tournament.\n\n"
      f"To request the Grandmaster role, post a picture of your in-game profile in {self.bot.get_channel(context.guild, name='role-claiming').mention}."
    )

  @commands.group(
    brief="Info on elixir",
    description="Usage:",
    case_insensitive = True,
    invoke_without_command=True,
    usage="[hero] [lvStart] [lvEnd]"
  )
  async def elixir(self, context, hero=None, lvStart=1, lvEnd=-1):
    if hero is None:
      await context.send(
        f"Elixir {self.bot.get_emoji(context.guild, 'elixir')} is a resource in Realm Defense.\n"
        f"It's main purpose is to level up your heroes.\n"
        f"It can be obtained from the Elixir Mine and as rewards from Mabyn's Wheel, Tournaments and Shattered Realms.\n"
        f"For info on the Elixir Mine, use the `?elixir mine` command.\n"
        f"To show the elixir cost for upgrading a hero, use `?elixir <hero> <lvStart> <lvEnd>`"
      )
      return
    hero = self.bot.find_hero(hero)
    if hero not in elixir_cost_hero:
      raise customExceptions.HeroNotFound(string.capwords(hero))
    if lvEnd <= lvStart:
      lvEnd = lvStart + 1
    if lvStart <= 0 or lvEnd > 35:
      await context.send(f"Level of {string.capwords(hero)} must be between 1 and 35.")
      return
    elixir_cost = sum(elixir_cost_hero[hero][lvStart-1:lvEnd-1])
    await context.send(
      f"Upgrading {string.capwords(hero)} from level {lvStart} to {lvEnd} costs:\n"
      f"{elixir_cost} {self.bot.get_emoji(context.guild, 'elixir')}"
    )

  @commands.command(
    brief="Info on Shattered Realms",
    description="Usage:"
  )
  async def srealm(self, context):
    await context.send(
      f"Shattered Realms is unlocked after level 31.\n"
      f"There are a total of 40 unique levels and you can play one level per day.\n"
      f"Each level rewards {self.bot.get_emoji(context.guild, 'elixir')}."
    )

  @commands.command(
    brief="Info on the Arcade",
    description="Usage:"
  )
  async def arcade(self, context):
    await context.send(
      f"Arcade is unlocked after level ?.\n"
      f"It has 5 unique mini-games you can play at 3 difficulties each.\n"
    )

  @commands.command(
    name="level",
    brief="Shows a selected level",
    description="Usage:",
    aliases=["lvl","lv"]
  )
  async def _level(self, context, level):
    result = self.bot.db[context.guild.id].select("levels", level)
    if result is None:
      raise customExceptions.DataNotFound("Level", level)
    if level[0] in ["s", "S"]:
      world = "Shattered Realms"
    else:
      try:
        level = int(level)
      except ValueError as err:
        raise commands.BadArgument(f"Could not find level {level}.")
      if 1 <= level <= 20:
        world = "World 1"
      elif 21 <= level <= 40:
        world = "World 2"
      elif 41 <= level <= 80:
        world = "World 3"
      elif 81 <= level <= 120:
        world = "World 4"
      elif 121 <= level <= 160:
        world = "World 5"
      elif 161 <= level <= 200:
        world = "World 6"
      #elif 201 <= level <= 240:
      #  world = "World 7
      else:
        raise commands.BadArgument("Invalid level for level command.")
    embed = discord.Embed(title=f"{level}. {result['name']}", colour=discord.Colour.green(), timestamp=context.message.created_at)
    if result["handicap"] != "NONE":
      embed.add_field(name="Legendary Handicap:", value=result["handicap"], inline=False)
    if result["tappable"] != "NONE":
      coin_emoji = self.bot.get_emoji(context.guild, "coin")
      if coin_emoji is not None:
        tappable = result["tappable"].replace(":moneybag:", f"{coin_emoji}")
      else:
        tappable = result["tappable"]
      embed.add_field(name="Tappable(s):", value=tappable, inline=False)
    if result["link"] != "NONE":
      embed.set_image(url=result["link"])
    embed.set_footer(text=world)
    await context.send(content=None, embed=embed)
    
  @commands.command(
    brief="Info on a world",
    description="Usage:",
    aliases=["w"]
  )
  async def world(self, context, num:int=None):
    if num is None:
      await context.send_help("world")
      return
    if num == 1:
      await context.send(
        f"World 1:\n"
        f"  Levels: 1 - 20\n"
        f"  Heroes: {self.bot.get_emoji(context.guild, 'fee')}{self.bot.get_emoji(context.guild, 'lancelot')}{self.bot.get_emoji(context.guild, 'smoulder')}"
        f"{self.bot.get_emoji(context.guild, 'efrigid')}{self.bot.get_emoji(context.guild, 'obsidian')}{self.bot.get_emoji(context.guild, 'mabyn')}"
        f"{self.bot.get_emoji(context.guild, 'masamune')}{self.bot.get_emoji(context.guild, 'normal connie')}{self.bot.get_emoji(context.guild, 'hogan')}\n"
        f"  Challenges: {self.bot.get_emoji(context.guild, 'smoulder')}{self.bot.get_emoji(context.guild, 'efrigid')}\n\n"
        f"Ask questions regarding any level in {self.bot.get_channel(context.guild, name='world-1').mention}."
      )
    elif num == 2:
      await context.send(
        f"World 2:\n"
        f"  Levels: 21 - 40\n"
        f"  Challenges: {self.bot.get_emoji(context.guild, 'obsidian')}{self.bot.get_emoji(context.guild, 'mabyn')}\n\n"
        f"Ask questions regarding any level in {self.bot.get_channel(context.guild, name='world-2').mention}."
      )
    elif num == 3:
      await context.send(
        f"World 3:\n"
        f"  Levels: 41 - 80\n"
        f"  Heroes: {self.bot.get_emoji(context.guild, 'helios')}{self.bot.get_emoji(context.guild, 'sethos')}\n"
        f"  Challenges: {self.bot.get_emoji(context.guild, 'helios')}{self.bot.get_emoji(context.guild, 'sethos')}\n\n"
        f"Ask questions regarding any level in {self.bot.get_channel(context.guild, name='world-3').mention}."
      )
    elif num == 4:
      await context.send(
        f"World 4:\n"
        f"  Levels: 81 - 120\n"
        f"  Heroes: {self.bot.get_emoji(context.guild, 'yan')}{self.bot.get_emoji(context.guild, 'narlax')}\n\n"
        f"Ask questions regarding any level in {self.bot.get_channel(context.guild, name='world-4').mention}."
      )
    elif num == 5:
      await context.send(
        f"World 5:\n"
        f"  Levels: 121 - 160\n"
        f"  Heroes: {self.bot.get_emoji(context.guild, 'leif')}{self.bot.get_emoji(context.guild, 'caldera')}\n\n"
        f"Ask questions regarding any level in {self.bot.get_channel(context.guild, name='world-5').mention}."
      )
    elif num == 6:
      await context.send(
        f"World 6:\n"
        f"  Levels: 161 - 200\n"
        f"  Heroes: {self.bot.get_emoji(context.guild, 'azura')}{self.bot.get_emoji(context.guild, 'raida')}{self.bot.get_emoji(context.guild, 'koizuul')}{self.bot.get_emoji(context.guild, 'shamiko')}\n"
        f"  Challenges: {self.bot.get_emoji(context.guild, 'shamiko')}, beat LV 200 + 3 Rank 6 Heroes\n\n"
        f"Ask questions regarding any level in {self.bot.get_channel(context.guild, name='world-6').mention}."
      )
    elif num == 7:
      await context.send(
        f"World 7:\n"
        f"  Levels: 201 - ???\n"
        f"  Heroes: {self.bot.get_emoji(context.guild, 'cyra')}{self.bot.get_emoji(context.guild, 'elara')}\n\n"
        f"Ask questions regarding any level in {self.bot.get_channel(context.guild, name='world-7').mention}."
      )
    else:
      raise customExceptions.DataNotFound("World", num)

  @commands.command(
    brief="Displays link to wiki",
    description="Usage:"
  )
  async def wiki(self, context):
#    await context.send(f"Wiki: https://realm-defense-hero-legends-td.fandom.com/wiki/Realm_Defense:_Hero_Legends_TD_Wiki")
    embed = discord.Embed(title="Realm Defense Wiki", url="https://realm-defense-hero-legends-td.fandom.com/wiki/Realm_Defense:_Hero_Legends_TD_Wiki",
                          description="The fandom wiki for Realm Defense.")
    embed.set_image(url="https://vignette.wikia.nocookie.net/realm-defense-hero-legends-td/images/2/27/RealmDefenseBanner.jpg/revision/latest?cb=20191107143646")
    await context.send(content=None, embed=embed)

  @elixir.command(
    brief="Info on elixir mine",
    description="Usage:"
  )
  async def mine(self, context):
    await context.send(
      f"Elixir Mine can be unlocked in World 1.\n"
      f"It has a total of 10 levels.\n"
      f"Level  1:    0 {self.bot.get_emoji(context.guild, 'gem')} (  5{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity:   40{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level  2:   50 {self.bot.get_emoji(context.guild, 'gem')} ( 15{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity:  120{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level  3:  300 {self.bot.get_emoji(context.guild, 'gem')} ( 30{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity:  240{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level  4:  600 {self.bot.get_emoji(context.guild, 'gem')} ( 45{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity:  360{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level  5: 1000 {self.bot.get_emoji(context.guild, 'gem')} ( 75{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity:  600{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level  6: 1500 {self.bot.get_emoji(context.guild, 'gem')} (105{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity:  840{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level  7: 2000 {self.bot.get_emoji(context.guild, 'gem')} (140{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity: 1260{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level  8: 2500 {self.bot.get_emoji(context.guild, 'gem')} (180{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity: 1620{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level  9: 4000 {self.bot.get_emoji(context.guild, 'gem')} (220{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity: 3520{self.bot.get_emoji(context.guild, 'elixir')})\n"
      f"Level 10: 6000 {self.bot.get_emoji(context.guild, 'gem')} (260{self.bot.get_emoji(context.guild, 'elixir')}/hour, Capacity: 6240{self.bot.get_emoji(context.guild, 'elixir')})"
    )

  @commands.command(
    brief="Info on ranks",
    description="Usage:",
    aliases=["ranks"]
  )
  async def rank(self, context):
    await context.send(
      f"Awakening Ranks:```"
      f"  Rank 0:   0 Tokens\n"
      f"  Rank 1:   5 Tokens\n"
      f"  Rank 2:  10 Tokens\n"
      f"  Rank 3:  15 Tokens\n"
      f"  Rank 4:  20 Tokens\n"
      f"  Rank 5:  40 Tokens\n"
      f"  Rank 6:  80 Tokens\n"
      f"  Rank 7: 100 Tokens```"
    )

  @commands.command(
    brief="Info on Realm Siege",
    description="Usage:",
    aliases=["rs"]
  )
  async def siege(self, context):
    await context.send(
      f"Realm Siege is unlocked after beating World 2.\n"
      f"Realm Siege Keys cost: 0, 0, 80, 80, 160, 160, 320 {self.bot.get_emoji(context.guild, 'gem')}\n"
      f"You can do up to 7 Realm Siege battles per day, which cost 800 {self.bot.get_emoji(context.guild, 'gem')}.\n"
      f"Increasing the difficulty will reward you with more Realm Siege Medals. You can get a maximum of 5 medals per battle."
      f"10 medals lets you open a chest that holds 50 gems.\n"
      f"You can store up to 10 Realm Siege Keys.\n"
      f"Tower slots can be blessed, which increases a tower's power relative to the difficulty."
    )

  @commands.group(
    brief="Info on leagues",
    description="Usage:",
    case_insensitive = True,
    invoke_without_command=True,
    aliases=["league"]
  )
  async def leagues(self, context):
    embed = discord.Embed(title="Tournament Leagues")
    embed.add_field(name="Bronze League:",   value="Top 3/15 promote to Silver League.",   inline=False)
    embed.add_field(name="Silver League:",   value="Top 3/15 promote to Gold League.",     inline=False)
    embed.add_field(name="Gold League:",     value="Top 3/20 promote to Platinum League.", inline=False)
    embed.add_field(name="Platinum League:", value="Top 3/25 promote to Diamond League.",  inline=False)
    embed.add_field(name="Diamond League:",  value="Top 5/30 promote to Master League.",   inline=False)
    embed.add_field(name="Master League:",   value="Top 5/30 promote to Legend League.",   inline=False)
    embed.add_field(name="Legend League:",   value="Top 3/50 earn a grandmaster title.",   inline=False)
    embed.add_field(name="For rewards:",   value="`?league reward <league>`",   inline=False)
    embed.set_footer(text="LEAGUES CARD")
    await context.send(content=None, embed=embed)
#    await context.send(
#      f"Bronze:   Top 3(of 15) promote\n"
#      f"Silver:   Top 3(of 15) promote\n"
#      f"Gold:     Top 3(of 20) promote\n"
#      f"Platinum: Top 3(of 25) promote\n"
#      f"Diamond:  Top 5(of 30) promote\n"
#      f"Master:   Top 5(of 30) promote\n"
#      f"Legend:   Top 3(of 50) earn GM"
#    )

  @leagues.command(
    name="reward",
    brief="Shows tournament rewards",
    description="Usage:",
    aliases=["rewards"],
    help='Shows tournament rewards of a league.\nSpecial thanks to NFdragon#7195 for collecting the data.',
  )
  async def league_reward(self, context, league=None):
    if league is None:
      await context.send_help("leagues reward")
      return
    guild = context.guild
    gem_emoji = self.bot.get_emoji(guild, "gem")
    if gem_emoji is None:
      gem_emoji = "__Gem__"
    elixir_emoji = self.bot.get_emoji(guild, "elixir")
    if elixir_emoji is None:
      elixir_emoji = "__Elixir__"
    medal_emoji = self.bot.get_emoji(guild, "medal")
    if medal_emoji is None:
      medal_emoji = "__Medal__"
    if league.lower() in ["bronze"]:
      league = "Bronze League"
      description = "Top 3 of 15 get promoted."
      rewards = {"1st place":f"140 {gem_emoji}, 700 {elixir_emoji}, 20 {medal_emoji}",
        "2nd place":f"120 {gem_emoji}, 500 {elixir_emoji}, 10 {medal_emoji}",
        "3rd place":f"100 {gem_emoji}, 300 {elixir_emoji}, 5 {medal_emoji}",
        "4th through 6th place":f"20 {gem_emoji}, 300 {elixir_emoji}, 3 {medal_emoji}",
        "7th through 10th place":f"10 {gem_emoji}, 100 {elixir_emoji}, 1 {medal_emoji}"}
      icon = discord.utils.get(guild.emojis, name="league_1_bronze")
    elif league.lower() in ["silver"]:
      league = "Silver League"
      description = "Top 3 of 15 get promoted."
      rewards = {"1st place":f"140 {gem_emoji}, 700 {elixir_emoji}, 30 {medal_emoji}",
        "2nd place":f"120 {gem_emoji}, 500 {elixir_emoji}, 20 {medal_emoji}",
        "3rd place":f"100 {gem_emoji}, 300 {elixir_emoji}, 10 {medal_emoji}",
        "4th through 6th place":f"20 {gem_emoji}, 300 {elixir_emoji}, 5 {medal_emoji}",
        "7th through 10th place":f"15 {gem_emoji}, 100 {elixir_emoji}, 3 {medal_emoji}"}
      icon = discord.utils.get(guild.emojis, name="league_2_silver")
    elif league.lower() in ["gold"]:
      league = "Gold League"
      description = "Top 3 of 20 get promoted."
      rewards = {"1st place":f"190 {gem_emoji}, 1200 {elixir_emoji}, 40 {medal_emoji}",
        "2nd place":f"170 {gem_emoji}, 1000 {elixir_emoji}, 30 {medal_emoji}",
        "3rd place":f"150 {gem_emoji}, 800 {elixir_emoji}, 20 {medal_emoji}",
        "4th through 6th place":f"30 {gem_emoji}, 800 {elixir_emoji}, 10 {medal_emoji}",
        "7th through 10th place":f"20 {gem_emoji}, 400 {elixir_emoji}, 5 {medal_emoji}"}
      icon = discord.utils.get(guild.emojis, name="league_3_gold")
    elif league.lower() in ["platinum","plat"]:
      league = "Platinum League"
      description = "Top 3 of 25 get promoted."
      rewards = {"1st place":f"300 {gem_emoji}, 1200 {elixir_emoji}, 50 {medal_emoji}",
        "2nd place":f"250 {gem_emoji}, 1000 {elixir_emoji}, 40 {medal_emoji}",
        "3rd place":f"200 {gem_emoji}, 800 {elixir_emoji}, 30 {medal_emoji}",
        "4th through 6th place":f"30 {gem_emoji}, 800 {elixir_emoji}, 15 {medal_emoji}",
        "7th through 10th place":f"20 {gem_emoji}, 400 {elixir_emoji}, 10 {medal_emoji}"}
      icon = discord.utils.get(guild.emojis, name="league_4_platinum")
    elif league.lower() in ["diamond", "dia"]:
      league = "Diamond League"
      description = "Top 5 of 30 get promoted."
      rewards = {"1st place":f"300 {gem_emoji}, 1200 {elixir_emoji}, 75 {medal_emoji}",
        "2nd and 3rd place":f"250 {gem_emoji}, 1000 {elixir_emoji}, 60 {medal_emoji}",
        "4th and 5th place":f"200 {gem_emoji}, 800 {elixir_emoji}, 50 {medal_emoji}",
        "6th through 10th place":f"40 {gem_emoji}, 800 {elixir_emoji}, 25 {medal_emoji}",
        "11th through 15th place":f"25 {gem_emoji}, 400 {elixir_emoji}, 15 {medal_emoji}"}
      icon = discord.utils.get(guild.emojis, name="league_5_diamond")
    elif league.lower() in ["master"]:
      league = "Master League"
      description = "Top 5 of 30 get promoted."
      rewards = {"1st place":f"300 {gem_emoji}, 1200 {elixir_emoji}, 100 {medal_emoji}",
        "2nd and 3rd place":f"250 {gem_emoji}, 1000 {elixir_emoji}, 90 {medal_emoji}",
        "4th and 5th place":f"200 {gem_emoji}, 800 {elixir_emoji}, 80 {medal_emoji}",
        "6th through 10th place":f"40 {gem_emoji}, 800 {elixir_emoji}, 40 {medal_emoji}",
        "11th through 15th place":f"25 {gem_emoji}, 400 {elixir_emoji}, 20 {medal_emoji}"}
      icon = discord.utils.get(guild.emojis, name="league_6_master")
    elif league.lower() in ["legend", "legendary"]:
      league = "Legendary League"
      description = "Top 3 of 50 get Grandmaster title."
      rewards = {"1st place":f"500 {gem_emoji}, 3000 {elixir_emoji}, 500 {medal_emoji}",
        "2nd place":f"400 {gem_emoji}, 2500 {elixir_emoji}, 400 {medal_emoji}",
        "3rd place":f"300 {gem_emoji}, 2000 {elixir_emoji}, 300 {medal_emoji}",
        "4th through 6th place":f"50 {gem_emoji}, 2000 {elixir_emoji}, 80 {medal_emoji}",
        "7th through 10th place":f"30 {gem_emoji}, 1000 {elixir_emoji}, 40 {medal_emoji}",
        "11th through 25th place":f"20 {gem_emoji}, 400 {elixir_emoji}, 5 {medal_emoji}"}
      icon = discord.utils.get(guild.emojis, name="league_7_legendary")
    else:
      await context.send(f"There is no league called {league}.")
      return
    embed = discord.Embed(title=league, description=description)
    for position, reward in rewards.items():
      embed.add_field(name=f"{position}:", value=f"{reward}", inline=False)
    if icon is not None:
      embed.set_footer(text="LEAGUE REWARDS", icon_url=icon.url)
    else:
      embed.set_footer(text="LEAGUE REWARDS")
    await context.send(content=None, embed=embed)

  @commands.group(
    name="event",
    brief="Shows info on events",
    description="Usage:",
    case_insensitive = True,
    invoke_without_command=True
  )
  async def _event(self, context):
    await context.send_help("event")
  
  @_event.command(
    name="info",
    brief="Shows info on events",
    description="Usage:"
  )
  async def eventinfo(self, context):
    await context.send(
      f"Events last 2 weeks. During an event you can collect tokens from a special Realm Siege Level to forge boxes. "
      f"The boxes have awakening tokens for the new hero. A box needs 35 event tokens. You can buy a box for 800{self.bot.get_emoji(context.guild, 'gem')} or 10 boxes for 7500{self.bot.get_emoji(context.guild, 'gem')}. "
      f"After the first week the Realm Siege Level will become unavailable but you still have the option to buy event tokens(and therfore boxes).\n"
      f"After an event the awakening tokens for the new hero will be unavailable for some time."
    )
    
  @_event.command(
    name="rmb",
    brief="Shows info on the event bundle",
    description="Usage:"
  )
  async def eventbundle(self, context):
    await context.send(
      f"The RMB(Real Money Bundle) can be bought twice. Each gives 10 awakening tokens, 800 {self.bot.get_emoji(context.guild, 'gem')} and 5 boxes in event tokens. "
      f"The RMB provides the best value for your money in an event."
    )

  @_event.command(
    name="rewards",
    brief="Shows info on the event rewards",
    description="Usage:"
  )
  async def eventrewards(self, context):
    await context.send(
      f"Event Rewards:\n"
      f"  Silver I: 2 Boxes in form of event tokens\n"
      f"  Silver II: New Hero\n"
      f"  Gold I: 5000 {self.bot.get_emoji(context.guild, 'elixir')}\n"
      f"  Gold II: 30 Awakening Tokens*\n"
      f"  Gold III: an exclusive event skin\n"
      f"  Platinum: an exclusive event skin\n\n"
      f"* You get the tokens for the hero which is closest to Platinum rank. "
      f"You need to have less than 140 total awakening tokens (50 if you have Gold III rank) for the hero. "
      f"Additionally not all awakening tokens are available - probably only the tokens you can get from a box."
    )
    
  @commands.group(
    name="rand",
    brief="Shows some random things",
    description="Usage:",
    aliases=["random"],
    case_insensitive = True,
    invoke_without_command=True
  )
  async def _rand(self, context):
    await context.send_help("rand")
    
  @_rand.command(
    name="fact",
    brief="Gets a random fact",
    description="Usage:"
  )
  @commands.cooldown(1, 30, commands.BucketType.user)
  async def randfact(self, context):
    await context.send(
      f"{random.choice(facts)}"
    )

  @_rand.command(
    brief="Gets a random quote",
    description="Usage:"
  )
  @commands.cooldown(1, 15, commands.BucketType.user)
  async def quote(self, context):
    result = self.bot.db[context.guild.id].query(f"SELECT * FROM quotes ORDER BY random() LIMIT 1")
    quote = result[0][2]
    hero = result[0][1]
    await context.send(
      f'"{quote}"\n\n'
      f'                  -*{hero}*'
    )
    
def setup(bot):
  bot.add_cog(InfoCog(bot))
  print("Added information cog.")
