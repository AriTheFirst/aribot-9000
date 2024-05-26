#!/usr/bin/env python
import re
import requests
import interactions
import os
import json
from datetime import datetime
import pytz
import time
import random
import pymongo
from dotenv import load_dotenv
import math

# Grab bot token from enviroment
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CAT_TOKEN = os.getenv("CAT_TOKEN")
bot = interactions.Client(token=TOKEN)

# Define Command Scopes
command_scopes = [752667089155915846, 1221655728029302865, 1172683672856567808]

# Set up some stuff for MongoDB
dbclient = pymongo.MongoClient("mongodb://10.0.0.21:27017")
database = dbclient["aribot-currency"]

# API Request Command
@bot.command(
    name="api",
    description="Get data on a user from Discord's API",
    scope=command_scopes,
    options = [
        interactions.Option(
            name="user",
            description="The User to get the data of",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def avatar(ctx: interactions.CommandContext, user: str):
    userchecked = re.sub("[^0-9]", "", f"{user}")
    url = f"https://discord.com/api/v10/users/{userchecked}"
    headers = {"Authorization": f"Bot {TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"Request for user {userchecked} successful!")
        response_dict = response.json() 
        username = response_dict['global_name']
        if username == None:
            username = answer['username']
        json_formatted_str = json.dumps(response_dict, indent=4, sort_keys=True)
        await ctx.send(f"Here is the Discord API response for {username}:\n```json\n{json_formatted_str}```")
    else:
        await ctx.send("Discord API Request Failed.\nThere could be multiple reasons for this:\n- You pinged a role instead of a user\n- You didn't ping the user but typed their name instead\n- You typed nonsense into the input\n- The Discord API Could be down (unlikely)",ephemeral=True)

# Avatar Command
@bot.command(
    name="avatar",
    description="Grab a user's avatar",
    scope=command_scopes,
    options=[
        interactions.Option(
            name="user",
            description="The User to get the avatar of",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def avatar(ctx: interactions.CommandContext, user: str):
    userchecked = re.sub("[^0-9]", "", f"{user}")
    url = f"https://discord.com/api/v10/users/{userchecked}"
    headers = {"Authorization": f"Bot {TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Request successful!")
        answer = response.json()
        avatar_id = answer['avatar']
        username = answer['global_name']
        print(f"{avatar_id}")
        if username == None:
            username = answer['username']
        avatar_url = f"https://cdn.discordapp.com/avatars/{userchecked}/{avatar_id}.png?size=2048"
        print(f"Got Avatar URL for User {userchecked}: {avatar_url}")
        await ctx.send(f"[Here]({avatar_url}) is {username}'s avatar!")
    else:
        print(f"API Request Failed with code {response.status_code}")
        await ctx.send("Discord API Request Failed.\nThere could be multiple reasons for this:\n- You pinged a role instead of a user\n- You didn't ping the user but typed their name instead\n- You typed nonsense into the input\n- The Discord API Could be down (unlikely)",ephemeral=True)

# Banner Command
@bot.command(
    name="banner",
    description="Grab a user's banner, and if they don't have nitro give it's hex code",
    scope=command_scopes,
    options=[
        interactions.Option(
            name="user",
            description="The User to get the banner of",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def banner(ctx: interactions.CommandContext, user: str):
    userchecked = re.sub("[^0-9]", "", f"{user}")
    url = f"https://discord.com/api/v10/users/{userchecked}"
    headers = {"Authorization": f"Bot {TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Request successful!")
        answer = response.json()
        username = answer['global_name']
        banner_id = answer['banner']
        banner_hex = answer['banner_color']
        print(f"{banner_id}")
        if username == None:
            username = answer['username']
        if banner_id == None:
            print("User does not have Nitro, Grabbing Hex Code....")
            print(f"Hex Code {banner_hex} found")
            hex_no_pound = re.sub('[^A-Za-z0-9]', '', banner_hex)
            await ctx.send(f"{username}'s banner Hex is [{banner_hex}](https://singlecolorimage.com/get/{hex_no_pound}/600x240)")
        else:
            banner_url = f"https://cdn.discordapp.com/banners/{userchecked}/{banner_id}.png?size=4096"
            print(f"Got Banner URL for User {userchecked}: {banner_url}")
            await ctx.send(f"[Here]({banner_url}) is {username}'s banner!")
    else:
        print(f"API Request Failed with code {response.status_code}")
        await ctx.send("Discord API Request Failed.\nThere could be multiple reasons for this:\n- You pinged a role instead of a user\n- You didn't ping the user but typed their name instead\n- You typed nonsense into the input\n- The Discord API Could be down (unlikely)",ephemeral=True)

# Info Command
@bot.command(
    name="info",
    description="Give information about the bot",
    scope=command_scopes,
)
async def info(ctx: interactions.CommandContext):
    await ctx.send("**## [Aribot 9000](https://github.com/AriTheFirst/aribot-9000): By [arithefirst](https://arithefirst.com)**Written in python using [interactions.py](https://github.com/interactions-py) for Discord API and [MongoDB](https://www.mongodb.com/) for storing data of the currency system")

# Ping Commang
@bot.command(
    name="ping",
    description="Sends Pong",
)
async def ping(ctx: interactions.CommandContext):
    await ctx.send('Pong!')

# Cat Command
@bot.command(
    name="cat",
    description="Sends a random cat",
    scope=command_scopes,
)
async def cat(ctx: interactions.CommandContext):
    url = "https://api.thecatapi.com/v1/images/search?limit=1&has_breeds=1"
    headers = {"x-api-key": CAT_TOKEN}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Request successful!")
        answer = response.json()
        cat_url = answer[0]['url']
        breed_full = answer[0]['breeds']
        breed = breed_full[0]['name']
        await ctx.send(f"Check out this [{breed} cat!]({cat_url})")
    else:
        print(f"API Request Failed with code {response.status_code}")
        await ctx.send(f"Error Communicating with https://thecatapi.com/v1/images/search/ ({response.status_code})")

# Coinflip Command
@bot.command(
    name="coinflip",
    description="Flips a Coin",
    scope=command_scopes,
    options=[
        interactions.Option(
            name="bet",
            description="Heads or Tails",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="wager",
            description="Amount of coins to wager",
            type=interactions.OptionType.INTEGER,
            required=False,
        )
    ]
)
async def coinflip(ctx: interactions.CommandContext, bet: str = None, wager: int = None):
    rng = random.SystemRandom()
    result = rng.randint(0, 1)
    if bet is None or wager is None:
        if result == 0:
            await ctx.send("The Coin landed on Heads!")
        else:
            await ctx.send("The Coin landed on Tails!")
    else:
        bet_lowercase = bet.lower()
        # Win on Tails
        if bet_lowercase == "tails" and result == 1:
            query = {"name": str(ctx.user.id)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                if int(balance) < int(wager):
                    await ctx.send("You wagered more than you have in your account.\nPlease try again.")
                else:
                    newbalance = int(balance) + int(wager)
                    newvalues = { "$set": { "amt": f"{newbalance}" }}
                    print(f"New balance for {ctx.user.id} is {newbalance}")
                    usercol.update_one(query, newvalues)
                    await ctx.send(f"You win! **{wager}** coins have been added to your account!\nYour new balance is **{newbalance}**!")
        # Win on Heads
        elif bet_lowercase == "heads" and result == 0:
            query = {"name": str(ctx.user.id)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                if int(balance) < int(wager):
                    await ctx.send("You wagered more than you have in your account.\nPlease try again.")
                else:
                    newbalance = int(balance) + int(wager)
                    newvalues = { "$set": { "amt": f"{newbalance}" }}
                    print(f"New balance for {ctx.user.id} is {newbalance}")
                    usercol.update_one(query, newvalues)
                    await ctx.send(f"You win! **{wager}** coins have been added to your account!\nYour new balance is **{newbalance}**!")
        # Lose on Tails            
        elif bet_lowercase == "tails" and result == 0:
            query = {"name": str(ctx.user.id)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                if int(balance) < int(wager):
                    await ctx.send("You wagered more than you have in your account.\nPlease try again.")
                else:
                    newbalance = int(balance) - int(wager)
                    newvalues = { "$set": { "amt": f"{newbalance}" }}
                    print(f"New balance for {ctx.user.id} is {newbalance}")
                    usercol.update_one(query, newvalues)
                    await ctx.send(f"You Lose. **{wager}** coins have been removed from your account.\nYour new balance is **{newbalance}**!")
        # Lose on Heads
        elif bet_lowercase == "heads" and result == 1:
            query = {"name": str(ctx.user.id)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                if int(balance) < int(wager):
                    await ctx.send("You wagered more than you have in your account.\nPlease try again.")
                else:
                    newbalance = int(balance) - int(wager)
                    newvalues = { "$set": { "amt": f"{newbalance}" }}
                    print(f"New balance for {ctx.user.id} is {newbalance}")
                    usercol.update_one(query, newvalues)
                    await ctx.send(f"You Lose. **{wager}** coins have been removed from your account.\nYour new balance is **{newbalance}**!")

# Timezones Command
@bot.command(
    name="time",
    description="Send the time in the 4 Major US Timezones, Optionally specify an extra timezone",
    scope=command_scopes,
    options=[
        interactions.Option(
            name="timezone",
            description="An optional extra timezone to get the time of (in Continent/City format)",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def time(ctx: interactions.CommandContext, timezone: str = None):  # Capture the timezone option here
    if timezone is None:  # Check if timezone is None (default case)
        time_zones = [
            "America/New_York",
            "America/Chicago",
            "America/Denver",
            "America/Los_Angeles"
        ]
        times = ""
        for tz in time_zones:
            tz_obj = pytz.timezone(tz)
            current_time = datetime.now(tz_obj)
            times += f"The time in **{tz}** is {current_time.strftime('%B %d, %Y %H:%M')}\n"
        await ctx.send(times)
    else:
        try:
            tz_obj = pytz.timezone(timezone)
            current_time = datetime.now(tz_obj)
            await ctx.send(f"The time in **{timezone}** is {current_time.strftime('%B %d, %Y %H:%M')}")
        except pytz.exceptions.UnknownTimeZoneError:
            await ctx.send("Invalid timezone provided.")

# Identify Command
@bot.command(
    name="identify",
    description="Gives you your user id and this server's id",
    scope=command_scopes,
)
async def identify(ctx: interactions.CommandContext):
    await ctx.send(f'**User ID:** {ctx.user.id}\n**Guild ID:** {ctx.guild_id}')

# Check Balance Command
@bot.command(
    name="checkbalance",
    description="Checks your balance",
    scope=command_scopes,
)
async def checkbal(ctx: interactions.CommandContext):
    query = {"name": str(ctx.user.id)}
    usercol = database[f"server-{ctx.guild_id}"]
    answer = usercol.find_one(query)
    
    if answer is None:
        name = str(ctx.user.id)
        default_values = { "name": f"{name}", "amt": "100", "lastfished": "0"}
        inst = usercol.insert_one(default_values)
        print(f"Added Entry {inst.inserted_id}")
        await ctx.send("You couldn't be found in the database, so I take it this is your first time banking with us,\nHere's 100 Coins for free!")
    else:
        balance = answer.get("amt")
        def comma_seperate(number_str):
            return "{:,}".format(int(number_str))
        formatted_blance = comma_seperate(balance)
        await ctx.send(f"Your balance is **{formatted_blance}** coins.")

# Setbalance Command
@bot.command(
    name="setbalance",
    description="Checks your balance",
    scope=command_scopes,
    options=[
        interactions.Option(
            name="user",
            description="User to modify the balance of",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="amt",
            description="New Balance for the user",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
    ]
)
async def setbalance(ctx: interactions.CommandContext, user: str, amt: int):
    if ctx.user.id == 613358761901424652:
        userchecked = re.sub("[^0-9]", "", f"{user}")
        query = {"name": f"{userchecked}"}
        usercol = database[f"server-{ctx.guild_id}"]
        newvalue = { "$set": { "amt": f"{amt}" }}
        usercol.update_one(query, newvalue)
        await ctx.send(f"<@{userchecked}>'s new balance was set to **{amt}** coins.")
    else:
        await ctx.send("This command can only be run by arithefirst herself.",ephemeral=True)

# Fish Command
@bot.command(
    name="fish",
    description="Go fishing",
    scope=command_scopes,
    )
async def fish(ctx: interactions.CommandContext):
    items = ['Old Boot', 'Rock', 'Wallet', 'Oar Fish', 'Funny Stupid Fish', 'Salmon', 'Sea Bunny', 'Wedding Ring', 'Ancient Evil Goblin That Steals your Coins']
    probabilities = [20, 20, 15, 15, 10, 10, 5, 2.5, 2.5,]
    total_percentage = sum(probabilities)
    normalized_probabilities = [p / total_percentage for p in probabilities]

    def vowel_check(item):
        delist = ' '.join(item)
        item_lower = delist.lower()
        if item_lower[0] in 'aeiou':
            return "an " + f"**{delist}**"
        else:
            return "a " + f"**{delist}**"

    value = rng.randint(1, 10)
    query = {"name": str(ctx.user.id)}
    usercol = database[f"server-{ctx.guild_id}"]
    answer = usercol.find_one(query)
    timesincefish = math.floor(time.time())-answer.get("lastfished")

    if timesincefish < 300:
        await ctx.send(f"/fish is still on cooldown for you! You have {timesincefish} seconds left.") 
    else: 
        rng = random.SystemRandom()
        fished_fish = rng.choices(items, weights=normalized_probabilities, k=1)
        if ' '.join(fished_fish) == "Old Boot":
            rng = random.SystemRandom()
            value = rng.randint(1, 10)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                newbalance = int(balance) + value
                newvalues = { "$set": { "amt": f"{newbalance}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth {value} Coins! Your new balance is {newbalance}.')
        elif ' '.join(fished_fish) == "Rock":
            rng = random.SystemRandom()
            value = rng.randint(1, 5)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                newbalance = int(balance) + value
                newvalues = { "$set": { "amt": f"{newbalance}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth {value} Coins! Your new balance is {newbalance}.')
        elif ' '.join(fished_fish) == "Wallet":
            rng = random.SystemRandom()
            value = rng.randint(30, 65)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                newbalance = int(balance) + value
                newvalues = { "$set": { "amt": f"{newbalance}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth {value} Coins! Your new balance is {newbalance}.')
        elif ' '.join(fished_fish) == "Oar Fish":
            rng = random.SystemRandom()
            value = rng.randint(45, 75)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                newbalance = int(balance) + value
                newvalues = { "$set": { "amt": f"{newbalance}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth {value} Coins! Your new balance is {newbalance}.')
        elif ' '.join(fished_fish) == "Funny Stupid Fish":
            rng = random.SystemRandom()
            value = rng.randint(60, 85)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                newbalance = int(balance) + value
                newvalues = { "$set": { "amt": f"{newbalance}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth {value} Coins! Your new balance is {newbalance}.')
        elif ' '.join(fished_fish) == "Salmon":
            rng = random.SystemRandom()
            value = rng.randint(55, 65)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                newbalance = int(balance) + value
                newvalues = { "$set": { "amt": f"{newbalance}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth {value} Coins! Your new balance is {newbalance}.')
        elif ' '.join(fished_fish) == "Sea Bunny":
            rng = random.SystemRandom()
            value = rng.randint(100, 200)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                newbalance = int(balance) + value
                newvalues = { "$set": { "amt": f"{newbalance}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth {value} Coins! Your new balance is {newbalance}.')
        elif ' '.join(fished_fish) == "Wedding Ring":
            rng = random.SystemRandom()
            value = rng.randint(150, 350)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                newbalance = int(balance) + value
                newvalues = { "$set": { "amt": f"{newbalance}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth {value} Coins! Your new balance is {newbalance}.')
        elif ' '.join(fished_fish) == "Ancient Evil Goblin That Steals your Coins":
            query = {"name": str(ctx.user.id)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                if int(balance) <= 1:
                    await ctx.send(f"You caught the {' '.join(fished_fish)}!\nHe tried to take half your coins, but you don't have any to take!")
                else: 
                    newbalance = int(balance)/2
                    roundedbalance = math.floor(newbalance)
                    newvalues = { "$set": { "amt": f"{roundedbalance}" }}
                    usercol.update_one(query, newvalues)
                    await ctx.send(f'You caught the **{' '.join(fished_fish)}**!\nHe took half your coins and now you have **{roundedbalance}**')
        
# Launch The Bot
print("Starting Bot....")
print("""   ___       _ ___       __    ___  ___  ___  ___ 
  / _ | ____(_) _ )___  / /_  / _ \\/ _ \\/ _ \\/ _ \\
 / __ |/ __/ / _  / _ \\/ __/  \\_, / // / // / // /
/_/ |_/_/ /_/____/\\___/\\__/  /___/\\___/\\___/\\___/ 
-------------------------------------------------------
https://arithefirst.com
""")
bot.start()