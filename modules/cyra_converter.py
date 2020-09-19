import difflib
from modules.cyra_constants import hero_synonyms, ability_synonyms, hero_list

def find_hero(word):
  word = word.lower()
  if word in hero_synonyms:
    return hero_synonyms[word]
  else:
    close_word = difflib.get_close_matches(word, hero_list, n=1)
    if not len(close_word) == 0:
      return close_word[0]
  raise custom_exceptions.HeroNotFound(string.capwords(word))
  
def find_ability(word):
  word = word.lower()
  if word.split(" ", 1)[0] in ["rank1", "rank2", "rank3", "rank4", "rank5", "rank6", "rank7"]:
    return word.replace("rank", "r", 1)
  if word in ability_synonyms:
    return ability_synonyms[word]
  return word
  
def toWorld(argument):
  world = argument.lower()
  if world.startswith("world"):
    world = world.replace("world", "", 1)
  elif world.startswith("w"):
    world = world.replace("w", "", 1)
  return int(world)
