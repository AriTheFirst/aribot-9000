<p align="center"><img src=images/botpfp.png></p>
<h1 align="center"><b>🤖 Aribot 9000: By <a href="https://arithefirst.com">arithefirst</a> 🤖</b></h1>
<h4 align="center">Written in python using <a href="https://github.com/interactions-py">interactions.py</a> for The Discord API and <a href="https://www.mongodb.com/">MongoDB</a> for storing data of the currency system</h4>

<h2>💾 Commands 💾</h2>

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

### /Checkbalance
**Inputs:** User (Ping or Snowflake); Optional<br>
**Description:** Sends you your current coin balance, gives you 100 coins if this is your first time using the command

### /Coinflip
**Inputs:**<br>
╰──**Bet:** A bet on if the coin will land on heads or tails<br>
╰──**Wager:** How much you want to wager on your bet<br>
**Description:** Flips a coin and optionally lets you wager on it's outcome

### /Fish
**Inputs:** N/A<br>
**Description:** Lets you fish for things worth different amounts of coins

### /Ping
**Inputs:** N/A<br>
**Description:** Sends a "Pong!"

### /Identify
**Inputs:** N/A<br>
**Description:** Gives the user their UID and the server the command was run in's Guild ID

### /Info
**Inputs:** N/A<br>
**Description:** Gives basic info about the bot

### /Send
**Inputs:**<br>
╰──**Amt:** How much money to send<br>
╰──**User:** Who to send money to<br>
**Description:** Flips a coin and optionally lets you wager on it's outcome

### /Timezone
**Inputs:** Timezone in TZ format (optional) <br>
**Description:** Displays the 4 major US Timezones, and displays a timezone of a User's input if one is submitted

<h2>🕹️🚫 Gamebreakers 🚫🕹️</h2>
<details closed>
<summary>Simplicursed</summary>
⠀ <a href="https://discord.com/users/490112659711328257">Simplicursed</a> has been added as a gamebreaker for discovering that the /coinflip command could be exploited using negative numbers.
<img src=images/simplicursed.png>
</details>

<details closed>
<summary>Shegu</summary>
⠀ <a href="https://discord.com/users/373905037057064970">Shegu</a> has been added as a gamebreaker for discovering that the /API and /Banner commands would error out when used on most bots.
</details>