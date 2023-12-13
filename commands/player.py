import discord
from discord.ext import commands
from database import load_database, save_database

class PlayerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("pit bosses")
    @commands.command()
    async def initialize(self, ctx):
        database = load_database()

        for guild in self.bot.guilds:
            for member in guild.members:
                if str(member.id) not in database:
                    database[str(member.id)] = {
                        "discord_username": str(member), 
                        "player_id": "", 
                        "total_net": 0
                    }

        save_database(database)
        await ctx.send("Database has been initiated.")

    @commands.command()
    async def id(self, ctx, player_id: str):
        database = load_database()

        if str(ctx.author.id) not in database:
            database[str(ctx.author.id)] = {
                "discord_username": str(ctx.author), 
                "player_id": "", 
                "total_net": 0
            }

        database[str(ctx.author.id)]['player_id'] = player_id
        save_database(database)
        await ctx.send(f'Player ID updated for {ctx.author.display_name}')

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        database = load_database()
        member_data = database.get(str(member.id))
        
        if member_data and 'total_net' in member_data:
            await ctx.send(f"{member.display_name}'s balance: {member_data['total_net']}")
        else:
            await ctx.send(f"No balance information found for {member.display_name}.")

async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))
