from .ledger import LedgerCommands
from .leaderboard import LeaderboardCommands
from .player import PlayerCommands

def setup(bot):
    bot.add_cog(LedgerCommands(bot))
    bot.add_cog(LeaderboardCommands(bot))
    bot.add_cog(PlayerCommands(bot))
