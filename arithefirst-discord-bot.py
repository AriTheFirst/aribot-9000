#!/usr/bin/env python
import re
import requests
import interactions
import os
from dotenv import load_dotenv

# Grab bot token from enviroment
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = interactions.Client(token=TOKEN)

# API Request Command
@bot.command(
    name="api",
    description="Get data on a user from Discord's API",
    scope=1221655728029302865,
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
        print("Request successful!")
        answer = response.json()
        await ctx.send(f"Here was the discord api response to your user:\n```json\n{answer}```")
    else:
        await ctx.send("Discord API Request Failed.\nThere could be multiple reasons for this:\n- You pinged a role instead of a user\n- You didn't ping the user but typed their name instead\n- You typed nonsense into the input\n- The Discord API Could be down (unlikely)",ephemeral=True)

# Avatar Command
@bot.command(
    name="avatar",
    description="Grab a user's avatar",
    scope=1221655728029302865,
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
    scope=1221655728029302865,
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
        username = answer['username']
        banner_id = answer['banner']
        banner_hex = answer['banner_color']
        print(f"{banner_id}")
        if banner_id == None:
            print("User does not have Nitro, Grabbing Hex Code....")
            print(f"Hex Code {banner_hex} found")
            await ctx.send(f"{username}'s banner Hex is {banner_hex}")
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
    scope=1221655728029302865,
)
async def info(ctx: interactions.CommandContext):
    await ctx.send("**## [Aribot 9000](https://github.com/AriTheFirst/aribot-9000): By [arithefirst](https://arithefirst.com)**Written in python using interactions.py and a custom method for interfacing with the Discord API")
print("Starting Bot....")
bot.start()