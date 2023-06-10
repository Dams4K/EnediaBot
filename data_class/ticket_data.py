import discord

from ddm import *
from utils.references import References


class TicketConfig(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.creation_embed_title = "Créer un Ticket"
        self.creation_embed_description = "Créer un ticket pour pouvoir parler en privé avec le staff du serveur"
        self.create_button_label = "Créer un Ticket"
        self.creation_response = "Ticket créé: {channel.mention}"

        self.ticket_channel_name = "ticket-{username}"
        self.ticket_category_id = None

        super().__init__(References.get_guild_folder(f"{self._guild.id}/ticket_config.json"))
    
    async def create_ticket_channel(self, member: discord.Member) -> discord.TextChannel:
        """Create ticket channel for a member

        Parameters
        ----------
            member: discord.Member
        
        Returns
        -------
            discord.TextChannel
        """
        category = await self.fetch_category_channel()

        channel_name = self.ticket_channel_name.format(username=member.name)
        reason = f"{member.name} has created a ticket"
        overwrites = {
            self._guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_message_history=True, attach_files=True, view_channel=True, send_messages=True, read_messages=True)
        }

        return await self._guild.create_text_channel(channel_name, reason=reason, category=category, overwrites=overwrites) 

    @Saveable.update()
    def set_creation_embed(self, title: str = None, description: str = None) -> None:
        """Set title and description of the creation embed

        Parameters
        ----------
            title: str
            description: str
        
        Returns
        -------
            None
        """
        if title:
            self.creation_embed_title = title
        if description:
            self.creation_embed_description = description       

    @Saveable.update()
    def set_create_button_label(self, text: str) -> None:
        """Set create ticket button label

        Parameters
        ----------
            text: str

        Returns
        -------
            None
        """
        self.create_button_label = text
    
    @Saveable.update()
    def set_category(self, category: discord.CategoryChannel) -> None:
        """Set category in which all ticket channels will be created

        Parameters
        ----------
            category: discord.CategoryChannel
        
        Returns
        -------
            None
        """
        self.ticket_category_id = category.id

    @Saveable.update()
    def set_creation_response(self, text: str) -> None:
        """Set creation response message

        Parameters
        ----------
            text: str

        Returns
        -------
            None
        """
        self.creation_response = value

    def get_creation_response(self, channel: discord.TextChannel) -> str:
        """Get creation response message for a channel

        Parameters
        ----------
            channel: discord.TextChannel
        
        Returns
        -------
            None
        """
        return self.creation_response.format(channel=channel)

    async def fetch_category_channel(self) -> discord.CategoryChannel:
        """Get tickets category channel

        Returns
        -------
            discord.CategoryChannel
        """
        return await self._guild.fetch_channel(self.ticket_category_id)