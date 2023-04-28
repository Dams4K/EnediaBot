import discord
import io
import math
from ddm import *
from utils.references import References
from PIL import Image, ImageDraw, ImageFilter, ImageFont

class WelcomeConfig(Saveable):
    def __init__(self, guild):
        self._guild = guild

        self.channel_id = self._guild.system_channel
        self.message = "Hey {member.mention}, Bienvenue sur **{guild.name}** !"
        
        self.image = None
        self.image_text = "{member} a rejoint le serveur"
        self.image_text_pos = (48+320+32, 48+320/2)
        self.font_size = 86

        self.avatar_pos = [48, 48]
        self.avatar_size = 320


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
    
    @Saveable.update()
    def set_message(self, message: str):
        self.message = message[:1024]
    
    def get_message(self, member: discord.Member) -> str:
        return self.message.format(member=member, guild=self._guild)
    
    @Saveable.update()
    def set_image_text(self, text: str) -> None:
        self.image_text = text
    
    def get_image_text(self, member: discord.Member) -> str:
        return self.image_text.format(member=member, guild=self._guild)

    @Saveable.update()
    def set_font_size(self, size: int) -> None:
        self.font_size = size
    
    @Saveable.update()
    def set_avatar_size(self, size: int) -> None:
        self.avatar_size = size

    @Saveable.update()
    def set_avatar_pos(self, pos: list) -> None:
        self.avatar_pos = pos

    def get_avatar_area(self):
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

    def get_text_dimensions(self, text_string, font):
        # from https://stackoverflow.com/a/46220683/9263761
        ascent, descent = font.getmetrics()

        text_width = font.getmask(text_string).getbbox()[2]
        text_height = font.getmask(text_string).getbbox()[3] + descent

        return (text_width, text_height)

    def fit_text_in(self, text, width, font) -> list:
        result = []

        remaining_text = ""
        tries = 0

        while not text == remaining_text == "":
            dimension = self.get_text_dimensions(text, font)

            if dimension[0] > width:
                splitted_text = text.split()
                
                if len(splitted_text) == 1:
                    remaining_text = text[-1] + remaining_text
                    text = text[:-1]
                else:
                    text = " ".join(splitted_text[:-1])
                    remaining_text = " " + splitted_text[-1] + remaining_text            
            else:
                result.append(text.lstrip())
                text = remaining_text.lstrip()
                remaining_text = ""

        return result

    async def get_image(self, member):
        background = Image.open("assets/images/cropped_background2.png")
        foreground = Image.new("RGB", background.size, color="#1f2025")

        mask = Image.new("L", background.size, 0)

        # Draw background gradient
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rectangle((0, 0, background.size[0], background.size[1]-background.size[1]/3), fill="white")
        mask = mask.filter(ImageFilter.GaussianBlur(128))

        # Draw avatar hole
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse(self.get_avatar_area(), fill="black")
        mask = mask.filter(ImageFilter.GaussianBlur(2))

        result = Image.composite(foreground, background, mask)

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
        result_draw.multiline_text(self.image_text_pos, "\n".join(text), font=font, fill=(255, 255, 255, 255), anchor="lm")

        return result