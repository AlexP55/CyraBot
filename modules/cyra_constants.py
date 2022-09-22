import discord

max_level = 40

emoji_keys = {
  "elixir":"item_Elixir",
  "gem":"item_Gem",
  "medal":"item_Medal",
  "star":"item_star",
  "coin":"item_coin",
  "meteor":"item_Meteor",
  "fee":"hero_Fee1",
  "lancelot":"hero_Lancelot1",
  "smoulder":"hero_Smoulder1",
  "efrigid":"hero_Efrigid1",
  "normal hogan":"hero_Hogan1",
  "hogan":"hero_HoganBeastmaster1",
  "bolton":"hero_Bolton1",
  "obsidian":"hero_Obsidian1",
  "masamune":"hero_Masamune1",
  "mabyn":"hero_Mabyn1",
  "narlax":"hero_Narlax1",
  "sethos":"hero_Sethos1",
  "helios":"hero_Helios1",
  "yan":"hero_Yan1",
  "raida":"hero_Raida1",
  "caldera":"hero_Caldera1",
  "leif":"hero_Leif1",
  "koizuul":"hero_Koizuul1",
  "azura":"hero_Azura1",
  "normal connie":"hero_Connie1",
  "connie":"hero_ConnieNecro1",
  "shamiko":"hero_Shamiko1",
  "cyra":"hero_Cyra1",
  "elara":"hero_Elara1",
  "osan":"hero_Osan1",
  "jett":"hero_Jett1",
  "koizuul dragon":"hero_Koizuul2",
  "gm":"title_4_gm",
  "knight":"title_2_knight",
  "ruler":"title_3_ruler",
  "bronze":"league_1_bronze",
  "silver":"league_2_silver",
  "gold":"league_3_gold",
  "platinum":"league_4_platinum",
  "diamond":"league_5_diamond",
  "master":"league_6_master",
  "legendary":"league_7_legendary"
}

hero_list = [
  "azura","bolton","caldera","connie","efrigid",
  "fee","helios","hogan", "normal hogan","koizuul","lancelot","leif",
  "mabyn","masamune","narlax","obsidian","raida","sethos",
  "shamiko","smoulder","yan","normal connie","cyra","elara","osan","jett"
]

emoji_dict = {
  "ConnieNecro": "connie",
  "Connie": "normal connie",
  "HoganBeastmaster": "hogan",
  "Hogan": "normal hogan"
}

hero_transformable = {
  "leif": ("Weapon lv1", "Weapon lv6"),
  "caldera": ("True Form", "Giant Form"),
  "koizuul": ("Fish Form", "Dragon Form"),
  "cyra": ("Normal Form", "Goddess Form"),
  "elara": ("Normal Form", "Goddess Form"),
  "jett": ("Normal Form", "Overheat Mode"),
}

hero_synonyms = {hero:hero for hero in hero_list}
hero_synonyms.update({ # hero synonyms
  "koi":"koizuul",
  "elsa":"efrigid",
  "efridge":"efrigid",
  "lance":"lancelot",
  "maybe":"mabyn",
  "masa":"masamune",
  "shampoo":"shamiko",
  "necroconnie":"connie",
  "old connie":"normal connie",
  "beastmasterhogan":"hogan",
  "old hogan":"normal hogan",
  "elana":"elara",
})
transform_extra = ["secret", "sylvan mercenary","l.a.g."]
transform_synonyms = hero_synonyms.copy()
transform_synonyms.update({hero:hero for hero in transform_extra})

ability_synonyms = {
  "range":"ranged",
  "melee attack":"melee",
  "ranged attack":"ranged",
  "range attack":"ranged"
}

# which world are heroes in
world_hero = {
  1:["fee", "lancelot", "hogan", "masamune", "bolton", "normal connie",
     "connie", "smoulder", "efrigid",],#"obsidian","mabyn"
  2:["obsidian", "mabyn"],
  3:["sethos", "helios"],
  4:["yan", "narlax"],
  5:["leif", "caldera"],
  6:["azura", "raida", "koizuul", "shamiko"],
  7:["cyra", "elara", "osan", "jett"],
  None:[], #default 
}

hero_menu_url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/d/d4/RDLoadingScreen.jpg/revision/latest?cb=20200906151545"
tower_menu_url = "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/2/27/RealmDefenseBanner.jpg/revision/latest?cb=20191107143646&format=original"

# url containing world thumbnails
world_url = {1: "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/5/58/Worldmap_world1.png/revision/latest?cb=20200906151344",
  2: "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/b/ba/Worldmap_world2.png/revision/latest?cb=20200906151344",
  3: "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/7/78/Worldmap_world3.png/revision/latest?cb=20200906151345",
  4: "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/d/d5/Worldmap_world4.png/revision/latest?cb=20200906151345",
  5: "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/c/ca/Worldmap_world5.png/revision/latest?cb=20200906151346",
  6: "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/e/ee/Worldmap_world6.png/revision/latest?cb=20200906151346",
  7: "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/4/4a/Worldmap_world7.png/revision/latest?cb=20210425052258",
  "S": "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/3/3b/SR.png/revision/latest?cb=20191128132619",
  "A": "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/9/91/Arcade.png/revision/latest?cb=20191128132703",
  "E": "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/1/14/Endless2.jpg/revision/latest?cb=20200209220437",
  "C": "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/c/cd/Challenges.png/revision/latest?cb=20191128135100&format=original",
  "T": "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/d/d3/Tournament1.png/revision/latest?cb=20191128132552",
  "Connie": "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/3/3e/Connie_Event_Chapter7.png/revision/latest?cb=20200228183358&format=original"}
  
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
  "Bosses are immune to most of the time buffs. The buffs that can affect them are Shamiko's Lovely Lullaby, Elara's 40% and 60% slow, Bolton's rank 5 shock, Efrigid's rank 5 freeze, and Broto's bubble",
  "Dodge can avoid direct damage, but it can never avoid a buff or a percentage damage.",
  "Buffs to troop towers don't have any effect on their troops, not even on the respawn rate.",
  "Selling a tower returns 70% gold spent. Before calling the first wave this ratio is 100%, but rebuilding towers during this will not count towards achievements.",
  "Some of the charmed units including Mummy, Magic Book, Cloud Sunfish, Origami Crane and Harpy cannot engage in melee.",
  "Don't use Shamiko's spell too fast. A unit will not receive a new buff/debuff if it already received one in the last 6s even if it's a different buff.",
  "50 is the maximum number of enemies in screen.",
  "Enemies taken terror from a specific set of spells will receive resistance that reduces the terror duration from the same set of skills, including Elara's Imposing Aura, Fee's R7 with Mabyn, Mabyn's Jack Toss and Raining Gift, Dragon Tower's terrify. Other terrify skills including Elara's Comic Flux, Shamiko's Shrieking Shred neither increase nor are affected by resistance",
  "Poison improved by Osan is a actually a burning effect that can damage shield points and kill enemies."
]
facts.append(f"There are {len(facts)+1} random facts stored in this command. Did you find them all?")

elixir_cost_fee =   [        10,     18,     45,     81,     121,    163,    208,    253,    298,
                     313,    329,    345,    362,    380,    399,    419,    440,    462,    485,
                     655,    885,    1194,   1612,   2177,   2938,   3967,   5355,   7230,   9760,
                     13176,  17787,  24013,  32418,  43764,  45296,  46881,  48522,  50220,  51978]
elixir_cost_lance = [        0,      36,     65,     117,    210,    378,    380,    382,    384,
                     404,    423,    444,    466,    490,    514,    540,    567,    595,    625,
                     844,    1139,   1537,   2075,   2802,   3783,   5106,   6894,   9307,   12564,
                     16961,  22898,  30912,  41731,  56337,  58308,  60349,  62461,  64647,  66910]
elixir_cost_1500 =  [        30,     54,     97,     175,    315,    567,    570,    573,    575,
                     604,    634,    666,    699,    734,    771,    810,    850,    893,    937,
                     1265,   1708,   2306,   3113,   4203,   5674,   7660,   10341,  13960,  18846,
                     25442,  34347,  46368,  62596,  84505,  87462,  90524,  93692,  96971,  100365]
elixir_cost_3000 =  [        40,     72,     130,    233,    420,    756,    760,    763,    767,
                     806,    846,    888,    933,    979,    1028,   1080,   1134,   1190,   1250,
                     1687,   2278,   3075,   4151,   5604,   7565,   10213,  13787,  18613,  25128,
                     33922,  45795,  61823,  83462,  112673, 116617, 120698, 124923, 129295, 133820]
elixir_cost_6000 =  [        50,     90,     162,    292,    525,    945,    950,    954,    959,
                     1007,   1057,   1110,   1166,   1224,   1285,   1349,   1417,   1488,   1562,
                     2109,   2847,   3843,   5189,   7005,   9456,   12766,  17234,  23267,  31410,
                     42403,  57244,  77279,  104327, 140841, 145771, 150873, 156154, 161619, 167276]
elixir_cost_7500 =  [        60,     108,    194,    350,    630,    1134,   1139,   1145,   1151,
                     1208,   1269,   1332,   1399,   1469,   1542,   1619,   1700,   1785,   1875,
                     2531,   3416,   4612,   6226,   8406,   11348,  15319,  20681,  27920,  37691,
                     50883,  68693,  92735,  125192, 169010, 174925, 181047, 187384, 193942, 200730]
elixir_cost_hero = {
  "fee":elixir_cost_fee,
  "lancelot":elixir_cost_lance,
  "smoulder":elixir_cost_3000,
  "efrigid":elixir_cost_3000,
  "normal hogan":elixir_cost_1500,
  "hogan":elixir_cost_1500,
  "bolton":elixir_cost_1500,
  "obsidian":elixir_cost_3000,
  "masamune":elixir_cost_1500,
  "mabyn":elixir_cost_3000,
  "sethos":elixir_cost_6000,
  "helios":elixir_cost_6000,
  "normal connie":elixir_cost_1500,
  "connie":elixir_cost_1500,
}

rank_cost = [5, 10, 15, 20, 40, 80, 100]

def elixir_cost_list(hero):
  if hero in elixir_cost_hero: return elixir_cost_hero[hero]
  else: return elixir_cost_7500

def elixir_cost(hero, lvlow, lvhigh):
  if lvlow > lvhigh:
    lvlow, lvhigh = lvhigh, lvlow
  return sum(elixir_cost_list(hero)[lvlow-1:lvhigh-1])
  
def token_cost(ranklow, rankhigh):
  if ranklow > rankhigh:
    ranklow, rankhigh = rankhigh, ranklow
  return sum(rank_cost[ranklow:rankhigh])

achievemets_dict = {
"Slime":["slime"],"Bucket Slime":["slime"],"Giant Slime":["slime"],"Slime Queen":["slime"],"Slime Blob":["slime"],
"Skeleton":["skeleton"],"Skeleton Archer":["skeleton"],"Skeleton Mage":["skeleton"],
"Spider":["spider"],"Poison Spider":["spider"],
"Crow":["flying"],

"Goblin Grunt":["goblin"],"Goblin Archer":["goblin"],"Goblin Shaman":["goblin"],"Maniac":["goblin"],"Heretic":["goblin"],
"Goblin Tallman":["goblin"],"Goblin Chieftain":["goblin"],"Orc":["goblin"],"Hordemonger":["goblin"],
"Crow Rider":["flying"],

"Anubian":["anubian"],"Mega Anubian":["anubian"],
"Cactus Golem":["golem"],
"Flying Scarab":["flying"],"Vulture Rider":["flying"],

"Fire Elemental":["elemental"],"Ice Elemental":["elemental"],"Void Elemental":["elemental"],"Earth Elemental":["elemental"],
"Gravity Wizard":["wizard"],"Wizard Initiate":["wizard"],
"Time Construct":["golem"],"Ivory Golem":["golem"],
"Whelp":["flying"],

"Duskvine Sproutling":["duskvine"],"Duskvine Sporophyte":["duskvine"],"Duskvine Lasher":["duskvine"],"Duskvine Crusher":["duskvine"],
"Myrk Archer":["myrk"],"Myrk Assassin":["myrk"],"Myrk Warlock":["myrk"],
"Aqua Slime":["slime"],"Lava Slime":["slime","lava"],
"Cave Bat":["flying"],"Lava Bat":["flying","lava"],"Giant Cave Bat":["flying"],
"Lava Snail":["lava"],"Lava Pango":["lava"],"Lava Smasher":["lava"],
"Small Ent":["ent"],"Large Ent":["ent"],

"Strange Monk":["w6","monk"],"Chibi-Mahou":["w6","monk"],"Kakutouka":["w6","monk"],"Kami-no-Mahoutsukai":["w6"],"Shunmin-shi":["w6"],
"Origami Crane":["w6","flying"],"Daruma":["w6","flying"],"Harpi":["w6","flying"],
"Oni-tekidanhei":["w6","oni"],"Oni-baba":["w6","oni"],"Oni-ken":["w6","oni"],"Oni-kanadzuchi":["w6","oni"],
"Small Ghostfire":["w6","spirit"],"Kagami-no-Yuurei":["w6","spirit"],"Oni Mask":["w6","spirit"],"Aoi Mask":["w6","spirit"],"Big Ghostfire":["w6","spirit"],
"Skeleton Samurai":["w6","skeleton"],
"Koi-jin":["w6","fishguard"],"Namazu-jin":["w6","fishguard"],"Kaeru-hei":["w6","fishguard"],

"Quadropus":["corrupted"], "Floating Rambler":["corrupted"], "Rock Rambler":["corrupted","sentient_rock"],
"Tin Slime":["w7_slime"], "Flying Slime":["w7_slime", "flying_slime"], "Ground Slime":["w7_slime"],
"Gem Eye":["security_construct"], "Eta Sentry":["security_construct"], "Chameleon Sentry":["security_construct"], "Elysium Pebble":["sentient_rock"],
"Elysium Rock":["sentient_rock"], "Rock Flinger":["sentient_rock"], "Slime Shooter":["w7_slime"], "Omega Spider":["security_construct"]
}
achievements = sorted(set([j for i in achievemets_dict.values() for j in i]))
achievements += ["villager", "bandit"]

tappables = ["tappable", "trap", "hidden enemies", "loose change", "chicken dinner", "snowman", "windmill", "cow", "boneheaded", "seeker", "llama", "mercenary board"]
tower_achievements = ["tower"]

achievement_synonyms = {achievement:achievement for achievement in achievements}
achievement_synonyms.update({ # achievement synonyms
"w6enemy":"w6",
"world6":"w6",
"bird":"flying",
"air":"flying",
"flier":"flying",
"lavacreature":"lava",
"construct":"security_construct",
"rock":"sentient_rock"
})
farmable_achievement_synonyms = achievement_synonyms.copy()

achievement_synonyms.update({tappable:tappable for tappable in tappables})
achievement_synonyms.update({achievement:achievement for achievement in tower_achievements})
achievement_synonyms.update({ # tappable synonyms
"hidden": "hidden enemies",
"unleash": "hidden enemies",
"enemies": "hidden enemies",
"loose": "loose change",
"change": "loose change",
"chicken": "chicken dinner",
"mercenary": "mercenary board"
})
achievement_synonyms.update({ # synonyms for "fast"
"fast": "fast",
"quick": "fast",
"short": "fast"
})

bot_state = {
  "_default":{
    "mod_role":"Enforcer",
    "admin_role":"Master",
    "color":discord.Colour.gold(),
    "nocommand_msg":"{context.author.mention} There is no such command. Please refer to `{context.prefix}help`.",
    "cooldown_msg":"Skill is on cooldown, please retry in {error.retry_after:.1f}s.",
    "nohero_msg":"There is no hero called **{error.item}**.",
    "noability_msg_self":"Emm... I don't think I am able to use **{error.ability}**.",
    "noability_msg_other":"Emm... I don't think **{error.hero}** is able to use **{error.ability}**.",
    "nodata_msg":"Sorry, there is nothing I know about **{error.category} - {error.item}**.",
    "badinput_msg":"{context.author.mention}, I'm not sure I understand those arguments.\nPlease refer to `{context.prefix}help {context.command.qualified_name}` for more information.",
    "noaccess_msg":"I'm sorry, you do not have permission to use {context.command.qualified_name}. Please ask my masters.",
    "unexpected_msg":"Something unexpected happened in my command. Maybe try something else?\nPlease refer to `{context.prefix}help {context.command.qualified_name}` for information on my commands."
  },
  "cyra": {
    "mod_role":"Enforcer",
    "admin_role":"Master",
    "color":discord.Colour.red(),
    "nocommand_msg":"{context.author.mention} I have my dignity as a goddess and what you ask is beneath me. Please refer to `{context.prefix}help`.",
    "cooldown_msg":"Skill is on cooldown, I should have it ready in {error.retry_after:.1f}s.",
    "nohero_msg":"Emm... None of my colleagues is called **{error.item}**.",
    "noability_msg_self":"Emm... I don't think I am able to use **{error.ability}**.",
    "noability_msg_other":"Emm... I don't think **{error.hero}** is able to use **{error.ability}**.",
    "nodata_msg":"Sorry, I want to help but I don't know anything about **{error.category} - {error.item}**.",
    "badinput_msg":"{context.author.mention}, I'm not sure I understand those arguments.\nPlease refer to `{context.prefix}help {context.command.qualified_name}` for more information.",
    "noaccess_msg":"I'm sorry, you do not have permission to use `{context.command.qualified_name}`. Please ask my masters.",
    "unexpected_msg":"Elara stopped me from executing that command. Maybe try something else?\nPlease refer to `{context.prefix}help {context.command.qualified_name}` for information on my commands."
  },
  "elara": {
    "mod_role":"Ravager",
    "admin_role":"Master",
    "color":discord.Colour.dark_purple(),
    "nocommand_msg":"{context.author.mention}, **do not try to fool me** with your fake command. Refer to `{context.prefix}help` to get a taste of the darkness.",
    "cooldown_msg":"Do not rush me mortal! I cannot use this skill so often ({error.retry_after:.1f}s remains).",
    "nohero_msg":"Who is **{error.item}**? Is that a new nickname?",
    "noability_msg_self":"**{error.ability}** sounds cool. Maybe I should learn it from now.",
    "noability_msg_other":"**{error.ability}** sounds cool. Maybe **{error.hero}** should learn it from now.",
    "nodata_msg":"**{error.category} - {error.item}** is beyond my knowledge, try to use some better words!",
    "badinput_msg":"{context.author.mention}, a smart command with awful arguments. Study the `{context.prefix}help {context.command.qualified_name}`, mortal.",
    "noaccess_msg":"Why are you using this command without permission? Watch yourself!",
    "unexpected_msg":"Cyra stopped me from executing that command. It's too dangerous, even for myself.\nRefer to `{context.prefix}help {context.command.qualified_name}` for information on my commands."
  }
}
