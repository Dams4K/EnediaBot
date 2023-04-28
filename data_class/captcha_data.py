import discord
from ddm import *
from utils.references import References

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

class CaptchaConfig(Saveable):
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