max_level = 35

emoji_keys = {
  "elixir":"item_Elixir",
  "gem":"item_Gem",
  "medal":"item_Medal",
  "star":"item_star",
  "coin":"item_coin",
  "fee":"hero_Fee1",
  "lancelot":"hero_Lancelot1",
  "smoulder":"hero_Smoulder1",
  "efrigid":"hero_Efrigid1",
  "hogan":"hero_Hogan1",
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
  "normal connie":"hero_Connie",
  "connie":"hero_ConnieNecro",
  "shamiko":"hero_Shamiko1",
  "cyra":"hero_Cyra",
  "elara":"hero_Elara",
  "koizuul dragon":"hero_Koizuul5"
}

hero_synonyms = {
  "koi":"koizuul",
  "elsa":"efrigid",
  "efridge":"efrigid",
  "lance":"lancelot",
  "maybe":"mabyn",
  "masa":"masamune",
  "shampoo":"shamiko",
  "necroconnie":"connie",
  "normalconnie":"normal connie",
  "elana":"elara",
}

ability_synonyms = {
  "range":"ranged",
  "melee attack":"melee",
  "ranged attack":"ranged",
  "range attack":"ranged"
}

hero_list = [
  "azura","bolton","caldera","connie","efrigid",
  "fee","helios","hogan","koizuul","lancelot","leif",
  "mabyn","masamune","narlax","obsidian","raida","sethos",
  "shamiko","smoulder","yan","normal connie","cyra","elara",
]

hero_transformable = {
  "leif": ("Weapon lv1", "Weapon lv6"),
  "caldera": ("True Form", "Giant Form"),
  "koizuul": ("Fish Form", "Dragon Form"),
  "cyra": ("Normal Form", "Goddess Form"),
  "elara": ("Normal Form", "Goddess Form")
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
  7:["cyra", "elara"],
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
  7: "https://static.wikia.nocookie.net/realm-defense-hero-legends-td/images/7/7f/Worldmap_comingSoon.png/revision/latest?cb=20200906151342"}
  
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

achievemets_dict = {
"Slime":["slime"],"Skeleton":["skeleton"],"Crow":["flying"],"Skeleton Archer":["skeleton"],"Spider":["spider"],"Poison Spider":["spider"],
"Skeleton Mage":["skeleton"],"Bucket Slime":["slime"],"Giant Slime":["slime"],"Slime Queen":["slime"],"Slime Blob":["slime"],"Goblin Grunt":["goblin"],
"Crow Rider":["flying"],"Goblin Archer":["goblin"],"Goblin Shaman":["goblin"],"Maniac":["goblin"],"Goblin Tallman":["goblin"],
"Heretic":["goblin"],"Orc":["goblin"],"Goblin Chieftain":["goblin"],"Hordemonger":["goblin"],"Flying Scarab":["flying"],
"Anubian":["anubian"],"Vulture Rider":["flying"],"Mega Anubian":["anubian"],"Cactus Golem":["golem"],"Fire Elemental":["elemental"],
"Ice Elemental":["elemental"],"Whelp":["flying"],"Time Construct":["golem"],"Wizard Initiate":["wizard"],"Void Elemental":["elemental"],"Gravity Wizard":["wizard"],
"Earth Elemental":["elemental"],"Ivory Golem":["golem"],"Duskvine Sproutling":["duskvine"],"Aqua Slime":["slime"],
"Cave Bat":["flying"],"Lava Slime":["slime","lava"],"Lava Bat":["flying","lava"],"Lava Snail":["lava"],"Duskvine Sporophyte":["duskvine"],"Giant Cave Bat":["flying"],
"Myrk Archer":["myrk"],"Small Ent":["ent"],"Duskvine Lasher":["duskvine"],"Myrk Assassin":["myrk"],"Duskvine Crusher":["duskvine"],"Myrk Warlock":["myrk"],
"Lava Pango":["lava"],"Lava Smasher":["lava"],"Large Ent":["ent"],"Strange Monk":["w6"],"Big Crane":["w6","flying"],"Origami Crane":["w6","flying"],
"Oni-tekidanhei":["w6"],"Daruma":["w6","flying"],"Small Ghostfire":["w6","spirit"],"Chibi-Mahou":["w6"],"Harpi":["w6","flying"],"Skeleton Samurai":["w6","skeleton"],
"Mizu-no-Sei":["w6","flying"],"Oni-baba":["w6"],"Koi-jin":["w6"],"Kakutouka":["w6"],"Oni-ken":["w6"],"Kagami-no-Yuurei":["w6","spirit"],"Namazu-jin":["w6"],
"Oni Mask":["w6","flying","spirit"],"Aoi Mask":["w6","flying","spirit"],"Kami-no-Mahoutsukai":["w6"],"Kaeru-hei":["w6"],"Big Ghostfire":["w6","spirit"],
"Shunmin-shi":["w6"],"Oni-kanadzuchi":["w6"]
}
achievements = sorted(set([j for i in achievemets_dict.values() for j in i]))
achievement_synonyms = {
"w6enemy":"w6",
"world6":"w6",
"bird":"flying",
"air":"flying"
}
