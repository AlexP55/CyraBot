import discord
import string
from base.modules.interactive_message import InteractiveMessage
from modules.stats import HeroStats
from modules.cyra_constants import hero_transformable, max_level, elixir_cost, token_cost
from base.modules.constants import arrow_emojis
from datetime import datetime

def rankup_cost_msg(context, hero, ranklow, rankhigh):
  token = context.bot.get_emoji(context.guild, hero)
  if token is None:
    token = "🧩"
  return f"{token} Tokens: {token_cost(ranklow, rankhigh)}"
  
def lvlup_cost_msg(context, hero, lvlow, lvhigh):
  elixir = context.bot.get_emoji(context.guild, "elixir")
  if elixir is None:
    elixir = "🧪"
  return f"{elixir} Elixirs: {elixir_cost(hero, lvlow, lvhigh)}"

class StatsMessage(InteractiveMessage):
  def __init__(self, hero, rank, level, dbrow, transform=False, **attributes):
    super().__init__(None, **attributes)
    self.hero = hero
    self.rank = rank
    self.level = level
    self.transform = transform
    self.dbrow = dbrow
    self.last_status = None
    if hero in hero_transformable.keys():
      self.child_emojis.append(arrow_emojis["trans"])
      self.transform_text = hero_transformable[hero]
    self.child_emojis.extend((arrow_emojis["backward"], arrow_emojis["forward"], arrow_emojis["down"], 
      arrow_emojis["fast_down"], arrow_emojis["up"], arrow_emojis["fast_up"]))
    
  @property
  def stats(self):
    return HeroStats(self.hero, self.rank, self.level, self.dbrow).get_clean_stats(self.transform)
    
  async def transfer_to_child(self, emoji):
    if emoji == arrow_emojis["trans"]:
      self.last_status = (self.current_stats, self.rank, self.level, self.transform)
      self.transform = not self.transform
      return self
    elif emoji == arrow_emojis["backward"]:
      if self.rank > self.dbrow["minRank"]:
        self.last_status = (self.current_stats, self.rank, self.level, self.transform)
        self.rank -= 1
        return self
      else:
        return None
    elif emoji == arrow_emojis["forward"]:
      if self.rank < self.dbrow["maxRank"]:
        self.last_status = (self.current_stats, self.rank, self.level, self.transform)
        self.rank += 1
        return self
      else:
        return None
    elif emoji == arrow_emojis["down"]:
      if self.level > 1:
        self.last_status = (self.current_stats, self.rank, self.level, self.transform)
        self.level -= 1
        return self
      else:
        return None
    elif emoji == arrow_emojis["fast_down"]:
      if self.level > 1:
        self.last_status = (self.current_stats, self.rank, self.level, self.transform)
        self.level = max(self.level-5, 1)
        return self
      else:
        return None
    elif emoji == arrow_emojis["up"]:
      if self.level < max_level:
        self.last_status = (self.current_stats, self.rank, self.level, self.transform)
        self.level += 1
        return self
      else:
        return None
    elif emoji == arrow_emojis["fast_up"]:
      if self.level < max_level:
        self.last_status = (self.current_stats, self.rank, self.level, self.transform)
        self.level = min(self.level+5, max_level)
        return self
      else:
        return None
        
  async def get_embed(self):
    self.current_stats = self.stats
    instruction = f"{arrow_emojis['backward']} {arrow_emojis['forward']} Rank       {arrow_emojis['down']} {arrow_emojis['up']} Level"
    if arrow_emojis["trans"] in self.child_emojis:
      form_text = f"__{self.transform_text[self.transform]}__ "
      instruction = f"{instruction}\n{arrow_emojis['trans']} Transform"
    else:
      form_text = ""
    reqMsg = []
    if self.last_status is None:
      statsMsg = self.current_stats.clean_stats_msg()
      introMsg = f"{form_text}at __R{self.rank}__ and __Lv{self.level}__"
    else:
      (last_stats, last_rank, last_level, last_transform) = self.last_status
      statsMsg = self.current_stats.stats_change_msg(last_stats)
      rank_msg = f"__R{self.rank}__"
      if self.rank != last_rank:
        rank_msg = f"{rank_msg} ({self.rank-last_rank:+})"
        reqMsg.append(rankup_cost_msg(self.context, self.hero, self.rank, last_rank))
      level_msg = f"__Lv{self.level}__"
      if self.level != last_level:
        level_msg = f"{level_msg} ({self.level-last_level:+})"
        reqMsg.append(lvlup_cost_msg(self.context, self.hero, self.level, last_level))
      if self.transform != last_transform:
        form_text = f"{form_text}{arrow_emojis['trans'] }"
      introMsg = f"{form_text}at {rank_msg} and {level_msg}"
    max_len = max(len(ele) for ele in statsMsg)
      
    embed = discord.Embed(title=f"Stats: {self.hero}",
      timestamp=datetime.utcnow(), colour=discord.Colour.blue())
    embed.add_field(name=f"{introMsg}:", value="\n".join(f"`{stat:<{max_len}}`" for stat in statsMsg), inline=False)
    if reqMsg:
      embed.add_field(name="Required Resources:", value="\n".join(reqMsg), inline=False)
    embed.add_field(name=f"To adjust stats:", value=instruction, inline=False)
    emoji = None
    if self.hero == "koizuul" and self.transform:
      emoji = self.context.bot.get_emoji(self.context.guild, "koizuul dragon")
    if emoji is None:
      emoji = self.context.bot.get_emoji(self.context.guild, self.hero)
    if emoji is not None:
      embed.set_thumbnail(url=emoji.url)
      embed.set_footer(text="STATS CARD", icon_url=emoji.url)
    else:
      embed.set_footer(text="STATS CARD")
    return embed
    
class StatsCmpMessage(InteractiveMessage):
  def __init__(self, hero, rank1, level1, rank2, level2, dbrow, transform=False, adjustR=True, **attributes):
    super().__init__(None, **attributes)
    self.hero = hero
    self.rank = [rank1, rank2]
    self.level = [level1, level2]
    self.transform = transform
    self.adjustR = adjustR # to adjust left stats or right stats, default right
    self.dbrow = dbrow
    if hero in hero_transformable.keys():
      self.child_emojis.append(arrow_emojis["trans"])
      self.transform_text = hero_transformable[hero]
    self.child_emojis.extend((arrow_emojis["left_right"], arrow_emojis["backward"], arrow_emojis["forward"], 
      arrow_emojis["down"], arrow_emojis["fast_down"], arrow_emojis["up"], arrow_emojis["fast_up"]))
    
  @property
  def statsL(self):
    return HeroStats(self.hero, self.rank[0], self.level[0], self.dbrow).get_clean_stats(self.transform)
    
  @property
  def statsR(self):
    return HeroStats(self.hero, self.rank[1], self.level[1], self.dbrow).get_clean_stats(self.transform)
    
  async def transfer_to_child(self, emoji):
    if emoji == arrow_emojis["left_right"]:
      self.adjustR = not self.adjustR
      return self
    elif emoji == arrow_emojis["trans"]:
      self.transform = not self.transform
      return self
    elif emoji == arrow_emojis["backward"]:
      if self.rank[self.adjustR] > self.dbrow["minRank"]:
        self.rank[self.adjustR] -= 1
        return self
      else:
        return None
    elif emoji == arrow_emojis["forward"]:
      if self.rank[self.adjustR] < self.dbrow["maxRank"]:
        self.rank[self.adjustR] += 1
        return self
      else:
        return None
    elif emoji == arrow_emojis["down"]:
      if self.level[self.adjustR] > 1:
        self.level[self.adjustR] -= 1
        return self
      else:
        return None
    elif emoji == arrow_emojis["fast_down"]:
      if self.level[self.adjustR] > 1:
        self.level[self.adjustR] = max(self.level[self.adjustR]-5, 1)
        return self
      else:
        return None
    elif emoji == arrow_emojis["up"]:
      if self.level[self.adjustR] < max_level:
        self.level[self.adjustR] += 1
        return self
      else:
        return None
    elif emoji == arrow_emojis["fast_up"]:
      if self.level[self.adjustR] < max_level:
        self.level[self.adjustR] = min(self.level[self.adjustR]+5, max_level)
        return self
      else:
        return None
        
  async def get_embed(self):
    leftStats, rightStats = self.statsL, self.statsR
    instruction = (f"{arrow_emojis['backward']} {arrow_emojis['forward']} Rank       {arrow_emojis['down']} {arrow_emojis['up']} Level"
                   f"\n{arrow_emojis['left_right']} L/R Switch")
    if arrow_emojis["trans"] in self.child_emojis:
      form_text = f"on __{self.transform_text[self.transform]}__ "
      instruction = f"{instruction} {arrow_emojis['trans']} Transform"
    else:
      form_text = ""
    if self.adjustR:
      introMsg = f"Comparison {form_text}at R{self.rank[0]} Lv{self.level[0]} to __R{self.rank[1]} Lv{self.level[1]}__"
    else:
      introMsg = f"Comparison {form_text}at __R{self.rank[0]} Lv{self.level[0]}__ to R{self.rank[1]} Lv{self.level[1]}"
    statsMsg = leftStats.stats_compare_msg(rightStats)
    max_len = max(len(ele) for ele in statsMsg)
    
    reqMsg = []
    if self.rank[0] != self.rank[1]:
      reqMsg.append(rankup_cost_msg(self.context, self.hero, self.rank[0], self.rank[1]))
    if self.level[0] != self.level[1]:
      reqMsg.append(lvlup_cost_msg(self.context, self.hero, self.level[0], self.level[1]))
      
    embed = discord.Embed(title=f"Stats: {self.hero}",
      timestamp=datetime.utcnow(), colour=discord.Colour.blue())
    embed.add_field(name=f"{introMsg}:", value="\n".join(f"`{stat:<{max_len}}`" for stat in statsMsg), inline=False)
    if reqMsg:
      embed.add_field(name="Required Resources:", value="\n".join(reqMsg), inline=False)
    embed.add_field(name=f"To adjust stats:", value=instruction, inline=False)
    emoji = None
    if self.hero == "koizuul" and self.transform:
      emoji = self.context.bot.get_emoji(self.context.guild, "koizuul dragon")
    if emoji is None:
      emoji = self.context.bot.get_emoji(self.context.guild, self.hero)
    if emoji is not None:
      embed.set_thumbnail(url=emoji.url)
      embed.set_footer(text="STATS CARD", icon_url=emoji.url)
    else:
      embed.set_footer(text="STATS CARD")
    return embed
