import discord

from ddm import *
from utils.references import References


class TicketConfig(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.creation_message_title = "Créer un Ticket"
        self.creation_message_description = "Créer un ticket pour pouvoir parler en privé avec le staff du serveur"
        self.message_button_label = "Créer un Ticket"
        self.message_response = "Ticket créé: {channel.mention}"

        self.ticket_channel_name = "ticket-{username}"
        self.ticket_category_id = None

        super().__init__(References.get_guild_folder(f"{self._guild.id}/ticket_config.json"))
    
    async def create_ticket_channel(self, member: discord.Member) -> discord.TextChannel:
        category = await self.fetch_category_channel()

        channel_name = self.ticket_channel_name.format(username=member.name)
        reason = f"{member.name} has created a ticket"
        overwrites = {
            self._guild.default_role: discord.PermissionOverwrite(), #TODO: all False
            member: discord.PermissionOverwrite(read_message_history=True, attach_files=True, view_channel=True, send_messages=True, read_messages=True)
        }

        return await self._guild.create_text_channel(channel_name, reason=reason, category=category, overwrites=overwrites) 

    @Saveable.update()
    def set_creation_message(self, title: str = None, description: str = None) -> None:
        if title:
            self.creation_message_title = title
        if description:
            self.creation_message_description = description       

    @Saveable.update()
    def set_message_button_label(self, value) -> None:
        self.message_button_label = value
    
    @Saveable.update()
    def set_category(self, category: discord.CategoryChannel) -> None:
        self.ticket_category_id = category.id

    @Saveable.update()
    def set_message_response(self, value) -> None:
        self.message_response = value

    def get_message_response(self, channel) -> str:
        return self.message_response.format(channel=channel)

    async def fetch_category_channel(self) -> discord.abc.GuildChannel:
        return await self._guild.fetch_channel(self.ticket_category_id)