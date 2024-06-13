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
command_scopes = [752667089155915846, 1221655728029302865, 1172683672856567808, 1246819071513722900]

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
    # Take the "<@>" out of the user ping
    userchecked = re.sub("[^0-9]", "", f"{user}")
    # Make sure get request dosen't fail
    if api_request(userchecked,False) == "API Request Failure":
        await ctx.send(api_fail_msg,ephemeral=True)
    else:
        # Format the API Response
        json_formatted_str = json.dumps(api_request(userchecked,True), indent=4, sort_keys=True)
        embed = interactions.Embed(
            title=f"{api_request(userchecked,False)}'s API Response",
            description=f"```json\n{json_formatted_str}```",
            color=embedcolor("#cba6f7")
        )
        # Send the API Response
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
    # Take the "<@>" out of the user ping
    userchecked = re.sub("[^0-9]", "", f"{user}")
    # Make sure get request dosen't fail
    if api_request(userchecked,False) == "API Request Failure":
        await ctx.send(api_fail_msg,ephemeral=True)
    else:
        # Extract the avatar url from the API Response
        avatar_url = f"https://cdn.discordapp.com/avatars/{userchecked}/{api_request(userchecked,True)['avatar']}.png?size=128"
        print(f"Got Avatar URL for User {userchecked}: {avatar_url}")
        embed = interactions.Embed(
            title=f"{api_request(userchecked,False)}'s avatar",
            color=embedcolor("#cba6f7")
        )
        embed.set_image(avatar_url)
        # Send Embed
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
    # Take the "<@>" out of the user ping
    userchecked = re.sub("[^0-9]", "", f"{user}")
    # Make sure get request dosen't fail
    if api_request(userchecked,True) == "API Request Failure":
        await ctx.send(api_fail_msg,ephemeral=True)
    else:
        username = api_request(userchecked,True)['global_name']
        banner_id = api_request(userchecked,True)['banner']
        banner_hex = api_request(userchecked,True)['banner_color']
        print(f"{banner_id}")
        # Check if the user has a Nitro Banner
        if banner_id == None:
            print(f"{userchecked} does not have Nitro, Grabbing Hex Code....")
            if banner_hex == None:
                # Return an error if a user has no banner and no hex code
                await ctx.send(f"<@{userchecked}> has no banner, nor a banner hex code.")
                print(f"Could not find banner or hex code for {userchecked}")
            else:
                # Get color code if user dosen't have a Nitro Banner
                print(f"Hex Code {banner_hex} found")
                hex_no_pound = re.sub('[^A-Za-z0-9]', '', banner_hex)
                embed = interactions.Embed(
                    title=f"{api_request(userchecked,False)}'s banner",
                    footer=interactions.EmbedFooter(text=f"{banner_hex}"),
                    color=embedcolor("#cba6f7")
                )
                # Set hex code embed image
                embed.set_image(f'https://singlecolorimage.com/get/{hex_no_pound}/600x240')
                await ctx.send(embeds=[embed])
        else:
            # Set the banner url using the response from the Discord API
            banner_url = f"https://cdn.discordapp.com/banners/{userchecked}/{banner_id}.png?size=4096"
            print(f"Got Banner URL for User {userchecked}: {banner_url}")
            embed = interactions.Embed(
                title=f"{api_request(userchecked,False)}'s banner",
                color=embedcolor("#cba6f7")
            )
            embed.set_image(banner_url)
            # Send Embed
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
)
async def ping(ctx: interactions.SlashContext):
    await ctx.send('Pong!')

# Cat Command
@interactions.slash_command(
    name="cat",
    description="Sends a random cat",
)
async def cat(ctx: interactions.SlashContext):
    # Make Request to the Cat API
    url = "https://api.thecatapi.com/v1/images/search?limit=1&has_breeds=1"
    # Get the API Key from the ENV
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
        # Add the breed name to the embed
        embed = interactions.Embed(
            title=f"Check out this {breed} cat!",
            color=embedcolor("#cba6f7")
        )
        embed.add_image(cat_url)
        # Send Embed
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
    name="bet",
    description="Heads or Tails",
    required=False,
    opt_type=interactions.OptionType.STRING
)
@interactions.slash_option(
    name="wager",
    description="Amount of coins to wager",
    required=False,
    opt_type=interactions.OptionType.INTEGER
)
async def coinflip(ctx: interactions.SlashContext, bet: str = None, wager: int = None):
    result = random.SystemRandom().randint(0, 1)
    # Non-betting Coinflip
    if bet is None or wager is None:
        if result == 0:
            await ctx.send("The Coin landed on Heads!")
        else:
            await ctx.send("The Coin landed on Tails!")
    # Betting Coinflip
    else:
        # Check if user has bank account
        query = {"name": str(ctx.user.id)}
        usercol = database[f"server-{ctx.guild_id}"]
        answer = usercol.find_one(query)
        if answer == None:
                await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
        else:
            # Check if user wagered more than they have
            balance = answer.get("amt")
            if int(balance) < abs(int(wager)):
                await ctx.send(f"You wagered **{wager}** Coins,which is more than you have in your account.\nPlease try again.")
            else:
                # Win Condition
                if bet.lower() == "tails" and result == 1 or bet.lower() == "heads" and result == 0:
                    newbalance = int(balance) + abs(int(wager))
                    newvalues = { "$set": { "amt": f"{newbalance}" }}
                    print(f"Win on {bet.lower()} for {ctx.user.id}: Balance = {newbalance}")
                    usercol.update_one(query, newvalues)
                    await ctx.send(f"You win! **{comma_seperate(abs(int(wager)))}** coins have been added to your account!\nYour new balance is **{comma_seperate(newbalance)}**!")
                # Lose Condition    
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
# Im ngl i dont know wtf is going on in here i made this one at like 4AM
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
        embed = interactions.Embed(
            title="Major US Timezones",
            color=embedcolor("#cba6f7"),
            description=f"{times}",
            )
        await ctx.send(embeds=[embed])
    else:
        try:
            tz_obj = pytz.timezone(timezone)
            current_time = datetime.now(tz_obj)
            embed = interactions.Embed(
                title="User-Specified Timezone",
                color=embedcolor("#cba6f7"),
            description=f"The time in **{timezone}** is {current_time.strftime('%B %d, %Y %H:%M')}"
            )
            await ctx.send(embeds=[embed])
        except pytz.exceptions.UnknownTimeZoneError:
            await ctx.send("Invalid timezone provided.\nPlease use [TZ Database Formatting](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)")

# Identify Command
@interactions.slash_command(
    name="identify",
    description="Gives you your user id and this server's id",
    scopes=command_scopes,
)
async def identify(ctx: interactions.SlashContext):
    # Get and print UID and Guild ID
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
    # Code for if no external user is specified
    if user == None:
            query = {"name": str(ctx.user.id)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            # Check for account
            if answer == None:
                # Make account if user dosen't have one
                name = str(ctx.user.id)
                default_values = { "name": f"{name}", "amt": "100", "lastfished": "0", "rod": "0", "lance": "0", "tmcn": "0",}
                inst = usercol.insert_one(default_values)
                print(f"Added Entry {inst.inserted_id}")
                await ctx.send("You couldn't be found in the database, so I take it this is your first time banking with us.\nHere's 100 Coins for free!")
            else:
                # Get and send user balane if they have one
                balance = answer.get("amt")
                formatted_blance = comma_seperate(balance)
                await ctx.send(f"Your balance is **{formatted_blance}** coins.")
    # Code for when external user is specified
    else: 
        # Checks if the user wants to look for mortimer
        if user.lower() == "mortimer":
            query = {"name_nonuser": "mortimer"}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            if answer == None:
                await ctx.send("No one here has caught Mortimer yet, so his balance is **0** coins.")
            else:
                balance = answer.get("amt")
                await ctx.send(f"Mortimer's balance is **{comma_seperate(balance)}** coins.")
        else:
            userchecked = re.sub("[^0-9]", "", f"{user}")
            query = {"name": str(userchecked)}
            usercol = database[f"server-{ctx.guild_id}"]
            answer = usercol.find_one(query)
            # Check if they have an account
            if answer == None:
                # Send an error if they don't
                await ctx.send(f"@<{userchecked}> dosen't have an account open.")
            else:
                # Send user balance if they do
                balance = answer.get("amt")
                await ctx.send(f"<@{userchecked}>'s balance is **{comma_seperate(balance)}** coins.")

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
async def setbalance(ctx: interactions.SlashContext, user: str, amt: int, goblin: bool = False):
    # Check to make sure the user running the command is me (owner of the bot)
    if ctx.user.id == 613358761901424652:
        # Take the "<@>" out of the user ping
        userchecked = re.sub("[^0-9]", "", f"{user}")
        # Check if the user is set as mortimer for manually setting his balance
        if user.lower() == "mortimer":
            query = {"name_nonuser": "mortimer"}
            pingname = "Mortimer"
        else:
            query = {"name": f"{userchecked}"}
            pingname = f"<@{userchecked}>"
        usercol = database[f"server-{ctx.guild_id}"]
        newvalue = { "$set": { "amt": f"{amt}" }}
        # Write new balance to DB
        usercol.update_one(query, newvalue)
        formatted_balance = "{:,}".format(int(amt))
        await ctx.send(f"{pingname}'s new balance was set to **{formatted_balance}** coins.")
    # If command runner is not me, send an error message
    else:
        await ctx.send("This command can only be run by <@613358761901424652> herself.")

# Fish Command
@interactions.slash_command(
    name="fish",
    description="Go fishing",
    scopes=command_scopes,
    )
async def fish(ctx: interactions.SlashContext):
    # Call the load_fishing() funciton from fishing.py
    fish_reply = fishing.load_fishing(ctx.user.id, ctx.guild_id)
    if fish_reply == "lance_true":
                # Setup the Dropdown
        select_menu = interactions.StringSelectMenu(
            "Left", "Right",
            placeholder="Which way do you stab?",
            min_values=1,
            max_values=1,
            custom_id="duel_selection",
        )

        # Create Embed
        embed = interactions.Embed(
            title="Mortimer Duel",
            color=embedcolor("#cba6f7"),
            description=f"""You caught **Mortimer, The Ancient Evil Goblin That Steals Your Coins**! He \
was about to take your coins, but you challenged him to a duel! He will pick a random direction to jump to \
avoid your sword. If he jumps to the same direction you stab, you win and take all of his coins! If he \
jumps the opposite way, you loose, and he takes 25% of your coins!"""
        )
        embed.set_thumbnail(url="https://raw.githubusercontent.com/arithefirst/aribot-9000/main/images/fishing/placeholder.png")

        # Send Embed
        message = await ctx.send(embeds=[embed])
        dropdown = await ctx.send(components=[select_menu], ephemeral=True)
        dropdown_id = dropdown.id

        # Query MongoDB
        gobquery = {"name_nonuser": "mortimer"}
        query = {"name": str(ctx.user.id)}
        usercol = database[f"server-{ctx.guild_id}"]
        gobanswer = usercol.find_one(gobquery)
        answer = usercol.find_one(query)
        gobbalance = gobanswer.get("amt")
        balance = answer.get("amt")

        # Set the check to always return true
        SelectMenuEvent = None
        async def check(event: SelectMenuEvent) -> bool:
            return True

        try:
            # Wait for the Select Menu interaction
            used_option: SelectMenuEvent = await bot.wait_for_component(components=select_menu, check=check, timeout=60)
            print(f"Selected Option: {used_option.ctx.values[0]}")

        except TimeoutError:
            # Runs on timeout (60s)
            print("Timed Out!")
            select_menu.disabled = True
            await message.edit(components=[select_menu])
            await ctx.send("Interaction Timed out; 50% of your coins have been taken by default.")
            # Half user's coins
            newvalue = { "$set": { "amt": f"{int(balance)/2}" }}
            usercol.update_one(query, newvalue)

        # Check to see which way user picked
        if used_option.ctx.values[0] == "Left" and random.SystemRandom().randint(0, 1) == 0 or used_option.ctx.values[0] == "Right" and random.SystemRandom().randint(0, 1) == 1:
            print("User won")
            # Set Goblin Balance to 0
            goblin_new_values = { "$set": {"amt": "0",}}
            usercol.update_one(gobquery, goblin_new_values)
            # Set new user balance
            newvalues = { "$set": { "amt": f"{int(gobbalance)+int(balance)}" }}
            usercol.update_one(query, newvalues)
            embed = interactions.Embed(
                title="Mortimer Duel",
                color=embedcolor("#cba6f7"),
                description=f"You won the Duel!\nYou took all of Mortimer's coins, and now you have **{comma_seperate(int(gobbalance)+int(balance))}**"
            )
            embed.set_thumbnail(url="https://raw.githubusercontent.com/arithefirst/aribot-9000/main/images/fishing/placeholder.png")
            # Send new embed and delete dropdown
            await message.edit(embeds=[embed])
            await ctx.delete(dropdown_id)
        else:
            # Set new goblin balance
            goblin_new_values = { "$set": {"amt": f"{math.floor(int(gobbalance)+(int(balance)*0.25))}"}}
            usercol.update_one(gobquery, goblin_new_values)
            # Set new user balance
            newvalues = { "$set": { "amt": f"{math.floor(int(balance)*0.75)}" }}
            usercol.update_one(query, newvalues)
            embed = interactions.Embed(
                title="Mortimer Duel",
                color=embedcolor("#cba6f7"),
                description=f"You lost the Duel.\nMortimer took 25% of your coins! You now have **{comma_seperate(math.floor(int(balance)*0.75))}** Coins"
            )
            embed.set_thumbnail(url="https://raw.githubusercontent.com/arithefirst/aribot-9000/main/images/fishing/placeholder.png")
            # Send new embed and delete dropdown
            await message.edit(embed=[embed])
            await ctx.delete(dropdown_id)
    else:
        await ctx.send(embeds=fish_reply)

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
    # Query the sender and reciver balances
    query_reciver = {"name": str(userchecked)}
    query_sender = {"name": str(ctx.user.id)}
    usercol = database[f"server-{ctx.guild_id}"]
    answer_reciver = usercol.find_one(query_reciver)
    answer_sender = usercol.find_one(query_sender)
    # Check to make sure both users have bank accounts
    if answer_sender == None:
        await ctx.send("You don't have a bank account with us! Please run `/checkbalance`")
    elif answer_reciver == None:
        await ctx.send(f"<@{userchecked}> dosen't have a bank account with us! Tell them to run `/checkbalance`")
    else:
        reciver_balance = answer_reciver.get("amt")
        sender_balance = answer_sender.get("amt")
        # Make sure sender dosen't try to send more than they have
        if int(sender_balance) < abs(amt):
            await ctx.send(f"You tried to send **{abs(amt)}** Coins, which is more than you have in your account.\nPlease try again.")
        else:
            # Set new balances for sender and reciver
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
            # Send Embed
            await ctx.send(embeds=[embed])

# Leaderboard Command
@interactions.slash_command(
    name="leaderboard",
    description="Display server leaderboard",
    scopes=command_scopes,
    )
async def Leaderboard(ctx: interactions.SlashContext):
    # Look through every document with the "name" property
    query = {"name": {"$exists": True}}    
    usercol = database[f"server-{ctx.guild_id}"]
    cursor = usercol.find(query, {"name": 1, "amt": 1, "_id": 0})
    documents = list(cursor)
    # Sort Documents
    sorted_documents = sorted(documents, key=lambda x: int(x['amt']), reverse=True)
    # Add some formatting so it looks pretty
    documents_str = '\n'.join(f"**{i+1}**) <@{doc['name']}> - **{doc['amt']}**" for i, doc in enumerate(sorted_documents))
    embed = interactions.Embed(
        title="Leaderboard",
        color=embedcolor("#cba6f7"),
        description=f"{documents_str}"
    )
    # Send Embed
    await ctx.send(embeds=[embed])

# Help Command
@interactions.slash_command(
    name = "help",
    description = "Gives command help",
    scopes=command_scopes,
)
@interactions.slash_option(
    name="command",
    description="Specific command to get help with",
    required=False,
    opt_type=interactions.OptionType.STRING,
    choices=[
        # Set all of the options you can choose from
        interactions.SlashCommandChoice(name="API", value="API"),
        interactions.SlashCommandChoice(name="Avatar", value="Avatar"),
        interactions.SlashCommandChoice(name="Banner", value="Banner"),
        interactions.SlashCommandChoice(name="Cat", value="Cat"),
        interactions.SlashCommandChoice(name="Checkbalance", value="Checkbalance"),
        interactions.SlashCommandChoice(name="Fish", value="Fish"),
        interactions.SlashCommandChoice(name="Leaderboard", value="Leaderboard"),
        interactions.SlashCommandChoice(name="Ping", value="Ping"),
        interactions.SlashCommandChoice(name="Identify", value="Identify"),
        interactions.SlashCommandChoice(name="Info", value="Info"),
        interactions.SlashCommandChoice(name="Send", value="Send"),
        interactions.SlashCommandChoice(name="Timezone", value="Timezone"),
    ]
)
async def help (ctx: interactions.SlashContext, command: str = None):
    if command == None:
        commands_list = """\
        **1)** API
        **2)** Avatar
        **3)** Banner
        **4)** Cat
        **5)** Checkbalance
        **6)** Coinflip
        **7)** Fish
        **8)** Leaderboard
        **9)** Ping
        **10)** Identify
        **11)** Info
        **12)** Send
        **13)** Timezone"""

        embed = interactions.Embed(
            title="Commands List",
            color=embedcolor("#cba6f7"),
            description=commands_list
        )
        await ctx.send(embeds=[embed])
    # /api help
    elif command.lower() == "api":
        embed = interactions.Embed(
            title="API Command",
            color=embedcolor("#cba6f7"),
            description="The API command gets data on a certain user from the Discord API.\
                        This data includes the UID, Username, Avatar ID, Public Flags, Flags\
                        , Banner ID, Profile Accent Color, Global Name, Avatar Decoration Data\
                        , Banner Color, and Clan Data.",
            fields=[interactions.EmbedField(name=f"Inputs:", value="**User** -- The User to get the API Data of (Ping or User ID)", inline=True),]
        )
        await ctx.send(embeds=[embed])
    # /avatar help
    elif command.lower() == "avatar":
        embed = interactions.Embed(
            title="Avatar Command",
            color=embedcolor("#cba6f7"),
            description="The Avatar Command gets and displays a specified user's avatar.",
            fields=[interactions.EmbedField(name=f"Inputs:", value="**User** -- The User to get the avatar of (Ping or User ID)", inline=True),]
        )
        await ctx.send(embeds=[embed])
    # /banner help
    elif command.lower() == "banner":
        embed = interactions.Embed(
            title="Banner Command",
            color=embedcolor("#cba6f7"),
            description="The Bannner Command gets and displays a specified user's avatar.",
            fields=[interactions.EmbedField(name=f"Inputs:", value="**User** -- The User to get the banenr of (Ping or User ID)", inline=True),]
        )
        await ctx.send(embeds=[embed])
        # /cat help
    elif command.lower() == "cat":
        embed = interactions.Embed(
            title="Cat Command",
            color=embedcolor("#cba6f7"),
            description="The Cat Command sends a random cat.",
        )
        await ctx.send(embeds=[embed])

        # /checkbalance help
    elif command.lower() == "checkbalance":
        embed = interactions.Embed(
            title="Check Balance Command",
            color=embedcolor("#cba6f7"),
            description="The Check Balance Command shows you your, or a specified user's, current account\
                        balance. This command can also be run to initalize an account for a user who does not \
                        have one.",
            fields=[interactions.EmbedField(name=f"Inputs:", value="**User (Optional)** -- The User to get the balance of (Ping or User ID)", inline=True),]
        )
        await ctx.send(embeds=[embed])
        # /coinflip help
    elif command.lower() == "coinflip":
        embed = interactions.Embed(
            title="Coinflip Command",
            color=embedcolor("#cba6f7"),
            description="The coinflip command will flip a coin. It optionally allows users to bet coins on the output of the coinflip.",
            fields=[interactions.EmbedField(name=f"Inputs:", value="""\
                **Wager (Optional)** -- Amount of money to wager on your selected outcome
                **Bet (Optional)** -- Which coinflip outcome you want to bet on
                """, inline=True),]
        )
        await ctx.send(embeds=[embed])
        # /fish help
    elif command.lower() == "fish":
        embed = interactions.Embed(
            title="Fish Command",
            color=embedcolor("#cba6f7"),
            description="The Fish command lets you go fishing. Fishing can reel in one of many different items that have a wide range value.",
            )
        await ctx.send(embeds=[embed])
        # /leaderboard help
    elif command.lower() == "leaderboard":
        embed = interactions.Embed(
            title="Leaderboard Command",
            color=embedcolor("#cba6f7"),
            description="The Leaderboard Command shows the server currency leaderboard, with the person with the most coins on top, and the person with the least on the bottom.",
            )
        await ctx.send(embeds=[embed])
        # /ping help
    elif command.lower() == "ping":
        embed = interactions.Embed(
            title="Ping Command",
            color=embedcolor("#cba6f7"),
            description='Sends a "Pong!"',
            )
        await ctx.send(embeds=[embed])
        # /identify help
    elif command.lower() == "identify":
        embed = interactions.Embed(
            title="Identify Command",
            color=embedcolor("#cba6f7"),
            description='The Identify Command returns your Discord User ID and the Guild ID of the server you ran the command in.',
            )
        await ctx.send(embeds=[embed])
        # /info help
    elif command.lower() == "info":
        embed = interactions.Embed(
            title="Info Command",
            color=embedcolor("#cba6f7"),
            description="The Info Command returns some information about Aribot and it's developer.",
            )
        await ctx.send(embeds=[embed])
        # /send help
    elif command.lower() == "send":
        embed = interactions.Embed(
            title="Send Command",
            color=embedcolor("#cba6f7"),
            description="The Send Command allows you to transfer some of your coins to another user.",
            fields=[interactions.EmbedField(name=f"Inputs:", value="""\
                **User** -- The User to send your money to (Ping or User ID)
                **Amt** -- The amount of Money to send
                """, inline=True),]
        )
        await ctx.send(embeds=[embed])
        # /timezone help
    elif command.lower() == "timezone":
        embed = interactions.Embed(
            title="Timezone Command",
            color=embedcolor("#cba6f7"),
            description="The Timezone displays the current time in the 4 Continental US Time zones, or optionally lets you specify another timezone in TZ Database format..",
            fields=[interactions.EmbedField(name=f"Inputs:", value="**Timezone** -- The optional timezone to get the time of ([TZ Database Format](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))", inline=True),]
        )
        await ctx.send(embeds=[embed])
# Shop Show Command
@interactions.slash_command(
    name="shop",
    scopes=command_scopes,
    sub_cmd_name="show",
    sub_cmd_description="Show the Shop"
    )
async def test(ctx: interactions.SlashContext):
    embed = interactions.Embed(
        title="Shop Items",
        color=embedcolor("#cba6f7"),
        description="**Jousting Lance** -- **3,000** Coins\n**Fishing Rod** -- **5,000** Coins\n**Time Machine** -- **10,000** Coins",
        footer="Run '/shop more {item}' for more info on an item"
    )
    await ctx.send(embeds=[embed])

# Shop More Command
@interactions.slash_command(
    name="shop",
    description="Show the Shop",
    sub_cmd_name="more",
    sub_cmd_description="Get more info on an item",
    scopes=command_scopes
)
@interactions.slash_option(
    name="item",
    description="Item to see details of",
    required=True,
    opt_type=interactions.OptionType.INTEGER,
    choices=[
        interactions.SlashCommandChoice(name="Jousting Lance", value=1),
        interactions.SlashCommandChoice(name="Fishing Rod", value=2),
        interactions.SlashCommandChoice(name="Time Machine", value=3)
    ]
)
async def more(ctx: interactions.SlashContext, item: int = None):
    if item == None:
        await ctx.send("Please enter a valid item.",ephemeral=true)
    elif item == 1:
        embed = interactions.Embed(
            title="Jousting Lance",
            color=embedcolor("#cba6f7"),
            description="""The Jousting Lance costs 3,000 coins, and can be used to fight off \
Mortimer the Goblin whenever you fish him up. Upon catching \
Mortimer, you will be presented with a small minigame where you \
choose to either stab left or stab right. Mortimer will randomly \
pick an option to try to dodge this attack. If he fails to dodge, \
you win the fight, and you gain all of the coins that he has taken from \
everybody in the server. If you loose, he will still take your coins, but only \
25% of them instead of the normal 50%.""",
            footer="Run '/shop buy Jousting Lance' to purchase this item"
        )
        await ctx.send(embeds=[embed])
    elif item == 2:
        embed = interactions.Embed(
            title="Fishing Rod",
            color=embedcolor("#cba6f7"),
            description="""The Fishing Rod costs 5,000, and is made of \
a special bait-infused titanium. Because of this, this rod prevents you \
from hooking things like rocks and boots on the line, and lets you catch many new types of fish!""",
            footer="Run '/shop buy Fishing Rod' to purchase this item"
        )
        await ctx.send(embeds=[embed])
    elif item == 3:
        embed = interactions.Embed(
            title="Time Machine",
            color=embedcolor("#cba6f7"),
            description="""This revolutionary new piece of fishing technology costs 10,000 coins, \
and attatches to your fishing rod. Every time you hook a fish, time is sped up by 2 minutes, effectively reducing your cooldown to only 30s.""",
            footer="Run '/shop buy Time Machine' to purchase this item"
        )
        await ctx.send(embeds=[embed])

# Shop Buy Command
@interactions.slash_command(
    name="shop",
    description="Purchase an item",
    sub_cmd_name="buy",
    sub_cmd_description="Purchase an item",
    scopes=command_scopes
)
@interactions.slash_option(
    name="item",
    description="Item to purchase",
    required=True,
    opt_type=interactions.OptionType.INTEGER,
    choices=[
        interactions.SlashCommandChoice(name="Jousting Lance", value=1),
        interactions.SlashCommandChoice(name="Fishing Rod", value=2),
        interactions.SlashCommandChoice(name="Time Machine", value=3)
    ]
)
async def buy(ctx: interactions.SlashContext, item: int = None):
    # Query MongoDB
    query = {"name": str(ctx.user.id)}
    usercol = database[f"server-{ctx.guild_id}"]
    answer = usercol.find_one(query)
    # Make itemcost and purchase_grammar global
    global purchase_grammar
    purchase_grammar = None
    global itemcost
    itemcost = None
    global item_id
    item_id = None

    # Make sure the user has an account
    if answer == None:
            await ctx.send("You do not have an account open. Run `/checkbalance` to create one.")
    else:
        # Make sure the user dosen't already own the item
        if item == 1 and int(answer.get("lance")) == 1:
            await ctx.send("You already own this item.", ephemeral=True)
        elif item == 2 and int(answer.get("rod")) == 1:
            await ctx.send("You already own this item.", ephemeral=True)
        elif item == 3 and int(answer.get("tmcn")) == 1:
            await ctx.send("You already own this item.", ephemeral=True)
        else:
            # Set costs and Formatted Name Strings
            # If Lance
            if item == 1:
                purchase_grammar = "**Jousting Lance** for **3,000** Coins"
                itemcost = 3000
                item_id = "lance"
            # If Rod
            elif item == 2:
                purchase_grammar == "**Fishing Rod** for **5,000** Coins"
                itemcost = 5000
                item_id = "rod"
            # If Time Machine
            elif item == 3:
                purchase_grammar == "**Time Machine** for **10,000** Coins"
                itemcost = 10000
                item_id = "tmcn"
            balance = answer.get("amt")
            # Check to see if the user has enough
            if int(balance) < itemcost:
                await ctx.send("You do not have enough to purchase this item.", ephemeral=True)
            else:
                embed = interactions.Embed(
                    title=f"{purchase_grammar} Purchase Sucessful!",
                    description=f"You spent **{comma_seperate(itemcost)}** Coins\nYou have **{comma_seperate(int(balance)-itemcost)}** Coins left.",
                    color=embedcolor("#CBA6F7")
                )
                await ctx.send(embeds=[embed])
                newvalue = { "$set": { "amt": f"{int(balance)-itemcost}", f"{item_id}": "1" }}
                usercol.update_one(query, newvalue)


# Launch The Bot
print("Starting Bot....")
# Oooooh look ASCII Art
print("""   ___       _ ___       __    ___  ___  ___  ___ 
  / _ | ____(_) _ )___  / /_  / _ \\/ _ \\/ _ \\/ _ \\
 / __ |/ __/ / _  / _ \\/ __/  \\_, / // / // / // /
/_/ |_/_/ /_/____/\\___/\\__/  /___/\\___/\\___/\\___/ 
-------------------------------------------------------
https://arithefirst.com
""")
bot.start()