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
import fishing

# Import various tokens and API Keys
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CAT_TOKEN = os.getenv("CAT_TOKEN")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_SECRET")
YOUTUBE_TOKEN = os.getenv("YOUTUBE_KEY")
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
@interactions.slash_command(
    name="api",
    description="Get data on a user from Discord's API",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="user",
    description="User to get the data of",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def api(ctx: interactions.SlashContext, user: str):
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
@interactions.slash_command(
    name="avatar",
    description="Grab a user's avatar",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="user",
    description="User to get the avatar of",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def avatar(ctx: interactions.SlashContext, user: str):
    userchecked = re.sub("[^0-9]", "", f"{user}")
    if api_request(userchecked,True) == "API Request Failure":
        await ctx.send(api_fail_msg,ephemeral=True)
    else:
        avatar_url = f"https://cdn.discordapp.com/avatars/{userchecked}/{api_request(userchecked,True)['avatar']}.png?size=128"
        print(f"Got Avatar URL for User {userchecked}: {avatar_url}")
        embed = interactions.Embed(
            title=f"{api_request(userchecked,False)}'s avatar",
            color=embedcolor("#cba6f7")
        )
        embed.set_image(avatar_url)
        await ctx.send(embeds=[embed])

# Banner Command
@interactions.slash_command(
    name="banner",
    description="Grab a user's banner, and if they don't have nitro give it's hex code",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="user",
    description="User to get the banner of",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def banner(ctx: interactions.SlashContext, user: str):
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
                    color=embedcolor("#cba6f7")
                )
                embed.set_image(f'https://singlecolorimage.com/get/{hex_no_pound}/600x240')
                await ctx.send(embeds=[embed])
        else:
            banner_url = f"https://cdn.discordapp.com/banners/{userchecked}/{banner_id}.png?size=4096"
            print(f"Got Banner URL for User {userchecked}: {banner_url}")
            embed = interactions.Embed(
                title=f"{api_request(userchecked,False)}'s banner",
                color=embedcolor("#cba6f7")
            )
            embed.set_image(banner_url)
            await ctx.send(embeds=[embed])

# Info Command
@interactions.slash_command(
    name="info",
    description="Give information about the bot",
    scopes=command_scopes,
)
async def info(ctx: interactions.SlashContext):
    await ctx.send("**## [Aribot 9000](https://github.com/AriTheFirst/aribot-9000): By [arithefirst](https://arithefirst.com)**Written in python using [interactions.py](https://github.com/interactions-py) for Discord API and [MongoDB](https://www.mongodb.com/) for storing data of the currency system")

# Ping Commang
@interactions.slash_command(
    name="ping",
    description="Sends Pong",
    scopes=command_scopes,
)
async def ping(ctx: interactions.SlashContext):
    await ctx.send('Pong!')

# Cat Command
@interactions.slash_command(
    name="cat",
    description="Sends a random cat",
    scopes=command_scopes,
)
async def cat(ctx: interactions.SlashContext):
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
        embed = interactions.Embed(
            title=f"Check out this {breed} cat!",
            color=embedcolor("#cba6f7")
        )
        embed.add_image(cat_url)
        await ctx.send(embeds=[embed])
    else:
        print(f"API Request Failed with code {response.status_code}")
        await ctx.send(f"Error Communicating with https://thecatapi.com/v1/images/search/ ({response.status_code})")

# Coinflip Command
@interactions.slash_command(
    name="coinflip",
    description="Flips a Coin",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="wager",
    description="Amount of coins to wager",
    required=True,
    opt_type=interactions.OptionType.INTEGER
)
@interactions.slash_option(
    name="bet",
    description="Heads or Tails",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def coinflip(ctx: interactions.SlashContext, bet: str = None, wager: int = None):
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
@interactions.slash_command(
    name="timezone",
    description="Send the time in the 4 Major US Timezones, Optionally specify an extra timezone",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="timezone",
    description="An optional extra timezone to get the time of (in Continent/City format)",
    opt_type=interactions.OptionType.STRING,
    required=False,
)
async def timezone(ctx: interactions.SlashContext, timezone: str = None):
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
@interactions.slash_command(
    name="identify",
    description="Gives you your user id and this server's id",
    scopes=command_scopes,
)
async def identify(ctx: interactions.SlashContext):
    await ctx.send(f'**User ID:** {ctx.user.id}\n**Guild ID:** {ctx.guild_id}')

# Checkbalance Command
@interactions.slash_command(
    name="checkbalance",
    description="Checks your balance",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="user",
    description="user to check the balance of",
    required=False,
    opt_type=interactions.OptionType.STRING
)
async def checkbal(ctx: interactions.SlashContext, user: str = None):
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
@interactions.slash_command(
    name="setbalance",
    description="Sets a user's balance",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="user",
    description="User to modify the balance of",
    required=False,
    opt_type=interactions.OptionType.STRING
)
@interactions.slash_option(
    name="amt",
    description="New Balance for the user",
    required=False,
    opt_type=interactions.OptionType.INTEGER
)
async def setbalance(ctx: interactions.SlashContext, user: str, amt: int):
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
@interactions.slash_command(
    name="fish",
    description="Go fishing",
    scopes=command_scopes,
    )
async def fish(ctx: interactions.SlashContext):
    fish_reply = fishing.load_fishing(ctx.user.id, ctx.guild_id)
    await ctx.send(fish_reply)

# Send Command
@interactions.slash_command(
    name="send",
    description="Sends money to another user",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="user",
    description="User to send money to",
    required=True,
    opt_type=interactions.OptionType.STRING
)
@interactions.slash_option(
    name="amt",
    description="Amount of money to send",
    required=True,
    opt_type=interactions.OptionType.INTEGER
)
async def send(ctx: interactions.SlashContext, user: str = None, amt: int = None):
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

# Leaderboard Command
@interactions.slash_command(
    name="leaderboard",
    description="Display server leaderboard",
    scopes=command_scopes,
    )
async def Leaderboard(ctx: interactions.SlashContext):
    query = {"name": ""}
    usercol = database[f"server-{ctx.guild_id}"]
    cursor = usercol.find({}, {"name": 1, "amt": 1, "_id": 0})
    documents = list(cursor)
    sorted_documents = sorted(documents, key=lambda x: int(x['amt']), reverse=True)
    documents_str = '\n'.join(f"**{i+1}**) <@{doc['name']}> - **{doc['amt']}**" for i, doc in enumerate(sorted_documents))
    embed = interactions.Embed(
        title="Leaderboard",
        color=embedcolor("#cba6f7"),
        description=f"{documents_str}"
    )
    await ctx.send(embeds=[embed])

# Help Command
@interactions.slash_command(
    name = "help",
    description = "Gives command help",
    scopes=command_scopes,
)
async def help (ctx: interactions.SlashContext):
    embed = interactions.Embed(
        title="Commands List",
        color=embedcolor("#cba6f7"),
        description="**1)** API\n**2)** Avatar\n**3)** Banner\n**4)** Cat\n**5)** Checkbalance\n**6)** Coinflip\n**7)** Fish\n**8)** Leaderboard\n**9)** Ping\n**10)** Identify\n**11)** Info\n**12)** Send\n**13)** Timezone"
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