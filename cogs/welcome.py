import aiohttp
import io
import math
from discord import *
from discord.abc import GuildChannel
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from data_class import WelcomeConfig
from utils.bot_embeds import *

class WelcomePositiveEmbed(Embed):
    def __init__(self, welcome_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if welcome_config.enabled:
            self.color = Colour.brand_green()
            self.set_footer(text="Messages de bienvenue activé")
        else:
            self.color = Colour.gold()
            self.set_footer(text="Messages de bienvenue désactivé")

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

        if not welcome_config.enabled:
            return

        if channel := await welcome_config.fetch_channel():
            if file := await self.get_welcome_file(member, welcome_config):
                await channel.send(welcome_config.get_message(member), file=file)

    welcome = SlashCommandGroup("welcome", default_member_permissions=Permissions(administrator=True), guild_only=True)
    w_set = welcome.create_subgroup("set")
    image = welcome.create_subgroup("image")

    @welcome.command(name="enable")
    async def enable_welcome(self, ctx):
        ctx.welcome_config.enable()

        embed = SucceedEmbed(title="Activé", description="Les messages de bienvenue sont activés")
        await ctx.respond(embed=embed)

    @welcome.command(name="disable")
    async def disable_welcome(self, ctx):
        ctx.welcome_config.disable()

        embed = DangerEmbed(title="Désactivé", description="Les messages de bienvenue sont désactivés")
        await ctx.respond(embed=embed)

    @welcome.command(name="show")
    async def welcome_show(self, ctx):
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)
        else:
            await ctx.respond(ctx.welcome_config.get_message(ctx.author))

    @w_set.command(name="channel")
    @option("channel", type=GuildChannel, channel_types=[ChannelType.text])
    async def set_channel(self, ctx, channel: TextChannel):
        ctx.welcome_config.set_channel(channel)

        title = "Salon redéfini"
        description = f"Les messages de bienvenue seront désormais envoyés dans le salon {channel.mention}"
        embed = WelcomePositiveEmbed(ctx.welcome_config, title=title, description=description)
        await ctx.respond(embed=embed)
    
    @w_set.command(name="message")
    @option("message", type=str, max_length=1024, required=False)
    async def set_message(self, ctx, message: str):
        ctx.welcome_config.set_message(message)

        title = "Message de bienvenue redéfini"
        description = f"Le message de bienvenue a été changé, fait {self.welcome_show.mention} pour voir le résultat"
        embed = WelcomePositiveEmbed(ctx.welcome_config, title=title, description=description)
        await ctx.respond(embed=embed)

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

    @image.command(name="upload")
    async def image_upload(self, ctx):
        await ctx.respond("Envoi l'image que tu veux utiliser")

        def has_file(m: Message):
            return m.author == ctx.author and len(m.attachments) > 0

        try:
            image_message: Message = await self.bot.wait_for("message", check=has_file, timeout=30)
        except TimeoutError:
            return await ctx.respond("timeout")

        attachments = image_message.attachments
        if images := [attachment for attachment in attachments if "image" in attachment.content_type]:
            image = images[0]

            async with aiohttp.ClientSession() as session:
                async with session.get(image.url) as response:
                    if response.status != 200:
                        await image_message.reply(f"Un problème a eu lieu `Error {response.status}`")
                    ctx.welcome_config.upload_background(await response.read(), image.content_type.split("/")[1])


def setup(bot):
    bot.add_cog(WelcomeCog(bot))