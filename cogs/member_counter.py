from discord import *

class MemberCounterCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_ready(self):
        print(self.bot.guilds[0])
        print(self.bot.guilds[0].members)
    

def setup(bot):
    bot.add_cog(MemberCounterCog(bot))