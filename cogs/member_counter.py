import time
from discord import *
from discord.abc import GuildChannel
from discord.ext import tasks
from data_class import MemberCounterData
from utils.bot_embeds import SucceedEmbed, DangerEmbed

class MemberCounterCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @tasks.loop(minutes=2, seconds=30)
    async def update_channels_task(self):
        await self.update_channels(self.bot.guilds)

    async def update_channels(self, guilds: list):
        for guild in guilds:
            member_counter = MemberCounterData(guild)
            await member_counter.update_channels()

    @Cog.listener()
    async def on_member_join(self, member):
        await self.update_channels([member.guild])

    @Cog.listener()
    async def on_raw_member_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        await self.update_channels([guild])

    @Cog.listener()
    async def on_ready(self):
        await self.update_channels(self.bot.guilds)

    @Cog.listener()
    async def on_presence_update(self, before, after):
        guilds = after.mutual_guilds
        await self.update_channels(guilds)
    
    member_counter = SlashCommandGroup("member_counter", default_member_permissions=Permissions(administrator=True), guild_only=True)

    @member_counter.command(name="link")
    @option("channel", type=GuildChannel, channel_types=[ChannelType.voice, ChannelType.text])
    @option("name", type=str)
    async def member_counter_link(self, ctx, channel, name: str):
        ctx.member_counter.add_channel(channel, name)

        embed = SucceedEmbed(title="Salon relié")
        embed.description = f"Le salon {channel.mention} comptera les membres, son nom sera mis-à-jour dans les minutes qui suivent et devrait ressembler à ça:\n\n{ctx.member_counter.get_channel_name(channel.id)}"

        await ctx.respond(embed=embed)
    
    @member_counter.command(name="unlink")
    @option("channel", type=GuildChannel, channel_types=[ChannelType.voice, ChannelType.text])
    async def member_counter_unlink(self, ctx, channel):
        ctx.member_counter.remove_channel(channel)

        embed = DangerEmbed(title="Salon dissocié")
        embed.description = f"Le salon {channel.mention} ne comptera plus les membres"

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(MemberCounterCog(bot))