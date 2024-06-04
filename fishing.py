#!/usr/bin/env python
from datetime import datetime
import time
import random
import pymongo
import math
import interactions

def comma_seperate(number_str):
    return "{:,}".format(int(number_str))

def vowel_check(item):
    delist = ' '.join(item)
    item_lower = delist.lower()
    if item_lower[0] in 'aeiou':
        return "an " + f"**{delist}**"
    else:
        return "a " + f"**{delist}**"    

# Function for setting embed colors
def embedcolor(hex_code):
    return int(hex_code.lstrip('#'), 16)

# MongoDB URLs and DB
dbclient = pymongo.MongoClient("mongodb://10.0.0.21:27017")
database = dbclient["aribot-currency"]

def load_fishing(user_id, guild_id):
    items = ['Old Boot', 'Rock', 'Wallet', 'Oar Fish', 'Funny Stupid Fish', 'Salmon', 'Sea Bunny', 'Wedding Ring', 'Mortimer: The Ancient Evil Goblin That Steals your Coins', 'Monkey']
    probabilities = [20, 20, 15, 15, 10, 10, 5, 2.5, 2.5, 0.1]
    total_percentage = sum(probabilities)
    normalized_probabilities = [p / total_percentage for p in probabilities]

    gobquery = {"name_nonuser": "mortimer"}
    query = {"name": str(user_id)}
    usercol = database[f"server-{guild_id}"]
    answer = usercol.find_one(query)
    if answer == None:
        embed = interactions.Embed(
            title="You don't have an account!",
            color=embedcolor("#cba6f7"),
            description=f"Run `/checkbalance` to create an account.",
        )
        return [embed]
    else:
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
            embed = interactions.Embed(
                title="You're on Cooldown!",
                color=embedcolor("#cba6f7"),
                description=f"You have **{convert_ms(150-(math.floor(time.time())-int(lastfished)))}** until you can fish again.",
            )
            return [embed]        
        elif roundtime - int(lastfished) > 150:
            fished_fish = random.SystemRandom().choices(items, weights=normalized_probabilities, k=1)
            # Setup Fishing Logic
            def fishingrandomizer(minval: int, maxval: int):
                value = random.SystemRandom().randint(minval, maxval)
                balance = answer.get("amt")
                newbalance = int(balance) + value
                print(f"Current balance for {user_id} is {balance}, fished {int(newbalance)-int(balance)}, new balance is {newbalance}")
                newvalues = { "$set": { "amt": f"{newbalance}", "lastfished": f"{math.floor(time.time())}" }}
                usercol.update_one(query, newvalues)
                embed = interactions.Embed(
                    title="You Caught Something!",
                    color=embedcolor("#cba6f7"),
                    description=f"You caught {vowel_check(fished_fish)} worth **{comma_seperate(int(newbalance)-int(balance))}** Coins! Your new balance is **{comma_seperate(newbalance)}**.",
                )
                return [embed]
            # Old Boot Code
            if ' '.join(fished_fish) == "Old Boot":
                return fishingrandomizer(1,10)
            # Rock Code
            elif ' '.join(fished_fish) == "Rock":
                return fishingrandomizer(1, 5)
            # Wallet Code
            elif ' '.join(fished_fish) == "Wallet":
                return fishingrandomizer(30, 65)
            # Oar Fish Code
            elif ' '.join(fished_fish) == "Oar Fish":
                return fishingrandomizer(45, 75)
            # Funny Stupid Fish Code
            elif ' '.join(fished_fish) == "Funny Stupid Fish":
                return fishingrandomizer(60, 85)
            # Salmon Code
            elif ' '.join(fished_fish) == "Salmon":
                return fishingrandomizer(55, 65)
            # Sea Bunny Code       
            elif ' '.join(fished_fish) == "Sea Bunny":
                return fishingrandomizer(100, 200)
            # Wedding Ring Code
            elif ' '.join(fished_fish) == "Wedding Ring":
                return fishingrandomizer(150, 350)
            # Monkey Code
            elif ' '.join(fished_fish) == "Monkey":
                return fishingrandomizer(1000, 2000)
            # Goblin Code
            elif ' '.join(fished_fish) == "Mortimer: The Ancient Evil Goblin That Steals your Coins":
                balance = answer.get("amt")
                if int(balance) <= 1:
                    return(f"You caught the {' '.join(fished_fish)}!\nHe tried to take half your coins, but you were too poor!")
                else: 
                    gobanswer = usercol.find_one(gobquery)
                    return(f'You caught **Mortimer, The Ancient Evil Goblin That Steals Your Coins**!\nHe took half your coins and now you have **{math.floor(int(balance)/2)}**')
                    if gobanswer == None:
                        inst = usercol.insert_one({ "name_nonuser": "mortimer", "amt": f"{math.floor(int(balance)/2)}",})
                        newvalues = { "$set": { "amt": f"{math.floor(int(balance)/2)}", "lastfished": f"{math.floor(time.time())}" }}
                        usercol.update_one(query, newvalues)
                    else:
                        gob_balance = gobanswer.get("amt")
                        goblin_new_values = { "$set": {"amt": f"{int(gob_balance)+(math.floor(int(balance)/2))}",}}
                        newvalues = { "$set": { "amt": f"{math.floor(int(balance)/2)}", "lastfished": f"{math.floor(time.time())}" }}
                        usercol.update_one(query, newvalues)
                        usercol.update_one(gobquery, goblin_new_values)
