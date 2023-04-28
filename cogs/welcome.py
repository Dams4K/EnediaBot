import io
import math
from discord import *
from discord.abc import GuildChannel
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from data_class import WelcomeConfig

class WelcomeCog(Cog):
    AVATAR_SIZE = 384
    FONT_SIZE = 86

    def __init__(self, bot):
        self.bot = bot

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

    def get_area(self, position: list, size: list):
        return (position[0], position[1], position[0]+size[0], position[1]+size[1])

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


    async def get_welcome_image(self, member: Member):
        template = Image.open("assets/images/welcome_template.png")

        # Get member's avatar
        member_avatar = member.display_avatar.with_size(self.get_ceil_power2_size(WelcomeCog.AVATAR_SIZE))
        avatar_bytes = await member_avatar.read()
        avatar_image = Image.open(io.BytesIO(avatar_bytes))
        if avatar_image.size[0] != WelcomeCog.AVATAR_SIZE:
            avatar_image = avatar_image.resize([WelcomeCog.AVATAR_SIZE]*2)

        # Create avatar mask
        avatar_mask = Image.new("L", avatar_image.size, 0)
        draw = ImageDraw.Draw(avatar_mask)
        draw.ellipse((0, 0, WelcomeCog.AVATAR_SIZE, WelcomeCog.AVATAR_SIZE), fill=255)
        avatar_mask = avatar_mask.filter(ImageFilter.GaussianBlur(1))
        
        # Add avatar image
        avatar_area = self.get_area([48]*2, [WelcomeCog.AVATAR_SIZE]*2)
        template.paste(avatar_image, avatar_area, avatar_mask)

        # Add text
        font = ImageFont.truetype("assets/font/Roboto-Medium.ttf", WelcomeCog.FONT_SIZE)

        text = f"{member} a rejoint le serveur"
        # print(self.get_text_dimensions(text, font))
        text = self.fit_text_in(text, template.size[0] - WelcomeCog.AVATAR_SIZE - 48 - 24, font)

        template_draw = ImageDraw.Draw(template)
        template_draw.multiline_text((avatar_area[2]+24, (avatar_area[1]+avatar_area[3])/2), "\n".join(text), font=font, fill=(255, 255, 255, 255), anchor="lm")

        with io.BytesIO() as image_binary:
            template.save(image_binary, "PNG")
            image_binary.seek(0)
            
            file = File(image_binary, filename="welcome.png")
            return file
            
    @Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        welcome_config = WelcomeConfig(guild)

        if channel := await welcome_config.fetch_channel():
            await channel.send(f"Hey {member.mention}, Bienvenue sur **Enedia** !", file=await self.get_welcome_image(member))
        
    welcome = SlashCommandGroup("welcome", default_member_permissions=Permissions(administrator=True), guild_only=True)
    w_set = welcome.create_subgroup("set")

    @w_set.command(name="channel")
    @option("channel", type=GuildChannel, channel_types=[ChannelType.text])
    async def set_channel(self, ctx, channel: TextChannel):
        ctx.welcome_config.set_channel(channel)
    
    @w_set.command(name="message")
    @option("message", type=str, max_length=1024)
    async def set_message(self, ctx, message: str):
        pass


def setup(bot):
    bot.add_cog(WelcomeCog(bot))