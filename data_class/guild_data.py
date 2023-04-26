import discord
from discord.enums import Status as DiscordStatus
from ddm import *
from utils.references import References

class ChannelFormatter(dict):
    def __missing__(self, key):
        return f"{key}"

class MemberCounterData(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.channels = {}

        super().__init__(References.get_guild_folder(f"{self._guild.id}/member_counter.json"))
    
    @Saveable.update()
    def add_channel(self, channel, name):
        self.channels[str(channel.id)] = name
    
    @Saveable.update()
    def remove_channel(self, channel):
        channel_id = str(channel.id)
        if channel_id in self.channels:
            return self.channels.pop(channel_id)
    
    async def fetch_channels(self):
        return [await self._guild.fetch_channel(int(channel_id)) for channel_id in self.channels]

    async def update_channels(self):
        for channel_id in self.channels.keys():
            await self.update_channel(channel_id)
        
    async def update_channel(self, channel_id):
        channel_id = str(channel_id)
        channel_name = self.channels.get(channel_id, None)
        if channel_name is None:
            return

        channel = await self._guild.fetch_channel(int(channel_id))
        if channel is None:
            return


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

        formatted_name = channel_name.format(
            member_count=member_count,
            connected_members=connected_members,
            online_members=online_members,
            offline_members=offline_members,
            idle_members=idle_members,
            dnd_members=dnd_members,
            streaming_members=streaming_members,
            bot_members=bot_members
        )
        
        if formatted_name != channel.name:
            await channel.edit(name=formatted_name)

    
class TicketConfigData(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.message_title = "Créer un Ticket"
        self.message_description = "Créer un ticket pour pouvoir parler en privé avec le staff du serveur"
        self.message_button_label = "Créer un Ticket"
        self.message_response = "Ticket créé"

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

        channel = await self._guild.create_text_channel(channel_name, reason=reason, category=category, overwrites=overwrites)

        await channel.send(member.mention)

        return channel

    @Saveable.update()
    def set_message_title(self, value):
        self.message_title = value
    
    @Saveable.update()
    def set_message_description(self, value):
        self.message_description = value

    @Saveable.update()
    def set_message_button_label(self, value):
        self.message_button_label = value
    
    @Saveable.update()
    def set_category(self, category: discord.CategoryChannel):
        self.ticket_category_id = category.id

    async def fetch_category_channel(self):
        return await self._guild.fetch_channel(self.ticket_category_id)

class MemberCaptcha(Data):
    def __init__(self):
        self.text = None
        self.message_id = None
    
    async def fetch_message(self, channel) -> discord.TextChannel:
        """Get the captcha message sent by the bot

        Parameters
        ----------
            channel: discord.TextChannel

        Returns
        -------
            discord.TextChannel | None
        """
        return await channel.fetch_message(self.message_id)

class CaptchaConfigData(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.enabled = False
        
        self.size = 5
        self.message = "{member.mention} écrit le mot affiché sur l'image. Le mot est consitué de {size} caractères, toutes les lettres sont en majuscules"

        self.verified_role_id = None
        self.unverified_role_id = self._guild.default_role.id # @everyone
        self.channel_id = None

        self.member_captchas = {}
        self._member_captchas_type = MemberCaptcha()

        super().__init__(References.get_guild_folder(f"{self._guild.id}/captcha_config.json"))
    
    @Saveable.update()
    def enable(self) -> None:
        """Enable the captcha"""
        self.enabled = True
    @Saveable.update()
    def disable(self) -> None:
        """Disable the captcha"""
        self.enabled = False

    @Saveable.update()
    def set_size(self, size: int) -> None:
        """Set the size of the generated captcha text
        
        Parameters
        ----------
            size: int
        """
        self.size = size

    @Saveable.update()
    def set_message(self, message: str) -> None:
        """Set the message sent with the image
        
        Parameters
        ----------
            message: str
                max size: 2048
        """
        self.message = message[:2048]

    def get_message(self, **kwargs) -> str:
        """Get the message sent with the image with basic formatting (size, roles...)
        
        Returns
        -------
            str
        """
        return self.message.format(size=self.size, verified_role=self.get_verified_role(), unverified_role=self.get_unverified_role(), **kwargs)

    @Saveable.update()
    def set_unverified_role(self, role: discord.Role) -> None:
        """Set the unverified role
        
        Parameters
        ----------
            role: discord.Role
        """
        self.unverified_role_id = role.id
    
    def get_unverified_role(self) -> discord.Role:
        """Get the unverified role
        
        Returns
        -------
            discord.Role | None
        """
        return self._guild.get_role(self.unverified_role_id)

    @Saveable.update()
    def set_verified_role(self, role: discord.Role) -> None:
        """Set the verified role
        
        Parameters
        ----------
            role: discord.Role
        """
        self.verified_role_id = role.id
    
    def get_verified_role(self) -> discord.Role:
        """Get the verified role
        
        Returns
        -------
            discord.Role | None
        """
        return self._guild.get_role(self.verified_role_id)
    
    @Saveable.update()
    def set_channel(self, channel: discord.TextChannel) -> None:
        """Set the channel where the captcha message will be sent
        
        Parameters
        ----------
            channel: discord.TextChannel
        """
        self.channel_id = channel.id

    async def fetch_channel(self) -> discord.TextChannel:
        """Get the channel where the captcha message will be sent
        
        Returns
        -------
            discord.TextChannel | None
        """
        try:
            return await self._guild.fetch_channel(self.channel_id)
        except discord.NotFound:
            return self._guild.system_channel
    
    
    @Saveable.update()
    def add_member_captcha(self, member: discord.Member, member_captcha: MemberCaptcha) -> None:
        """Add a MemberCaptcha
        
        Parameters
        ----------
            member: discord.Member
                The member to whom the MemberCaptcha instance will be assigned
            member_captcha: MemberCaptcha
                The MemberCaptcha instance
        """
        self.member_captchas[str(member.id)] = member_captcha

    @Saveable.update()
    def remove_member_captcha(self, member_id: int) -> MemberCaptcha:
        """Remove a MemberCaptcha asigned to a member
        
        Parameters
        ----------
            member_id: int
                The identifier of the member
        
        Returns
        -------
            MemberCaptcha | None
        """
        if str(member_id) in self.member_captchas:
            return self.member_captchas.pop(str(member_id))

    def get_member_captcha(self, member_id: int) -> MemberCaptcha:
        """Get a MemberCaptcha asigned to a member
        
        Parameters
        ----------
            member_id: int
                The identifier of the member
        
        Returns
        -------
            MemberCaptcha | None
        """
        return self.member_captchas.get(str(member_id))