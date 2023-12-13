import discord
from discord.ext import commands
import asyncio
import config

# Description and Intents
description = 'Discord Bot with Leaderboard Feature'
intents = discord.Intents.default()
intents.members = True  # Necessary for member-related information
intents.message_content = True  # Necessary for reading message content

bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

# Load Cogs/Extensions
async def load_extensions():
    cogs = ['commands.leaderboard', 'commands.ledger', 'commands.player']
    for cog in cogs:
        await bot.load_extension(cog)

# Main Function
async def main():
    # Load Cogs
    await load_extensions()

    # Start the Bot
    await bot.start(config.BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
