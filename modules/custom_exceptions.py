from discord.ext import commands

class ElaraRefuseToAnswer(commands.CheckFailure):
  def __init__(self, message=None):
    super().__init__(message=message)
    
class DataNotFound(commands.BadArgument):
  def __init__(self, category, item):
    super().__init__(message=f"{category}: {item} is not found in database")
    self.category = category
    self.item = item
  
class HeroNotFound(DataNotFound):
  def __init__(self, hero):
    super().__init__("Hero", hero)
    
class AbilityNotFound(DataNotFound):
  def __init__(self, hero, ability):
    super().__init__("Ability", f"{ability} for hero {hero}")
    self.hero = hero
    self.ability = ability
