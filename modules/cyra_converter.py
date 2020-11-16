import difflib
import modules.custom_exceptions as custom_exceptions
from modules.cyra_constants import hero_synonyms, ability_synonyms, hero_list, achievements, achievement_synonyms

def find_hero(word):
  word = word.lower()
  if word in hero_synonyms:
    return hero_synonyms[word]
  else:
    close_word = difflib.get_close_matches(word, hero_list, n=1)
    if not len(close_word) == 0:
      return close_word[0]
  raise custom_exceptions.HeroNotFound(word.title())
  
def find_ability(word):
  word = word.lower()
  if word.split(" ", 1)[0] in ["rank1", "rank2", "rank3", "rank4", "rank5", "rank6", "rank7"]:
    return word.replace("rank", "r", 1)
  if word in ability_synonyms:
    return ability_synonyms[word]
  return word
  
def find_achievement(name):
  name = name.lower()
  if name in ["shortest", "fastest", "short", "fast", "quick", "quickest"]:
    return "fast"
  elif name in achievement_synonyms:
    return achievement_synonyms[name]
  else:
    close_word = difflib.get_close_matches(name, achievements, n=1)
    if not len(close_word) == 0:
      return close_word[0]
  raise custom_exceptions.ItemNotFound("Achievement", name.title())
  
def toMode(argument):
  argument = argument.lower()
  if argument in ["legend", "legendary"]:
    return "legendary"
  elif argument in ["camp", "campaign"]:
    return "campaign"
  raise custom_exceptions.ItemNotFound("Mode", argument.title())

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
  
