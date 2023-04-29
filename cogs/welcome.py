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

    async def get_welcome_file(self, member, welcome_config):
        with io.BytesIO() as image_binary:
            img = await welcome_config.get_image(member)
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            
            return File(image_binary, filename="welcome.png")

    @Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        welcome_config = WelcomeConfig(guild)

        if channel := await welcome_config.fetch_channel():
            if file := await self.get_welcome_file(member, welcome_config):
                await channel.send(welcome_config.get_message(member), file=file)

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
        await ctx.defer()

        ctx.welcome_config.set_font_size(size)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)
    
    @image.command(name="avatar_size")
    @option("size", type=int)
    async def image_avatar_size(self, ctx, size: int):
        await ctx.defer()

        ctx.welcome_config.set_avatar_size(size)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)
    
    @image.command(name="avatar_pos")
    @option("x", type=int)
    @option("y", type=int)
    async def image_avatar_pos(self, ctx, x: int, y: int):
        await ctx.defer()

        ctx.welcome_config.set_avatar_pos(x, y)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)

    @image.command(name="text")
    @option("text", type=str, max_length=1024)
    async def image_text(self, ctx, text: str):
        await ctx.defer()

        ctx.welcome_config.set_image_text(text)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)

    @image.command(name="text_pos")
    @option("x", type=int)
    @option("y", type=int)
    async def image_text_pos(self, ctx, x: int, y: int):
        await ctx.defer()

        ctx.welcome_config.set_image_text_pos(x, y)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)


def setup(bot):
    bot.add_cog(WelcomeCog(bot))