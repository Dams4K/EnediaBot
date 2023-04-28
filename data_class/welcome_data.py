import discord
from ddm import *
from utils.references import References

class WelcomeConfig(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.channel_id = self._guild.system_channel

        super().__init__(References.get_guild_folder(f"{self._guild.id}/welcome_config.json"))
    
    @Saveable.update()
    def set_channel(self, channel: discord.TextChannel) -> None:
        """Set the channel where the welcome message will be sent
        
        Parameters
        ----------
            channel: discord.TextChannel
        """
        self.channel_id = channel.id

    async def fetch_channel(self) -> discord.TextChannel:
        """Get the channel where the welcome message will be sent
        
        Returns
        -------
            discord.TextChannel | None
        """
        try:
            return await self._guild.fetch_channel(self.channel_id)
        except discord.NotFound:
            return self._guild.system_channel