from discord import *
from data_class import MinecraftMemberData

class MinecraftLinkCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    minecraft = SlashCommandGroup("minecraft")

    @minecraft.command(name="link")
    @option("username", type=str, max_length=16)
    async def minecraft_link(self, ctx, username):
        minecraft_member_data = MinecraftMemberData(ctx.author, ctx.guild)
        await minecraft_member_data.set_uuid_from_name(username)

    @minecraft.command(name="unlink")
    async def minecraft_unlink(self, ctx):
        minecraft_member_data = MinecraftMemberData(ctx.author, ctx.guild)
        minecraft_member_data.delete()


def setup(bot):
    bot.add_cog(MinecraftLinkCog(bot))