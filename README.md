# circus-bot

# Circus Casino Discord Bot

## Description
A bot designed for managing casino-style games and leaderboards within Discord. It provides functionalities like tracking player balances, updating leaderboards, and managing game-related data. 

## Features
- **Database Initialization**: Initialize a database with current members' information.
- **Leaderboard Management**: Display a leaderboard of users sorted by their net winnings.
- **Player Balance**: Check the balance of individual players.
- **Ledger Processing**: Download and process game ledgers to update player statistics.

## Installation

### Prerequisites
- Python 3.8 or newer
- discord.py library
- pandas library
- Other dependencies listed in `requirements.txt`

### Setup
1. **Clone the Repository**
   ```bash
   git clone https://github.com/rudyroggio/circus-bot.git
   cd circus-bot
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. Run `bot.py` -- make sure token field is set.

# TODO
- [x] if a new player joins, once they add their <id>, check all ledgers for past games and update db accordingly so that past info isn't lost
- add a feature to parse game files and calculate vpip etc
