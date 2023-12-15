import discord
from discord.ext import commands
import asyncio
from database import load_database

class LeaderboardCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def lb(self, ctx):
		database = load_database()
		leaderboard = sorted(
			((user_id, user_data['total_net'], user_data.get('discord_username')) 
			 for user_id, user_data in database.items() if user_data.get('total_net')), 
			key=lambda x: x[1], reverse=True)

		ITEMS_PER_PAGE = 10
		total_pages = len(leaderboard) // ITEMS_PER_PAGE + (1 if len(leaderboard) % ITEMS_PER_PAGE else 0)

		def get_embed(page_number):
			start_index = page_number * ITEMS_PER_PAGE
			end_index = start_index + ITEMS_PER_PAGE
			embed = discord.Embed(title="Leaderboard")
			for rank, (user_id, total_net, discord_username) in enumerate(leaderboard[start_index:end_index], start=start_index+1):
				username_display = discord_username if discord_username else user_id
				total_net_rounded = format(total_net, '.2f')
				embed.add_field(name=f"{rank}. {username_display}", value=f"Net Winnings: {total_net_rounded}", inline=False)
			embed.set_footer(text=f"Page {page_number+1} of {total_pages}")
			return embed

		current_page = 0
		message = await ctx.send(embed=get_embed(current_page))

		await message.add_reaction('⬅️')
		await message.add_reaction('➡️')

		def check(reaction, user):
			return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

		while True:
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
				if str(reaction.emoji) == '➡️' and current_page < total_pages - 1:
					current_page += 1
				elif str(reaction.emoji) == '⬅️' and current_page > 0:
					current_page -= 1
				await message.edit(embed=get_embed(current_page))
				await message.remove_reaction(reaction, user)
			except asyncio.TimeoutError:
				break

async def setup(bot):
	await bot.add_cog(LeaderboardCommands(bot))
