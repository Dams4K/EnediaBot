from discord import *
from data_class import MemberCounterData

class MemberCounterCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def update_channels(self, guilds: list):
        for guild in guilds:
            guild_id = guild.id
            member_counter = MemberCounterData(guild_id)
            
            for channel_id, channel_name in member_counter.channels.items():
                channel = guild.get_channel(int(channel_id))
                if channel is None:
                    continue


    @Cog.listener()
    async def on_ready(self):
        await self.update_channels(self.bot.guilds)

    @Cog.listener()
    async def on_presence_update(self, before, after):
        pass
    
    member_counter = SlashCommandGroup("member_counter", default_member_permissions=Permissions(administrator=True), guild_only=True)

    @member_counter.command(name="link")
    @option("channel", type=VoiceChannel)
    @option("name", type=str)
    async def member_counter_link(self, ctx, channel: channel, name: str):
        ctx.member_counter.add_channel(channel, name)

def setup(bot):
    bot.add_cog(MemberCounterCog(bot))