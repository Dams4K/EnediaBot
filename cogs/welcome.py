import io
import math
from discord import *
from discord.abc import GuildChannel
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from data_class import WelcomeConfig

class WelcomeCog(Cog):
    AVATAR_SIZE = 320
    FONT_SIZE = 86

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        welcome_config = WelcomeConfig(guild)

        if channel := await welcome_config.fetch_channel():
            with io.BytesIO() as image_binary:
                img = await welcome_config.get_image(member)
                img.save(image_binary, "PNG")
                image_binary.seek(0)
                
                file = File(image_binary, filename="welcome.png")
                await channel.send(welcome_config.get_message(member), file=file)
        
    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        welcome_config = WelcomeConfig(message.guild)

        with io.BytesIO() as image_binary:
            img = await welcome_config.get_image(message.author)
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            
            file = File(image_binary, filename="welcome.png")
            await message.channel.send(file=file)


    welcome = SlashCommandGroup("welcome", default_member_permissions=Permissions(administrator=True), guild_only=True)
    w_set = welcome.create_subgroup("set")
    image = welcome.create_subgroup("image")

    @w_set.command(name="channel")
    @option("channel", type=GuildChannel, channel_types=[ChannelType.text])
    async def set_channel(self, ctx, channel: TextChannel):
        ctx.welcome_config.set_channel(channel)
    
    @w_set.command(name="message")
    @option("message", type=str, max_length=1024)
    async def set_message(self, ctx, message: str):
        ctx.welcome_config.set_channel(message)

    @image.command(name="font_size")
    @option("size", type=int)
    async def image_font_size(self, ctx, size: int):
        ctx.welcome_config.set_font_size(size)

def setup(bot):
    bot.add_cog(WelcomeCog(bot))