from ddm import *
from utils.references import References

class ChannelFormatter(dict):
    def __missing__(self, key):
        return f"{key}"

class MemberCounterData(Saveable):
    def __init__(self, guild_id):
        self._guild_id = guild_id

        self.channels = {}

        super().__init__(References.get_guild_folder(f"{self._guild_id}/member_counter.json"))
    
    @Saveable.update()
    def add_channel(self, channel, name):
        self.channels[str(channel.id)] = name
    
    @Saveable.update()
    def remove_channel(self, channel):
        channel_id = str(channel.id)
        if channel_id in self.channels:
            return self.channels.pop(channel_id)
        
    async def update_channels(self):
        for channel_id in self.channels.keys():
            await self.update_channel(channel_id)
        
    async def update_channel(self, channel_id):
        channel_id = str(channel_id)
        channel_name = self.channels.get(channel_id, None)
        if channel_name is None:
            return
        
        
    