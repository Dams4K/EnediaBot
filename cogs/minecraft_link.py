from discord import *
from data_class import MinecraftMemberData
from utils.bot_embeds import SucceedEmbed, DangerEmbed, InformativeEmbed

class MinecraftLinkCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    minecraft = SlashCommandGroup("minecraft")

    @minecraft.command(name="link")
    @option("username", type=str, max_length=16)
    async def minecraft_link(self, ctx, username):
        minecraft_member_data = MinecraftMemberData(ctx.author, ctx.guild)
        await minecraft_member_data.set_uuid_from_name(username)

        await ctx.respond(embed=SucceedEmbed(title="Compté lié", description=f"Ton compte discord a été lié au compte minecraft `{username}`, ton pseudo sera mis-à-jour dans quelques minutes"))

    @minecraft.command(name="unlink")
    async def minecraft_unlink(self, ctx):
        minecraft_member_data = MinecraftMemberData(ctx.author, ctx.guild)
        if minecraft_member_data.file_exist:
            minecraft_member_data.delete()
            await ctx.respond(embed=DangerEmbed(title="Compte délié", description="Ton compte discord n'est désormais plus lié"))
        else:
            await ctx.respond(embed=InformativeEmbed(title="Aucun lien existant", description="Ton compte discord n'est pas lié"))



def setup(bot):
    bot.add_cog(MinecraftLinkCog(bot))