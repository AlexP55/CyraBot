from modules.cyra_constants import achievements, achievemets_dict

def parse_level(entry):
  parsed_level = {"initial_gold":entry["initial_gold"], "max_life":entry["max_life"], "enemy_waves":[]}
  waves = entry["enemy_waves"]
  for wave in waves:
    parsed_level["enemy_waves"].append(parse_wave(wave))
  return parsed_level

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
    
def parse_wave_group(group, units):
  time = group["delay"] + (group["count"] - 1) * group["cadence"]
  if group["unit"] in units:
    units[group["unit"]] += group["count"]
  else:
    units[group["unit"]] = group["count"]
  return time
  
def parse_subwave(subwave, units):
  max_time = 0
  for group in subwave["groups"]:
    max_time = max(max_time, parse_wave_group(group, units))
  return max_time + subwave["delay"]
  
def parse_wave(wave):
  units = {}
  max_time = 0
  for subwave in wave["subwaves"]:
    max_time = max(max_time, parse_subwave(subwave, units))
  wave_data = {"reward":wave["total_reward"], "bonus":wave["max_early_bonus"], "time":max_time, "enemies":units}
  return wave_data
  
def sum_dict(dict1, dict2):
  for key in dict2:
    if key in dict1:
      dict1[key] += dict2[key]
    else:
      dict1[key] = dict2[key]
