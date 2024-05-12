import discord
from discord.ext import commands
from database import load_database, save_database
import glob
import pandas as pd
from datetime import timedelta
import re
import asyncio
import os

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


        @commands.command()
        async def selfmute(self, ctx, duration: str):
        # Regex to parse the duration input
                match = re.match(r"(\d+)([mhd])$", duration)
                if not match:
                        await ctx.send("Invalid duration format. Please use the format [number][m/h/d], e.g., 20m, 5h, or 1d.")
                        return

                amount, unit = match.groups()
                amount = int(amount)

                # Calculate mute duration
                if unit == 'm':
                        mute_duration = timedelta(minutes=amount)
                elif unit == 'h':
                        mute_duration = timedelta(hours=amount)
                elif unit == 'd':
                        mute_duration = timedelta(days=amount)

                # Get the Muted role from the server
                muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
                if muted_role is None:
                        await ctx.send("Muted role does not exist. Please create it and configure its permissions correctly.")
                        return

                # Assign the Muted role to the author
                await ctx.author.add_roles(muted_role)
                await ctx.send(f"You have been muted for {amount}{unit}.")

                # Schedule the removal of the Muted role after the mute duration
                await asyncio.sleep(mute_duration.total_seconds())
                await ctx.author.remove_roles(muted_role)
                await ctx.send(f"{ctx.author.display_name}, you have been unmuted.")



        @commands.has_role("pit bosses")
        @commands.command()
        async def reload(self, ctx):
                database = load_database()

                # Initialize a directory to read CSV files
                ledger_dir = "ledgers"
                os.makedirs(ledger_dir, exist_ok=True)

                # Process each ledger file
                for ledger_file in os.listdir(ledger_dir):
                        if ledger_file.endswith(".csv"):
                                # Construct the full path to the ledger file
                                file_path = os.path.join(ledger_dir, ledger_file)
                                # Read the CSV file into a DataFrame
                                df = pd.read_csv(file_path)
                                # Group by player_id and sum the net values
                                grouped_df = df.groupby("player_id")["net"].sum().reset_index()

                                # Update the database with the summed values
                                for index, row in grouped_df.iterrows():
                                        player_id = str(row["player_id"])
                                        net_gain = float(row["net"])
                                        if player_id in database:
                                                database[player_id]["total_net"] += net_gain

                save_database(database)
                # Notify the user
                await ctx.send("All balances have been reloaded based on the ledger files.")


async def setup(bot):
        await bot.add_cog(PlayerCommands(bot))
