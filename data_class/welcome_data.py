import io
import math

import discord
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ddm import *
from utils.references import References


class WelcomeConfig(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.enabled = False

        self.channel_id = self._guild.system_channel
        self.message = "Hey {member.mention}, Bienvenue sur **{guild.name}** !"
        
        self.image = None
        self.image_text = "{member} a rejoint le serveur"
        self.image_text_pos = [48+320+32, 48+320/2]
        self.font_size = 86

        self.avatar_pos = [48, 48]
        self.avatar_size = 320


        super().__init__(References.get_guild_folder(f"{self._guild.id}/welcome_config.json"))
    
    @Saveable.update()
    def enable(self) -> None:
        """Enable welcome message
        Returns
        -------
            None
        """
        self.enabled = True

    @Saveable.update()
    def disable(self) -> None:
        """Disable welcome message
        Returns
        -------
            None
        """
        self.enabled = False

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
    
    @Saveable.update()
    def set_message(self, message: str) -> None:
        """Set guild's welcome message

        Parameters
        ----------
            message: str

        Returns
        -------
            None
        """
        self.message = message
    
    def get_message(self, member: discord.Member) -> str:
        """Get guild's welcome message

        Returns
        -------
            str
        """
        if isinstance(self.message, str):
            return self.message.format(member=member, guild=self._guild)
        else:
            return None

    @Saveable.update()
    def set_image_text(self, text: str) -> None:
        """Set text for the guild's image

        Parameters
        ----------
            text: str
        
        Returns
        -------
            None
        """
        self.image_text = text
    
    def get_image_text(self, member: discord.Member) -> str:
        """Get guild's image text for a member

        Parameters
        ----------
            member: discord.Member
        
        Returns
        -------
            str
        """
        return self.image_text.format(member=member, guild=self._guild)
    
    def set_image_text_pos(self, x: int, y: int) -> None:
        """Set text position for the guild's image

        Parameters
        ----------
            x: int
            y: int
        
        Returns
        -------
            None
        """
        self.image_text_pos = [x, y]

    @Saveable.update()
    def set_font_size(self, size: int) -> None:
        """Set text size for guild's image

        Parameters
        ----------
            size: int

        Returns
        -------
            None
        """
        self.font_size = size
    
    @Saveable.update()
    def set_avatar_size(self, size: int) -> None:
        """Set avatar size for the guild's image

        Parameters
        ----------
            size: int
        
        Returns
        -------
            None
        """
        self.avatar_size = size

    @Saveable.update()
    def set_avatar_pos(self, x: int, y: int) -> None:
        """Set avatar position for the guild's image

        Parameters
        ----------
            x: int
            y: int
        
        Returns
        -------
            None
        """
        self.avatar_pos = [x, y]


    async def upload_background(self, attachment: discord.Attachment):
        """Upload custom background

        Parameters
        ----------
            attachment: discord.Attachment
                background image
        """
        folder = References.get_guild_folder(str(self._guild.id))
        file_path = os.path.join(folder, f"background.png")
        with open(file_path, mode="wb") as f:
            await attachment.save(f)

    def get_background_path(self):
        """Get the guild's background path

        Returns
        -------
            str
        """
        folder = References.get_guild_folder(str(self._guild.id))
        file_path = os.path.join(folder, f"background.png")
        if not os.path.exists(file_path):
            # Default background image path
            file_path = "assets/images/default_background.png"
        return file_path


    def get_avatar_area(self):
        """Return the area of the avatar: (x, y, width, height)

        Returns
        -------
            tuple[int]
        """
        return self.avatar_pos + [self.avatar_pos[0] + self.avatar_size, self.avatar_pos[1] + self.avatar_size]

    def get_ceil_power2_size(self, size):
        """Returns the closer but higher power 2 number of the given size

        Parameters
        ----------
            size: int

        Returns
        -------
            int
        """
        return 2**math.ceil(math.log10(size)/math.log10(2))

    def get_text_width(self, text, font) -> int:
        """Return the width of a given text

        Parameters
        ----------
            text: str
            font: PIL.ImageFont
        
        Returns
        -------
            int

        From https://stackoverflow.com/a/46220683/9263761
        """
        ascent, descent = font.getmetrics()

        text_width = font.getmask(text).getbbox()[2]
        text_height = font.getmask(text).getbbox()[3] + descent

        return text_width

    def fit_text_in(self, text: str, width: int, font) -> list:
        """Return a new text adapted to the width

        Parameters
        ----------
            text: str
                text to be adapted to width
            width: int
                the width at which the text must fit
            font: PIL.ImageFont
                font used

        Returns
        -------
            str
        """
        result = []

        remaining_text = ""
        
        while not text == remaining_text == "":
            text_width = self.get_text_width(text, font)

            if text_width > width:
                # The text can't fit, we must split the text
                splitted_text = text.split(" ")
                
                if len(splitted_text) == 1:
                    # There is only one word, so we are forced to split the word
                    remaining_text = text[-1] + remaining_text
                    text = text[:-1]
                else:
                    # We remove the last word from text
                    text = " ".join(splitted_text[:-1])
                    # We add the last word to remaining_text
                    remaining_text = " " + splitted_text[-1] + remaining_text            
            else:
                # The text can fit
                result.append(text.lstrip()) # We remove the spacing at the beginning of the text because it is a new line -> limitation
                text = remaining_text.lstrip()
                remaining_text = ""

        return "\n".join(result)

    async def get_image(self, member: discord.Member) -> Image:
        """Get the welcome image for a member
        
        Parameters
        ----------
            member: discord.Member

        Returns
        -------
            PIL.Image
        """
        background = Image.open(self.get_background_path())
        foreground = Image.new("RGB", background.size, color="#1f2025")

        b_mask = Image.new("L", background.size, 0)

        # Draw background gradient
        b_mask_draw = ImageDraw.Draw(b_mask)
        b_mask_draw.rectangle((0, 0, background.size[0], background.size[1]-background.size[1]/3), fill="white")
        b_mask = b_mask.filter(ImageFilter.GaussianBlur(128))

        # Draw avatar hole
        b_mask_draw = ImageDraw.Draw(b_mask)
        b_mask_draw.ellipse(self.get_avatar_area(), fill="black")
        # b_mask = b_mask.filter(ImageFilter.GaussianBlur(2))

        result = Image.composite(foreground, background, b_mask)

        # Get member's avatar
        member_avatar = member.display_avatar.with_size(self.get_ceil_power2_size(self.avatar_size))
        avatar_bytes = await member_avatar.read()
        avatar_image = Image.open(io.BytesIO(avatar_bytes))
        if avatar_image.size[0] != self.avatar_size:
            avatar_image = avatar_image.resize([self.avatar_size]*2)

        # Create avatar mask
        avatar_mask = Image.new("L", avatar_image.size, 0)
        draw = ImageDraw.Draw(avatar_mask)
        draw.ellipse((0, 0, self.avatar_size, self.avatar_size), fill=255)
        avatar_mask = avatar_mask.filter(ImageFilter.GaussianBlur(1))

        # Add avatar image
        result.paste(avatar_image, self.get_avatar_area(), avatar_mask)
        
        # Add text
        font = ImageFont.truetype("assets/font/Roboto-Medium.ttf", self.font_size)
        text = self.fit_text_in(self.get_image_text(member), result.size[0] - self.avatar_size - 48 - 24, font)

        result_draw = ImageDraw.Draw(result)
        result_draw.multiline_text(self.image_text_pos, text, font=font, fill=(255, 255, 255, 255), anchor="lm")

        return result