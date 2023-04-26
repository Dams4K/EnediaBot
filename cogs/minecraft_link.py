from discord import *

class MinecraftLinkCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    

def setup(bot):
    bot.add_cog(MinecraftLinkCog(bot))