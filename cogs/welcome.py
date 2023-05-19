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

    welcome = SlashCommandGroup("welcome", name_localizations={"fr": "bienvenue"}, default_member_permissions=Permissions(administrator=True), guild_only=True)
    w_set = welcome.create_subgroup("set", name_localizations={"fr": "définir"})
    image = welcome.create_subgroup("image", name_localizations={"fr": "image"})

    @welcome.command(
        name="enable",
        name_localizations={"fr": "activer"},
        description="Enable the automatic welcome message",
        description_localizations={"fr": "Activer le message de bienvenue automatique"}
    )
    async def enable_welcome(self, ctx):
        ctx.welcome_config.enable()

        embed = SucceedEmbed(title="Activé", description="Les messages de bienvenue sont activés")
        await ctx.respond(embed=embed)

    @welcome.command(
        name="disable",
        name_localizations={"fr": "désactiver"},
        description="Disable the automatic welcome message",
        description_localizations={"fr": "Désactive le message de bienvenue automatique"}
    )
    async def disable_welcome(self, ctx):
        ctx.welcome_config.disable()

        embed = DangerEmbed(title="Désactivé", description="Les messages de bienvenue sont désactivés")
        await ctx.respond(embed=embed)

    @welcome.command(
        name="show",
        name_localizations={"fr": "afficher"},
        description="Show what the welcome message looks like",
        description_localizations={"fr": "Montre à quoi ressemble le message de bienvenue"}
    )
    async def welcome_show(self, ctx):
        await ctx.defer(ephemeral=True)

        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)
        else:
            await ctx.respond(ctx.welcome_config.get_message(ctx.author))

    @w_set.command(
        name="channel",
        name_localizations={"fr": "salon"},
        description="Channel where the welcome message will be sent",
        description_localizations={"fr": "Salon où le message de bienvenue sera envoyé"}
    )
    @option("channel", name_localizations={"fr": "salon"}, type=GuildChannel, channel_types=[ChannelType.text])
    async def set_channel(self, ctx, channel: TextChannel):
        ctx.welcome_config.set_channel(channel)

        title = "Salon redéfini"
        description = f"Les messages de bienvenue seront désormais envoyés dans le salon {channel.mention}"
        embed = WelcomePositiveEmbed(ctx.welcome_config, title=title, description=description)
        await ctx.respond(embed=embed)
    
    @w_set.command(
        name="message",
        name_localizations={"fr": "message"},
        description="Message sent when someone join the server",
        description_localizations={"fr": "Message envoyé lorsque quelqu'un rejoint le serveur"}
    )
    @option("message", name_localizations={"fr": "message"}, type=str, max_length=1024, required=False)
    async def set_message(self, ctx, message: str):
        ctx.welcome_config.set_message(message)

        title = "Message de bienvenue redéfini"
        description = f"Le message de bienvenue a été changé, fait {self.welcome_show.mention} pour voir le résultat"
        embed = WelcomePositiveEmbed(ctx.welcome_config, title=title, description=description)
        await ctx.respond(embed=embed)

    @image.command(
        name="font_size",
        name_localizations={"fr": "taille_de_police"},
        description="Change the font size of the text on the image",
        description_localizations={"fr": "Change la taille de la police du texte sur l'image"}
    )
    @option("size", name_localizations={"fr": "taille"}, type=int)
    async def image_font_size(self, ctx, size: int):
        await ctx.defer()

        ctx.welcome_config.set_font_size(size)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)
    
    @image.command(
        name="avatar_size",
        name_localizations={"fr": "taille_avatar"},
        description="Change the avatar size on the image",
        description_localizations={"fr": "Change la taille de l'avatar sur l'image"}
    )
    @option("size", name_localizations={"fr": "taille"}, type=int)
    async def image_avatar_size(self, ctx, size: int):
        await ctx.defer()

        ctx.welcome_config.set_avatar_size(size)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)
    
    @image.command(
        name="avatar_pos",
        name_localizations={"fr": "position_avatar"},
        description="Change the position of the avatar on the image",
        description_localizations={"fr": "Change la position de l'avatar sur l'image"}
    )
    @option("x", type=int)
    @option("y", type=int)
    async def image_avatar_pos(self, ctx, x: int, y: int):
        await ctx.defer()

        ctx.welcome_config.set_avatar_pos(x, y)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)

    @image.command(
        name="text",
        name_localizations={"fr": "texte"},
        description="Change the text of the image",
        description_localizations={"fr": "Change le texte de l'image"}
    )
    @option("text", name_localizations={"fr": "texte"}, type=str, max_length=1024)
    async def image_text(self, ctx, text: str):
        await ctx.defer()

        ctx.welcome_config.set_image_text(text)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)

    @image.command(
        name="text_pos",
        name_localizations={"fr": "position_texte"},
        description="Change the position of the text of the image",
        description_localizations={"fr": "Change la position de du texte de l'image"}
    )
    @option("x", type=int)
    @option("y", type=int)
    async def image_text_pos(self, ctx, x: int, y: int):
        await ctx.defer()

        ctx.welcome_config.set_image_text_pos(x, y)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            await ctx.respond(ctx.welcome_config.get_message(ctx.author), file=file)

    @image.command(
        name="import",
        name_localizations={"fr": "importer"},
        description="Import a background image that will be used by the bot",
        description_localizations={"fr": "Importe une image de fond qui sera utilisée par le robot"}
    )
    @option("image", type=Attachment, required=True)
    async def image_import(self, ctx, image):
        await ctx.welcome_config.upload_background(image)
        if file := await self.get_welcome_file(ctx.author, ctx.welcome_config):
            embed = SucceedEmbed(title="Image importé avec succès", description="Résultat :")
            embed.set_image(url=f"attachment://{file.filename}")
            await ctx.respond(embed=embed, file=file)
        else:
            embed = DangerEmbed(title="Erreur", description="Un problème est survenu")
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(WelcomeCog(bot))