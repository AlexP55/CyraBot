from modules.cyra_constants import achievements, achievemets_dict

def is_boss_level(level, mode, remark):
  return (remark == "boss" and (mode != "legendary" or level in ["10", "20", "30", "40"]))

def parse_achievements(waves):
  time = 0
  achievement_count = {achievement:0 for achievement in achievements}
  gold = 0
  for wave in waves:
    time += wave["time"]
    sum_dict(achievement_count, parse_wave_achievements(wave["enemies"]))
    gold += wave["reward"] + wave["bonus"]
  return time, achievement_count, gold
  
def parse_wave_achievements(enemies):
  achievement_count = {}
  for enemy in enemies:
    if enemy in achievemets_dict:
      for name in achievemets_dict[enemy]:
        if name in achievement_count:
          achievement_count[name] += enemies[enemy]
        else:
          achievement_count[name] = enemies[enemy]
  return achievement_count
  
def sum_dict(dict1, dict2):
  for key in dict2:
    if key in dict1:
      dict1[key] += dict2[key]
    else:
      dict1[key] = dict2[key]
