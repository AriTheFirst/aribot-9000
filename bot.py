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
import urllib.parse

# Grab bot token from enviroment
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CAT_TOKEN = os.getenv("CAT_TOKEN")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_SECRET")
bot = interactions.Client(token=TOKEN)

# Define Command Scopes
command_scopes = [752667089155915846, 1221655728029302865, 1172683672856567808]

# Function for setting embed colors
def embedcolor(hex_code):
    return int(hex_code.lstrip('#'), 16)

# MongoDB URLs and DB
dbclient = pymongo.MongoClient("mongodb://10.0.0.21:27017")
database = dbclient["aribot-currency"]

# Function for seperating numbers with commas
def comma_seperate(number_str):
    return "{:,}".format(int(number_str))

# API Lookups Function
def api_request(uid,returnfull: bool):
    url = f"https://discord.com/api/v10/users/{uid}"
    headers = {"Authorization": f"Bot {TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_dict = response.json() 
        username = response_dict['global_name']
        if username == None:
            username = response_dict['username']
        if returnfull == True:
            return response_dict
        else:
            return username
    else: 
        return "API Request Failure"
        print(f"API Request Failed with code {response.status_code}")

# Blurb to send when API Requests Fail
api_fail_msg = """\
Discord API Request Failed.
There could be multiple reasons for this:
- You pinged a role instead of a user
- You didn't ping the user but typed their name instead
- You typed nonsense into the input
- The Discord API Could be down (unlikely)"""

# ----------------- #
# Start of Commands #
# ----------------- #

# API Request Command
@bot.command(
    name="api",
    description="Get data on a user from Discord's API",
    options = [
        interactions.Option(
            name="user",
            description="The User to get the data of",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def api(ctx: interactions.CommandContext, user: str):
    userchecked = re.sub("[^0-9]", "", f"{user}")
    if api_request(userchecked,False) == "API Request Failure":
        await ctx.send(api_fail_msg,ephemeral=True)
    else:
        json_formatted_str = json.dumps(api_request(userchecked,True), indent=4, sort_keys=True)
        embed = interactions.Embed(
            title=f"{api_request(userchecked,False)}'s API Response",
            description=f"```json\n{json_formatted_str}```",
            color=embedcolor("#cba6f7")
        )
        await ctx.send(embeds=[embed])

# Avatar Command
@bot.command(
    name="avatar",
    description="Grab a user's avatar",
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
    if api_request(userchecked,True) == "API Request Failure":
        await ctx.send(api_fail_msg,ephemeral=True)
    else:
        avatar_url = f"https://cdn.discordapp.com/avatars/{userchecked}/{api_request(userchecked,True)['avatar']}.png?size=128"
        print(f"Got Avatar URL for User {userchecked}: {avatar_url}")
        embed = interactions.Embed(
            title=f"{api_request(userchecked,False)}'s avatar",
            image=interactions.EmbedImageStruct(url=f"{avatar_url}"),
            color=embedcolor("#cba6f7")
        )
        await ctx.send(embeds=[embed])

# Banner Command
@bot.command(
    name="banner",
    description="Grab a user's banner, and if they don't have nitro give it's hex code",
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
    if api_request(userchecked,True) == "API Request Failure":
        await ctx.send(api_fail_msg,ephemeral=True)
    else:
        username = api_request(userchecked,True)['global_name']
        banner_id = api_request(userchecked,True)['banner']
        banner_hex = api_request(userchecked,True)['banner_color']
        print(f"{banner_id}")
        if banner_id == None:
            print(f"{userchecked} does not have Nitro, Grabbing Hex Code....")
            if banner_hex == None:
                await ctx.send(f"<@{userchecked}> has no banner, nor a banner hex code.")
                print(f"Could not find banner or hex code for {userchecked}")
            else:
                print(f"Hex Code {banner_hex} found")
                hex_no_pound = re.sub('[^A-Za-z0-9]', '', banner_hex)
                embed = interactions.Embed(
                    title=f"{api_request(userchecked,False)}'s banner",
                    footer=interactions.EmbedFooter(text=f"{banner_hex}"),
                    image=interactions.EmbedImageStruct(url=f"https://singlecolorimage.com/get/{hex_no_pound}/600x240"),
                    color=embedcolor("#cba6f7")
                )
                await ctx.send(embeds=[embed])
        else:
            banner_url = f"https://cdn.discordapp.com/banners/{userchecked}/{banner_id}.png?size=4096"
            print(f"Got Banner URL for User {userchecked}: {banner_url}")
            embed = interactions.Embed(
                title=f"{api_request(userchecked,False)}'s banner",
                image=interactions.EmbedImageStruct(url=f"{banner_url}"),
                color=embedcolor("#cba6f7")
            )
            await ctx.send(embeds=[embed])

# Info Command
@bot.command(
    name="info",
    description="Give information about the bot",
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
)
async def cat(ctx: interactions.CommandContext):
    # Make Request to the Cat API
    url = "https://api.thecatapi.com/v1/images/search?limit=1&has_breeds=1"
    headers = {"x-api-key": CAT_TOKEN}
    response = requests.get(url, headers=headers)

    # Check if Request Failed
    if response.status_code == 200:
        print("Request successful!")
        answer = response.json()
        # Pull Response Data
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
    result = random.SystemRandom().randint(0, 1)
    if bet is None or wager is None:
        if result == 0:
            await ctx.send("The Coin landed on Heads!")
        else:
            await ctx.send("The Coin landed on Tails!")
    else:
        query = {"name": str(ctx.user.id)}
        usercol = database[f"server-{ctx.guild_id}"]
        answer = usercol.find_one(query)
        if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
        else:
            balance = answer.get("amt")
            if int(balance) < abs(int(wager)):
                await ctx.send(f"You wagered **{wager}** Coins,which is more than you have in your account.\nPlease try again.")
            else:
                # Win
                if bet.lower() == "tails" and result == 1 or bet.lower() == "heads" and result == 0:
                    newbalance = int(balance) + abs(int(wager))
                    newvalues = { "$set": { "amt": f"{newbalance}" }}
                    print(f"Win on {bet.lower()} for {ctx.user.id}: Balance = {newbalance}")
                    usercol.update_one(query, newvalues)
                    await ctx.send(f"You win! **{comma_seperate(abs(int(wager)))}** coins have been added to your account!\nYour new balance is **{comma_seperate(newbalance)}**!")
                # Lose          
                else:
                    newbalance = int(balance) - abs(int(wager))
                    newvalues = { "$set": { "amt": f"{newbalance}" }}
                    print(f"Lose on {bet.lower()} for {ctx.user.id}: Balance = {newbalance}")
                    usercol.update_one(query, newvalues)
                    await ctx.send(f"You Lose. **{comma_seperate(abs(int(wager)))}** coins have been removed from your account.\nYour new balance is **{comma_seperate(newbalance)}**!")

# Timezones Command
@bot.command(
    name="timezone",
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
async def timezone(ctx: interactions.CommandContext, timezone: str = None):
    if timezone is None:
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

# Checkbalance Command
@bot.command(
    name="checkbalance",
    description="Checks your balance",
    scope=command_scopes,
    options=[
        interactions.Option(
            name="user",
            description="user to check the balance of (optional)",
            type=interactions.OptionType.STRING,
            required=False
        ),
    ]
)
async def checkbal(ctx: interactions.CommandContext, user: str = None):
    if user == None:
            query = {"name": str(ctx.user.id)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            if answer == None:
                name = str(ctx.user.id)
                default_values = { "name": f"{name}", "amt": "100", "lastfished": "0"}
                inst = usercol.insert_one(default_values)
                print(f"Added Entry {inst.inserted_id}")
                await ctx.send("You couldn't be found in the database, so I take it this is your first time banking with us.\nHere's 100 Coins for free!")
            else:
                balance = answer.get("amt")
                formatted_blance = comma_seperate(balance)
                await ctx.send(f"Your balance is **{formatted_blance}** coins.")
    else: 
        userchecked = re.sub("[^0-9]", "", f"{user}")
        query = {"name": str(userchecked)}
        usercol = database[f"server-{ctx.guild_id}"]
        answer = usercol.find_one(query)
        if answer == None:
            await ctx.send(f"@<{userchecked}> dosen't have an account open.")
        else:
            balance = answer.get("amt")
            formatted_blance = comma_seperate(balance)
            await ctx.send(f"<@{userchecked}>'s balance is **{formatted_blance}** coins.")


# Setbalance Command
@bot.command(
    name="setbalance",
    description="Sets a user's balance",
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
            required=True,
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
        formatted_balance = "{:,}".format(int(amt))
        await ctx.send(f"<@{userchecked}>'s new balance was set to **{formatted_balance}** coins.")
    else:
        await ctx.send("This command can only be run by <@613358761901424652> herself.")

# Fish Command
@bot.command(
    name="fish",
    description="Go fishing",
    scope=command_scopes,
    )
async def fish(ctx: interactions.CommandContext):
    items = ['Old Boot', 'Rock', 'Wallet', 'Oar Fish', 'Funny Stupid Fish', 'Salmon', 'Sea Bunny', 'Wedding Ring', 'Mortimer: The Ancient Evil Goblin That Steals your Coins']
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

    query = {"name": str(ctx.user.id)}
    usercol = database[f"server-{ctx.guild_id}"]
    answer = usercol.find_one(query)
    roundtime = math.floor(time.time())
    lastfished = answer.get("lastfished")
    def convert_ms(total_seconds):
        minutes, seconds = divmod(total_seconds, 60)
        if minutes == 1:
            return '%d Minute and %02d Seconds' % (minutes, seconds)
        elif minutes == 0:
            return '%02d Seconds' % (seconds)
        else:
            return '%d Minutes and %02d Seconds' % (minutes, seconds)

    if roundtime - int(lastfished) <= 150:
        await ctx.send(f"The /fish command is on cooldown!\nYou have **{convert_ms(150-(math.floor(time.time())-int(lastfished)))}** left.")
    elif roundtime - int(lastfished) > 150:
        fished_fish = random.SystemRandom().choices(items, weights=normalized_probabilities, k=1)

        # Old Boot Code
        if ' '.join(fished_fish) == "Old Boot":
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                value = random.SystemRandom().randint(1, 10)
                balance = answer.get("amt")
                newbalance = int(balance) + value
                print(f"Current balance for {ctx.user.id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.')
        
        # Rock Code
        elif ' '.join(fished_fish) == "Rock":
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                value = random.SystemRandom().randint(1, 5)
                balance = answer.get("amt")
                newbalance = int(balance) + value
                print(f"Current balance for {ctx.user.id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.')
       
       # Wallet Code
        elif ' '.join(fished_fish) == "Wallet":
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                value = random.SystemRandom().randint(30, 65)
                balance = answer.get("amt")
                newbalance = int(balance) + value
                print(f"Current balance for {ctx.user.id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.')
        
        # Oar Fish Code
        elif ' '.join(fished_fish) == "Oar Fish":
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                value = random.SystemRandom().randint(45, 75)
                balance = answer.get("amt")
                newbalance = int(balance) + value
                print(f"Current balance for {ctx.user.id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.')
        
        # Funny Stupid Fish Code
        elif ' '.join(fished_fish) == "Funny Stupid Fish": 
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                value = random.SystemRandom().randint(60, 85)
                balance = answer.get("amt")
                newbalance = int(balance) + value
                print(f"Current balance for {ctx.user.id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.')
       
        # Salmon Code
        elif ' '.join(fished_fish) == "Salmon":
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                value = random.SystemRandom().randint(55, 65)
                balance = answer.get("amt")
                newbalance = int(balance) + value
                print(f"Current balance for {ctx.user.id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.')
       
        # Sea Bunny Code       
        elif ' '.join(fished_fish) == "Sea Bunny":
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                value = random.SystemRandom().randint(100, 200)
                balance = answer.get("amt")
                newbalance = int(balance) + value
                print(f"Current balance for {ctx.user.id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.')
        
        # Wedding Ring Code
        elif ' '.join(fished_fish) == "Wedding Ring":
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                value = random.SystemRandom().randint(150, 350)
                newbalance = int(balance) + value
                print(f"Current balance for {ctx.user.id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                await ctx.send(f'You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.')
    
        # Goblin Code
        elif ' '.join(fished_fish) == "Mortimer: The Ancient Evil Goblin That Steals your Coins":
            query = {"name": str(ctx.user.id)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
            else:
                balance = answer.get("amt")
                if int(balance) <= 1:
                    await ctx.send(f"You caught the {' '.join(fished_fish)}!\nHe tried to take half your coins, but you were too poor!")
                else: 
                    newbalance = int(balance)/2
                    roundedbalance = math.floor(newbalance)
                    newvalues = { "$set": { "amt": f"{roundedbalance}", "lastfished": f"{math.floor(time.time())}" }}
                    usercol.update_one(query, newvalues)
                    await ctx.send(f'You caught the **{' '.join(fished_fish)}**!\nHe took half your coins and now you have **{comma_seperate(roundedbalance)}**')

# Send Command
@bot.command(
    name="send",
    description="Sends money to another user",
    scope=command_scopes,
    options=[
        interactions.Option(
            name="user",
            description="User to send money to",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="amt",
            description="Amount of money to send",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ]
)
async def send(ctx: interactions.CommandContext, user: str = None, amt: int = None):
    userchecked = re.sub("[^0-9]", "", f"{user}")
    query_reciver = {"name": str(userchecked)}
    query_sender = {"name": str(ctx.user.id)}
    usercol = database[f"server-{ctx.guild_id}"]
    answer_reciver = usercol.find_one(query_reciver)
    answer_sender = usercol.find_one(query_sender)
    if answer_sender == None:
        await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
    elif answer_reciver == None:
        await ctx.send(f"<@{userchecked}> dosen't have a bank account with us! Tell them to run `/checkbalance`")
    else:
        reciver_balance = answer_reciver.get("amt")
        sender_balance = answer_sender.get("amt")
        if int(sender_balance) < abs(amt):
            await ctx.send(f"You tried to send **{abs(amt)}** Coins, which is more than you have in your account.\nPlease try again.")
        else:
            newbal_reciver = { "$set": { "amt": f"{int(reciver_balance)+abs(int(amt))}" }}
            newbal_sender = { "$set": { "amt": f"{int(sender_balance)-abs(int(amt))}" }}
            print(f"{ctx.user.id} sent {amt} coins to {userchecked}. {ctx.user.id} balance = {newbal_sender}, {userchecked} balance = {newbal_reciver}")
            usercol.update_one(query_sender, newbal_sender)
            usercol.update_one(query_reciver, newbal_reciver)
            embed = interactions.Embed(
                title=f"Bank Transfer ",
                description=f"<@{ctx.user.id}> Sent **{amt}** to <@{userchecked}>",
                color=embedcolor("#cba6f7"),
                fields=[
                    interactions.EmbedField(name=f"{api_request(ctx.user.id, False)}'s Balance:", value=f"{comma_seperate(int(sender_balance)-abs(int(amt)))}", inline=True),
                    interactions.EmbedField(name=f"{api_request(userchecked, False)}'s Balance:", value=f"{comma_seperate(int(reciver_balance)+abs(int(amt)))}", inline=True)
                ]
            )
            await ctx.send(embeds=[embed])

@bot.command(
    name="spotify",
    description="Searches Spotify through the Spotify API",
    scope=command_scopes,
    options=[
        interactions.Option(
            name="query",
            description="Search Query",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ]
)
async def spotify(ctx: interactions.CommandContext, query: str = None):
    keygen_url = "https://accounts.spotify.com/api/token"
    keygen_headers = {"Content-Type": "application/x-www-form-urlencoded",}
    keygen_data = {
    "grant_type": "client_credentials",
    "client_id": "80b7971a22ec46358240b5bde22180a4",
    "client_secret": f"{SPOTIFY_CLIENT_SECRET}",
    }

    keygen_request = requests.post(keygen_url, headers=keygen_headers, data=keygen_data)
    spotify_api_key = keygen_request.json()["access_token"]

    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    headers = {'Authorization': f'Bearer {spotify_api_key}',}
    request = requests.get(url, headers=headers)
    reply = request.json()
    
    embed = interactions.Embed(
        title=f"Search Result ",
        description=f'<@{ctx.user.id}> searched for "{query}"',
        color=embedcolor("#cba6f7"),
        thumbnail=interactions.EmbedImageStruct(url=reply['tracks']['items'][0]['album']['images'][0]['url']),
        fields=[
            interactions.EmbedField(name=f"Album Title", value=reply['tracks']['items'][0]['album']['name'], inline=False),
            interactions.EmbedField(name=f"Album Artist", value=reply['tracks']['items'][0]['album']['artists'][0]['name'], inline=False),
            interactions.EmbedField(name=f"Track URL", value=reply['tracks']['items'][0]['external_urls']['spotify'], inline=False),
        ]
    )
    await ctx.send(embeds=[embed])



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