# CyraBot
This is a bot for Realm Defense discord server using the base bot: https://github.com/Kaldzkur/DiscordBaseBot.
It supports server moderations as well as showing various information on mobile game Realm Defense: Epic Tower Defense Strategy Game.

## Installation
You need a few PyPI packages for this bot to work:

````bash
pip install -U discord.py
pip install -U python-dotenv
pip install -U pytz
pip install -U emoji
pip install -U python-dateutil
pip install -U xlrd
````

It is highly recommended to upload the pictures in 'emojis/' as emojis in the server to improve the visual effects of the information commands.

After inviting the bot to the sever, you need to use the fetch command `?fetch all` to update the database of game. The database will be updated with the new patches in game. Using `?fetch all` after the `?upgrade` command will apply all the modifications to the bot's database.

## Main Features
In addition to the basic features inherited from base bot: https://github.com/Kaldzkur/DiscordBaseBot, the CyraBot has a few specific features for the Realm Defense game.

#### 1. Transformation between Cyra/Elara
A cool visual transformation in the server every 2 hours which changes the bot's role, name, and profile picture. Bot owners can use `?transform` to force a transformation.

#### 2. Various Information Commands
A large number of information commands showing game general information. Most of them are displayed in a pretty discord embed.

#### 3. Interactive Stats Commands
Hero stats, hero ability, tower, enemy, item, buff commands include stats which are data-mined from assets files and not directly shown in-game. Hero stats, hero ability and tower commands have a fancy "interactive" fashion by which the output embed will update based on your reaction made to the message. You can easily explore the hero/ability/tower list, change the hero rank/level or even transform hero forms in a single command.
