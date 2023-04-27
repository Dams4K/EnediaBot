import io
import math
from discord import *
from PIL import Image, ImageDraw, ImageFilter

class WelcomeCog(Cog):
    AVATAR_SIZE = 384

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

    def __init__(self, bot):
        self.bot = bot

    def get_area(self, position: list, size: list):
        return (position[0], position[1], position[0]+size[0], position[1]+size[1])

    async def get_welcome_image(self, member: Member):
        template = Image.open("images/welcome_template.png")

        # Get member's avatar
        member_avatar = member.display_avatar.with_size(self.get_ceil_power2_size(WelcomeCog.AVATAR_SIZE))
        avatar_bytes = await member_avatar.read()
        avatar_image = Image.open(io.BytesIO(avatar_bytes))
        if avatar_image.size[0] != WelcomeCog.AVATAR_SIZE:
            avatar_image = avatar_image.resize([WelcomeCog.AVATAR_SIZE]*2)

        avatar_mask = Image.new("L", avatar_image.size, 0)
        draw = ImageDraw.Draw(avatar_mask)
        draw.ellipse((0, 0, WelcomeCog.AVATAR_SIZE, WelcomeCog.AVATAR_SIZE), fill=255)
        avatar_mask = avatar_mask.filter(ImageFilter.GaussianBlur(1))
        
        avatar_area = self.get_area([48]*2, [WelcomeCog.AVATAR_SIZE]*2)
        
        template.paste(avatar_image, avatar_area, avatar_mask)

        with io.BytesIO() as image_binary:
            template.save(image_binary, "PNG")
            image_binary.seek(0)
            
            file = File(image_binary, filename="welcome.png")
            return file
            
    @Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if channel := await guild.fetch_channel(1101184040373076069):
                await channel.send(file=await self.get_welcome_image(member))
        

    @Cog.listener() # TODO: REMOVE THIS
    async def on_message(self, message):
        if not message.author.bot:
            await self.on_member_join(message.author)


def setup(bot):
    bot.add_cog(WelcomeCog(bot))