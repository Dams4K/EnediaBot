import io
import asyncio
from discord import *
from discord.abc import GuildChannel
from captcha.image import ImageCaptcha
from string import ascii_uppercase, digits
from random import choice
from data_class import CaptchaConfigData, MemberCaptcha
from utils.bot_embeds import *

class CaptchaCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def generate_captcha_text(self, size) -> str:
        """Generate a random sequence of `size` characters
        
        Parameters
        ----------
            size: int
                size of the character string
        
        Returns
        -------
            str
        """
        chars = digits + ascii_uppercase
        return "".join([choice(chars) for _ in range(size)])

    def generate_captcha_image(self, text: str):
        """Generate a captcha image
        
        Parameters
        ----------
            text: str
                text on the image
        
        Returns
        -------
            PIL.Image
        """
        image_captcha = ImageCaptcha(width = 300, height = 100)
        return image_captcha.generate_image(text)

    @Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        captcha_config = CaptchaConfigData(guild)

        if not captcha_config.enabled: # The captcha is disabled
            return

        channel = captcha_config.get_channel()
        if channel is None: # The channel doesn't exist
            return

        # Add the unverified role if it exists
        unverified_role = captcha_config.get_unverified_role()
        if not unverified_role in [None, guild.default_role]:
            await member.add_roles(unverified_role)

        # Send image
        text = self.generate_captcha_text(captcha_config.size)
        img = self.generate_captcha_image(text)
        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)

            file = File(image_binary, filename="captcha.png")
            embed = InformativeEmbed(title="Captcha", description=captcha_config.get_message(member=member))
            embed.set_image(url=f"attachment://{file.filename}")

            msg = await channel.send(embed=embed, file=file)

            # Add member in the members captcha data
            member_captcha = MemberCaptcha()
            member_captcha.text = text
            member_captcha.message_id = msg.id

            captcha_config.add_member_captcha(member, member_captcha)

    @Cog.listener()
    async def on_message(self, message):
        captcha_config = CaptchaConfigData(message.guild)

        channel = message.channel
        captcha_channel = captcha_config.get_channel()

        if channel.id != captcha_channel.id: # Message sent on another channel
            return
        
        author_captcha = captcha_config.get_member_captcha(message.author.id)
        if author_captcha is None: # Author has no captcha data
            return

        # Remove author's message
        await message.delete()

        if message.content == author_captcha.text: # Correct
            # Clear author captcha data
            captcha_config.remove_member_captcha(message.author.id)
            # Delete the captcha message if it exists
            if captcha_msg := self.bot.get_message(author_captcha.message_id):
                await captcha_msg.delete()
            
            # Add the verified role if it exists
            verified_role = captcha_config.get_verified_role()
            if not verified_role in [None, message.guild.default_role]: # Si le rôle existe et il n'est pas @everyone
                await message.author.add_roles(verified_role) 

            # Remove the unverified role if it exists
            unverified_role = captcha_config.get_unverified_role()
            if not unverified_role in [None, message.guild.default_role]: # Si le rôle existe et il n'est pas @everyone
                await message.author.remove_roles(unverified_role)


    captcha = SlashCommandGroup("captcha", default_member_permissions=Permissions(administrator=True), guild_only=True)
    c_set = captcha.create_subgroup("set")

    @captcha.command(name="enable")
    async def captcha_enable(self, ctx):
        ctx.captcha_config.enable()
        embed = SucceedEmbed(title="Captcha activé", description="Le captcha est désormais activé")
        await ctx.respond(embed=embed)

    @captcha.command(name="disable")
    async def captcha_disable(self, ctx):
        ctx.captcha_config.disable()
        embed = DangerEmbed(title="Captcha désactivé", description="Le captcha est désormais désactivé")
        await ctx.respond(embed=embed)

    @c_set.command(name="message")
    @option("message", type=str, max_length=2048)
    async def set_message(self, ctx, message: str):
        ctx.captcha_config.set_message(message)
        embed = SucceedEmbed()
        if not ctx.captcha_config.enabled:
            embed = WarningEmbed()
            embed.set_footer(text="Captcha désactivé")
        
        embed.title = "Changement effectué"
        embed.description = "Le message du captcha a été changé"

        await ctx.respond(embed=embed)

    @c_set.command(name="channel")
    @option("channel", type=GuildChannel, channel_types=[ChannelType.text])
    async def set_channel(self, ctx, channel: TextChannel):
        ctx.captcha_config.set_channel(channel)
        embed = SucceedEmbed()
        if not ctx.captcha_config.enabled:
            embed = WarningEmbed()
            embed.set_footer(text="Captcha désactivé")
        
        embed.title = "Changement effectué"
        embed.description = f"Le salon du où le captcha sera effectué est maintenant {channel.mention}"

        await ctx.respond(embed=embed)

    @c_set.command(name="size")
    @option("size", type=int)
    async def set_size(self, ctx, size: int):
        ctx.captcha_config.set_size(size)
        embed = SucceedEmbed()
        if not ctx.captcha_config.enabled:
            embed = WarningEmbed()
            embed.set_footer(text="Captcha désactivé")
        
        embed.title = "Changement effectué"
        embed.description = f"La taille du text du captcha est mainenant de {size} caractères"

        await ctx.respond(embed=embed)

    @c_set.command(name="unverified_role")
    @option("role", type=Role)
    async def set_unverified_role(self, ctx, role: Role):
        ctx.captcha_config.set_unverified_role(role)
        embed = SucceedEmbed()
        if not ctx.captcha_config.enabled:
            embed = WarningEmbed()
            embed.set_footer(text="Captcha désactivé")
        
        embed.title = "Changement effectué"
        embed.description = f"Le rôle pour les membres n'ayant pas passé le captcha est maintenant {role.mention}"

        await ctx.respond(embed=embed)
    
    @c_set.command(name="verified_role")
    @option("role", type=Role)
    async def set_verified_role(self, ctx, role: Role):
        ctx.captcha_config.set_verified_role(role)
        embed = SucceedEmbed()
        if not ctx.captcha_config.enabled:
            embed = WarningEmbed()
            embed.set_footer(text="Captcha désactivé")
        
        embed.title = "Changement effectué"
        embed.description = f"Le rôle pour les membres ayant passé le captcha est maintenant {role.mention}"

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(CaptchaCog(bot))