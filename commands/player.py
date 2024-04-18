import discord
from discord.ext import commands
from database import load_database, save_database
import glob
import pandas as pd

class PlayerCommands(commands.Cog):
        def __init__(self, bot):
                self.bot = bot

        @commands.has_role("pit bosses")
        @commands.command()
        async def init(self, ctx):
                database = load_database()

                for guild in self.bot.guilds:
                        for member in guild.members:
                                if str(member.id) not in database:
                                        database[str(member.id)] = {
                                                "discord_username": str(member.display_name),
                                                "player_id": "",
                                                "total_net": 0
                                        }

                save_database(database)
                await ctx.send("Database has been initiated.")


        @commands.command()
        async def id(self, ctx, player_id: str, member: discord.Member = None):
                database = load_database()

                # Determine the target member based on the command usage
                if member:
                        # Check if the user has the required role to change another user's ID
                        if any(role.name in ["pit bosses"] for role in ctx.author.roles):
                                target_member = member
                        else:
                                await ctx.send("You do not have permission to change another user's ID.")
                                return
                else:
                        target_member = ctx.author

                user_id = str(target_member.id)

                if user_id not in database:
                        database[user_id] = {
                                "discord_username": str(target_member.display_name),
                                "player_id": "",
                                "total_net": 0
                        }

                database[user_id]['player_id'] = player_id

                player_net = 0
                path = "ledgers/*.csv"
                for fname in glob.glob(path):
                        df = pd.read_csv(fname)
                        if player_id in df['player_id'].values:
                                grouped_df = df.groupby(['player_id'])['net'].sum().reset_index()
                                net_amount = grouped_df.loc[grouped_df['player_id'] == player_id, 'net']
                                if not net_amount.empty:
                                        player_net += net_amount.iloc[0] / 100
                database[user_id]['total_net'] = player_net
                save_database(database)
                await ctx.send(f'Player ID updated for {target_member.display_name}')

        @commands.command()
        async def bal(self, ctx, member: discord.Member = None):
                if member is None:
                        member = ctx.author

                database = load_database()
                member_data = database.get(str(member.id))

                if member_data and 'total_net' in member_data:
                        member_round = format(member_data['total_net'], '.2f')
                        await ctx.send(f"{member.display_name}'s balance: {member_round}")
                else:
                        await ctx.send(f"No balance information found for {member.display_name}.")


        @commands.has_any_role("pit bosses")
        @commands.command()
        async def setBal(self, ctx, member: discord.Member, amount: int):
                database = load_database()
                if str(member.id) not in database:
                        await ctx.send(f"{member.display_name} is not in the database.")
                        return
                database[str(member.id)]['total_net'] = amount
                save_database(database)
                await ctx.send(f"Updated {member.display_name}'s balance to {amount}.")

        @commands.has_any_role("pit bosses")
        @commands.command()
        async def addBal(self, ctx, member: discord.Member, amount: float):
                database = load_database()
                user_id = str(member.id)

                if user_id not in database:
                        await ctx.send(f"{member.display_name} is not in the database.")
                        return

                # Ensure total_net key exists, if not set it to 0
                current_balance = database[user_id].get('total_net', 0)
                database[user_id]['total_net'] = current_balance + amount
                save_database(database)
                await ctx.send(f"Added {amount} to {member.display_name}'s balance. New balance: {database[user_id]['total_net']}.")

        @commands.has_any_role("pit bosses")
        @commands.command()
        async def subBal(self, ctx, member: discord.Member, amount: float):
                database = load_database()
                user_id = str(member.id)

                if user_id not in database:
                        await ctx.send(f"{member.display_name} is not in the database.")
                        return

                # Ensure total_net key exists, if not set it to 0
                current_balance = database[user_id].get('total_net', 0)
                if current_balance < amount:
                        await ctx.send(f"Cannot subtract {amount} from {member.display_name}'s balance. Insufficient funds.")
                        return

                database[user_id]['total_net'] = current_balance - amount
                save_database(database)
                await ctx.send(f"Subtracted {amount} from {member.display_name}'s balance. New balance: {database[user_id]['total_net']}.")

async def setup(bot):
        await bot.add_cog(PlayerCommands(bot))
