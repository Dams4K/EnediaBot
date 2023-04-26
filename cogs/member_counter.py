from discord import *
from discord.abc import GuildChannel
from data_class import MemberCounterData

class MemberCounterCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
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
    
    @member_counter.command(name="unlink")
    @option("channel", type=GuildChannel, channel_types=[ChannelType.voice, ChannelType.text])
    async def member_counter_unlink(self, ctx, channel):
        ctx.member_counter.remove_channel(channel)

def setup(bot):
    bot.add_cog(MemberCounterCog(bot))