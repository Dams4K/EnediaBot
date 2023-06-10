import discord
from discord.enums import Status as DiscordStatus

from ddm import *
from utils.references import References


class ChannelFormatter(dict):
    def __missing__(self, key):
        return f"{key}"

class MemberCounter(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.channels = {}

        super().__init__(References.get_guild_folder(f"{self._guild.id}/member_counter.json"))
    
    @Saveable.update()
    def link_channel(self, channel: discord.abc.GuildChannel, name: str) -> None:
        """Add member counter channel

        Parameters
        ----------
            channel: discord.abc.GuildChannel
            name: str
        
        Returns
        -------
            None
        """
        self.channels[str(channel.id)] = name
    
    @Saveable.update()
    def unlink_channel(self, channel: discord.abc.GuildChannel) -> int:
        """Remove linked channel
        
        Parameters
        ----------
            channel: discord.abc.GuildChannel
        
        Returns
        -------
            int | None
        """
        channel_id = str(channel.id)
        if channel_id in self.channels:
            return self.channels.pop(channel_id)

    @Saveable.update()
    def unlink_channel_id(self, channel_id: int) -> int:
        """Remove linked channel by its id
        
        Parameters
        ----------
            channel_id: int
        
        Returns
        -------
            int | None
        """
        if channel_id in self.channels:
            return self.channels.pop(channel_id)

    async def fetch_channels(self) -> list:
        """Get the list of all linked channels

        Returns
        -------
            list[discord.abc.GuildChannel]
        """
        return [await self._guild.fetch_channel(int(channel_id)) for channel_id in self.channels]

    def get_channel_name(self, channel_id: int) -> str:
        """Get formatted name of the channel

        Parameters
        ----------
            channel_id: int
        
        Returns
        -------
            str | None
        """
        if channel_name := self.channels.get(str(channel_id)):
            member_count = self._guild.member_count
            connected_members = 0

            online_members = 0
            idle_members = 0
            dnd_members = 0
            streaming_members = 0
            bot_members = 0

            for member in self._guild.members:
                status = member.status
                if status != DiscordStatus.offline:
                    connected_members += 1
                
                if status == DiscordStatus.online:
                    online_members += 1
                elif status == DiscordStatus.idle:
                    idle_members += 1
                elif status == DiscordStatus.dnd:
                    dnd_members += 1
                elif status == DiscordStatus.streaming:
                    streaming_members += 1
                
                if member.bot:
                    bot_members += 1

            offline_members = self._guild.member_count - connected_members

            return channel_name.format(
                member_count=member_count,
                connected_members=connected_members,
                online_members=online_members,
                offline_members=offline_members,
                idle_members=idle_members,
                dnd_members=dnd_members,
                streaming_members=streaming_members,
                bot_members=bot_members
            )

    async def update_channels(self) -> None:
        """Update the name of all linked channels

        Returns
        -------
            None
        """
        for channel_id in self.channels.keys():
            await self.update_channel(channel_id)
        
    async def update_channel(self, channel_id: int) -> None:
        """Update the name of the channel

        Parameters
        ----------
            channel_id: int

        Returns
        -------
            None
        """
        try:
            channel = await self._guild.fetch_channel(channel_id)
        except discord.errors.NotFound:
            print("ERROR - Channel with id", channel_id, "not found")
            print("Channel with id", channel_id, "is automatically unlinked")
            self.unlink_channel_id(channel_id)
        else:
            if channel_name := self.get_channel_name(channel.id):
                if channel_name != channel.name:
                    await channel.edit(name=channel_name)