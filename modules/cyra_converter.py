import difflib
import re
import emoji
from datetime import timedelta
import discord
from discord.ext import commands
import modules.custom_exceptions as custom_exceptions
from modules.cyra_constants import hero_synonyms, ability_synonyms, hero_list, achievements, \
                                   achievement_synonyms, emoji_dict, farmable_achievement_synonyms, \
                                   transform_synonyms
from unidecode import unidecode

def find_closest(word, word_list):
  close_word = difflib.get_close_matches(word, word_list, n=1)
  if close_word:
    return close_word[0]
  return None
  
def find_hero_from_emoji(ctx, argument):
  # read a hero emoji
  match = re.match(r'<(a?):hero_([a-zA-Z]+)([0-9]+)?:([0-9]+)>$', argument)
  if match:
    hero_name = match.group(2)
    hero_name = emoji_dict[hero_name] if hero_name in emoji_dict else hero_name.lower()
    if hero_name not in hero_list:
      raise custom_exceptions.HeroNotFound(hero_name.title())
    emoji_id = int(match.group(4))
    emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)
    if not emoji:
      emoji = ctx.bot.get_emoji(ctx.guild, hero_name)
    return hero_name, emoji
  raise custom_exceptions.HeroNotFound(argument.title())
  
def find_hero_from_text(word):
  word = word.lower()
  close_word = find_closest(word, list(hero_synonyms))
  if close_word:
    return hero_synonyms[close_word]
  raise custom_exceptions.HeroNotFound(word.title())

class find_hero(commands.Converter):
  # convert a hero input to a string
  async def convert(self, ctx, word):
    try:
      hero, _ = find_hero_from_emoji(ctx, word)
      return hero
    except:
      return find_hero_from_text(word)
  
class hero_emoji_converter(commands.Converter):
  # convert a hero input to an emoji, can be used to distinguish skins
  async def convert(self, ctx, argument):
    try:
      _, emoji = find_hero_from_emoji(ctx, argument)
    except:
      hero = find_hero_from_text(argument)
      emoji = ctx.bot.get_emoji(ctx.guild, hero)
    if emoji:
      return emoji
    raise custom_exceptions.HeroNotFound(argument.title())
    
def hero_and_secret(word):
  word = word.lower()
  close_word = find_closest(word, list(transform_synonyms))
  if close_word:
    return transform_synonyms[close_word]
  raise custom_exceptions.HeroNotFound(word.title())
  
def find_ability(word):
  word = word.lower()
  keywords = word.split()
  if keywords[0] in ["rank", "r"]:
    keywords.pop(0)
    keywords[0] = f"r{keywords[0]}"
  elif keywords[0].startswith("rank") and keywords[0][4:].isnumeric():
    keywords[0] = keywords[0].replace("rank", "r", 1)
  word = " ".join(keywords)
  if word in ability_synonyms:
    return ability_synonyms[word]
  return word
  
def find_farmable_achievement(name):
  name = name.lower()
  close_word = find_closest(name, list(farmable_achievement_synonyms))
  if close_word:
    return farmable_achievement_synonyms[close_word]
  raise custom_exceptions.DataNotFound("Achievement", name.title())
  
def find_achievement(name):
  name = name.lower()
  close_word = find_closest(name, list(achievement_synonyms))
  if close_word:
    return achievement_synonyms[close_word]
  raise custom_exceptions.DataNotFound("Achievement", name.title())
  
def toMode(argument):
  argument = argument.lower()
  if argument in ["legend", "legendary"]:
    return "legendary"
  elif argument in ["camp", "campaign"]:
    return "campaign"
  raise custom_exceptions.DataNotFound("Mode", argument.title())

def toWorld(argument):
  world = argument.lower()
  if world.startswith("world"):
    world = world.replace("world", "", 1)
  elif world.startswith("w"):
    world = world.replace("w", "", 1)
  world = world.strip()
  return int(world)
  
def toLevelWorld(argument):
  world = argument.lower()
  if world.startswith("world"):
    return int(world[5:].strip())
  elif world.startswith("w"):
    return int(world[1:].strip())
  elif world in ["s", "sr", "shattered realms", "shatteredrealms"]:
    return "S"
  elif world in ["a", "arcade", "arcades"]:
    return "A"
  elif world in ["e", "endless"]:
    return "E"
  elif world in ["c", "challenge", "challenges"]:
    return "C"
  elif world in ["connie", "connie story", "conniestrory"]:
    return "Connie"
  raise custom_exceptions.DataNotFound("World", argument.title())
  
def numberComparisonConverter(argument):
  if "->" in argument:
    numbers = argument.split("->")
    return int(numbers[0]), int(numbers[1])
  else:
    return int(argument)
    
def TournamentTimeConverter(argument):
  # format minutes:seconds.milliseconds
  regex = re.compile(r'^(?P<minutes>\d+?):(?P<seconds>\d+?)[.:](?P<milliseconds>\d+?)$')
  parts = regex.match(argument)
  if not parts:
    raise Exception # cannot parse
  parts = parts.groupdict()
  time_params = {}
  for (name, param) in parts.items():
    if param:
      time_params[name] = int(param)
  if not time_params:
    raise Exception # cannot parse
  return timedelta(**time_params)
  
def deEmojify(text):
  text = emoji.get_emoji_regexp().sub(u'', text)
  return unidecode(text, "replace")
