import aiohttp
from discord import *
from discord.enums import Status as DiscordStatus

from utils.bot_embeds import InformativeEmbed
from utils.references import References

class GlobalCog(Cog):
    STATUS_EMOJIS = {
        DiscordStatus.offline: "⚫",
        DiscordStatus.online: "🟢",
        DiscordStatus.idle: "🟡",
        DiscordStatus.dnd: "🔴",
        DiscordStatus.streaming: "🟣",
    }

    def __init__(self, bot):
        self.bot = bot

    @user_command(name="User info")
    async def user_userinfo(self, ctx, user: Member):
        await ctx.respond(embed=self.userinfo_embed(user))
    
    @slash_command(name="userinfo")
    @option("member", type=Member, required=False)
    async def slash_userinfo(self, ctx, member: Member = None):
        member = member or ctx.author

        await ctx.respond(embed=self.userinfo_embed(member))

    def userinfo_embed(self, member: Member) -> Embed:
        embed = InformativeEmbed(title=f"{member} - {GlobalCog.STATUS_EMOJIS.get(member.status, GlobalCog.STATUS_EMOJIS[DiscordStatus.online])}")

        created_at = round(member.created_at.timestamp())
        joined_at = round(member.joined_at.timestamp())
        embed.add_field(name="Dates", value=f"Création: <t:{created_at}:f>\nArrivé: <t:{joined_at}:f>", inline=False)
        embed.add_field(name="Rôles", value=" ".join([role.mention for role in member.roles if role != member.guild.default_role]), inline=False)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID : {member.id}")
    
        return embed


def setup(bot):
    bot.add_cog(GlobalCog(bot))