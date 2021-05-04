
accept_keys = ["HealthPoints", "NormalDamage", "SpecialDamage", 
  "PhysicalArmor", "MagicalArmor", "MoveSpeed", "CastSpeed", "Shield", "Dodge", "ReviveTime"]
  
class Stats:
  #A base class that acts like a dict.
  #Enemy stats and Hero stats can be derived from it.
  def __init__(self, db_result):
    for k,v in db_result.items():
      self[k] = v

  def __getattr__(self, _name):
    if _name not in self.__dict__:
      raise AttributeError(f"Stats has no attribute {_name}.")
    return self.__dict__[_name]

  def __setattr__(self, _name, _value):
    self.__dict__[_name] = _value

  def __delattr__(self, _name):
    if _name not in self._dict__:
      raise AttributeError(f"Stats has no attribute {_name}.")
    del self.__dict__[_name]

  def __getitem__(self, _key):
    if _key not in self.__dict__:
      raise KeyError(f"Stats has no attribute {_key}.")
    return self.__dict__[_key]

  def __setitem__(self, _key, _value):
    self.__dict__[_key] = _value

  def __delitem__(self, _key):
    if _key not in self._dict__:
      raise KeyError(f"Stats has no attribute {_name}.")
    del self.__dict__[_name]

class HeroStats(Stats):
  def __init__(self, unit, rank, level, db_result):
    self.unit = unit
    self.rank = rank
    self.level = level
    #We specify the stats in order of display.
    self.HealthPoints = 0
    self.NormalDamage = 0
    self.SpecialDamage = 0
    self.PhysicalArmor = 0
    self.MagicalArmor = 0
    self.MoveSpeed = 0
    self.CastSpeed = 0
    self.Shield = 0
    self.Dodge = 0
    self.ReviveTime = 0
    super().__init__(db_result)

  def calculateStats(self):
    self.HealthPoints = self.baseHP + self.rank*self.drankHP + (self.level-1)*self.dlvHP + self.rank*(self.level-1)*self.dranklvHP
    self.NormalDamage = self.baseND + self.rank*self.drankND + (self.level-1)*self.dlvND + self.rank*(self.level-1)*self.dranklvND
    self.SpecialDamage = self.baseSD + self.rank*self.drankSD + (self.level-1)*self.dlvSD + self.rank*(self.level-1)*self.dranklvSD
    self.PhysicalArmor = self.basePhysicalArmor + self.rank*self.drankPhysicalArmor
    if self.unit in ["leif", "caldera"]:
      self.CastSpeed = 1
    if self.unit == "leif":
      if self.rank < 6:
        self.NormalDamage = round(self.NormalDamage/1.5)
        self.SpecialDamage = round(self.SpecialDamage/1.5)
      else:
        self.HealthPoints *= 2
    elif self.unit == "koizuul" and self.rank >= 6:
      self.NormalDamage *= 2
      self.SpecialDamage *= 2
    elif self.unit == "yan" and self.rank >= 6:
      self.SpecialDamage *= 2
    elif self.unit == "connie" and self.rank >= 6:
      self.ReviveTime *= 0.75

  def transformStats(self):
    if self.unit == "caldera":
      self.transformHealthPoints = 8 * self.HealthPoints
      self.transformNormalDamage = 8 * self.NormalDamage
      self.transformPhysicalArmor = self.PhysicalArmor + 1
      self.transformMoveSpeed = self.MoveSpeed - 2
      self.transformCastSpeed = 2 * self.CastSpeed
    elif self.unit == "leif":
      self.transformNormalDamage = round(1.5**5 * self.NormalDamage)
      self.transformSpecialDamage = round(1.5**5 * self.SpecialDamage)
      self.transformPhysicalArmor = 5*0.05 + self.PhysicalArmor
      self.transformMoveSpeed = round(1.1**5 * self.MoveSpeed, 2)
      self.transformCastSpeed = round(1.1**5 * self.CastSpeed, 2)
    elif self.unit == "koizuul":
      if self.rank >= 5:
        x = 160
      else:
        x = 40
      self.transformNormalDamage = x * self.NormalDamage
      self.transformSpecialDamage = x * self.SpecialDamage
      self.transformMoveSpeed = 2.2
    elif self.unit in ["cyra", "elara"]:
      self.transformPhysicalArmor = self.PhysicalArmor + 0.15
      self.transformMagicalArmor = self.MagicalArmor + (0.1 if self.unit == "cyra" else 0.15)
      self.transformMoveSpeed = self.MoveSpeed + 1
    
  def get_clean_stats(self, transform:bool=False):
    # return a dictionary with clean stats
    self.calculateStats()
    if transform:
      self.transformStats()
    stats = CleanStats({})
    for key, value in self.__dict__.items():
      if key not in accept_keys or (self[key] == 0 and "Armor" not in key):
        continue
      if transform and f"transform{key}" in self.__dict__:
        stats[key] = self[f"transform{key}"]
      else:
        stats[key] = value
    return stats
    
class CleanStats(Stats):

  def clean_stats_msg(self):
    # show the clean stats messages
    messages = []
    for key, value in self.__dict__.items():
      if "Armor" in key:
        if value > 0:
          messages.append(f"{key:<13} = {value:.1%}")
      elif "Dodge" == key:
        messages.append(f"{key:<13} = {value}%")
      else:
        messages.append(f"{key:<13} = {value}")
    return messages
  
  def stats_change_msg(self, other):
    # show how the stats are changed
    messages = []
    
    for key, value in self.__dict__.items():
      if key in other.__dict__ and value != other[key]:
        if "Armor" in key:
          increase = value - other[key]
          messages.append(f"{key:<13} = {value:<6.1%} ({increase:+.1%})")
        elif "Dodge" == key:
          increase = value - other[key]
          messages.append(f"{key:<13} = {value:<5}% ({increase:+}%)")
        else:
          increase = float(value - other[key])/other[key]
          messages.append(f"{key:<13} = {value:<6} ({increase:+.1%})")
      else:
        if "Armor" in key:
          if value > 0:
            messages.append(f"{key:<13} = {value:.1%}")
        elif "Dodge" == key:
          messages.append(f"{key:<13} = {value}%")
        else:
          messages.append(f"{key:<13} = {value}")
    return messages
    
  def stats_compare_msg(self, other):
    # compare two clean stats
    messages = []
    for key, value in self.__dict__.items():
      if key in other.__dict__ and value != other[key]:
        if "Armor" in key:
          increase = other[key] - value
          messages.append(f"{key:<13} = {value:<6.1%} -> {other[key]:<6.1%} ({increase:+.1%})")
        elif "Dodge" == key:
          increase = other[key] - value
          messages.append(f"{key:<13} = {value:<5}% -> {other[key]:<5}% ({increase:+}%)")
        else:
          increase = float(other[key] - value)/value
          messages.append(f"{key:<13} = {value:<6} -> {other[key]:<6} ({increase:+.1%})")
      else:
        if "Armor" in key:
          if value > 0:
            messages.append(f"{key:<13} = {value:.1%}")
        elif "Dodge" == key:
          messages.append(f"{key:<13} = {value}%")
        else:
          messages.append(f"{key:<13} = {value}")
    return messages
