# **Aribot 9000: By [arithefirst](https://arithefirst.com)**
Written in python using [interactions.py](https://github.com/interactions-py) for Discord API and [MongoDB](https://www.mongodb.com/) for storing data of the currency system<br>


## Current Commands

### /API
**Inputs:** User (Ping or Snowflake)<br>
**Description:** Uses the discord api to lookup data about specified user. This data includes the UID, Username, Avatar ID, Public Flags, Flags, Banner ID, Profile Accent Color, Global Name, Avatar Decoration Data, Banner Color, and Clan Data. 

### /Avatar
**Inputs:** User (Ping or Snowflake)<br>
**Description:** Returns a specified user's avatar.

### /Banner
**Inputs:** User (Ping or Snowflake)<br>
**Description:** Show's a specified user's banner. If the user does not have nitro, their banner's hex code and a color preview will be displayed

### /Cat
**Inputs:** N/A<br>
**Description:** Sends an image of a cat

### /Checkbal
**Inputs:** N/A<br>
**Description:** Sends you your current coin balance, gives you 100 coins if this is your first time using the command

### /Coinflip
**Inputs:**
    **Bet:** A bet on wether the coin will land on heads or tails<br>
    **Wager:** How much you want to wager on your bet<br>
**Description:** Flips a coin and optionally lets you wager on it's outcome

### /Ping
**Inputs:** N/A<br>
**Description:** Sends a "Pong!"

### /Identify
**Inputs:** N/A<br>
**Description:** Gives the user their UID and the server the command was run in's Guild ID

### /Info
**Inputs:** N/A<br>
**Description:** Gives basic info about the bot

### /Timezone
**Inputs:** Timezone in TZ format (optional) <br>
**Description:** Displays the 4 major US Timezones, and displays a timezone of a User's input if one is submitted