import requests
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

userchecked = "613358761901424652"

url = f"https://discord.com/api/v10/users/{userchecked}"
headers = {"Authorization": f"Bot {TOKEN}"}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("Request successful!")
    answer = response.json()
    avatar_id = answer['avatar']
    avatar_url = f"https://cdn.discordapp.com/avatars/{userchecked}/{avatar_id}.png?size=2048")
else:
    print(f"API Request Failed with code {response.status_code}")