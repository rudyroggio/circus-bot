import discord
from discord.ext import commands
import aiohttp
import pandas as pd
from database import load_database, save_database
import aiofiles
import os

class LedgerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_ids_file = 'processed_game_ids.txt'
        os.makedirs('data', exist_ok=True)
        self.game_ids_file_path = os.path.join('data', self.game_ids_file)

    @commands.has_any_role("pit bosses")
    @commands.command()
    async def ledger(self, ctx, url: str):
        try:
            game_id = self._extract_game_id(url)
            if self._is_duplicate_game_id(game_id):
                await ctx.send(f'Game ID {game_id} has already been processed.')
                return

            csv_file_path = await self._download_csv(game_id)
            if csv_file_path:
                self._process_and_update_ledger(csv_file_path, game_id)
                self._record_game_id(game_id)
                await ctx.send(f'Ledger processed and database updated for game ID: {game_id}')
                await ctx.send('The ledger has been officially closed. Thank you.')
            else:
                await ctx.send('Failed to download the ledger.')
        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')

    def _extract_game_id(self, url):
        return url.split('/')[-1]

    async def _download_csv(self, game_id):
        csv_url = f'https://www.pokernow.club/games/{game_id}/ledger_{game_id}.csv'
        ledger_dir = 'ledgers'
        os.makedirs(ledger_dir, exist_ok=True)
        file_path = os.path.join(ledger_dir, f'ledger_{game_id}.csv')

        async with aiohttp.ClientSession() as session:
            async with session.get(csv_url) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, 'wb') as file:
                        await file.write(await response.read())
                    return file_path

    def _process_and_update_ledger(self, file_path, game_id):
        df = pd.read_csv(file_path)
        grouped_df = self._group_ledger_data(df)
        database = load_database()
        self._update_database(database, grouped_df)
        save_database(database)

    def _is_duplicate_game_id(self, game_id):
        if os.path.exists(self.game_ids_file_path):
            with open(self.game_ids_file_path, 'r') as file:
                processed_ids = file.read().splitlines()
            return game_id in processed_ids
        return False

    def _record_game_id(self, game_id):
        with open(self.game_ids_file_path, 'a') as file:
            file.write(game_id + '\n')
            
    def _group_ledger_data(self, df):
        grouped_df = df.groupby(['player_nickname', 'player_id'])['net'].sum().reset_index()
        grouped_df['net'] = grouped_df['net'].astype(float) / 100
        return grouped_df

    def _update_database(self, database, grouped_df):
        for _, row in grouped_df.iterrows():
            player_id = str(row['player_id'])
            net_gain = float(row['net'])
            for key, value in database.items():
                if value.get('player_id') == player_id:
                    database[key]['total_net'] = float(database[key].get('total_net', 0.0)) + net_gain

async def setup(bot):
    await bot.add_cog(LedgerCommands(bot))
