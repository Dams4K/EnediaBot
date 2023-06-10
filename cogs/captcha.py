import asyncio
import io

from discord import *
from discord.abc import GuildChannel

from data_class import CaptchaConfig, MemberCaptcha
from utils.bot_embeds import *


class CaptchaPositiveEmbed(Embed):
    def __init__(self, captcha_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if captcha_config.enabled:
            self.color = Colour.brand_green()
            self.set_footer(text="Captcha activé")
        else:
            self.color = Colour.gold()
            self.set_footer(text="Captcha désactivé")

class CaptchaCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        guild = member.guild
        captcha_config = CaptchaConfig(guild)

        if not captcha_config.enabled: # The captcha is disabled
            return

        # Add the unverified role if it exists
        unverified_role = captcha_config.get_unverified_role()
        if not unverified_role in [None, guild.default_role]:
            await member.add_roles(unverified_role)


        try:
            channel: TextChannel = await captcha_config.fetch_channel()
        except errors.NotFound:
            print(f"WARNING - {channel} do not exist")
        else:
            if not member in channel.members: # The member have no access to the channel
                print(f"WARNING - {member} has no access to the captcha channel, no captcha message will be sent")
                return

            # Send image
            text = captcha_config.generate_captcha_text()
            img = captcha_config.generate_captcha_image(text)
            with io.BytesIO() as image_binary:
                img.save(image_binary, "PNG")
                image_binary.seek(0)

                file = File(image_binary, filename="captcha.png")
                embed = InformativeEmbed(title="Captcha - Verification", description=captcha_config.get_message(member=member))
                embed.set_image(url=f"attachment://{file.filename}")

                msg = await channel.send(embed=embed, file=file)

                # Add member in the members captcha data
                member_captcha = MemberCaptcha()
                member_captcha.text = text
                member_captcha.message_id = msg.id

                captcha_config.add_member_captcha(member, member_captcha)

    @Cog.listener()
    async def on_raw_member_remove(self, payload):
        user = payload.user
        guild = self.bot.get_guild(payload.guild_id)
        captcha_config = CaptchaConfig(guild)

        if member_captcha := captcha_config.remove_member_captcha(user.id): # User wasn't verified
            if captcha_message := await member_captcha.fetch_message(await captcha_config.fetch_channel()):
                await captcha_message.delete()


    @Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        
        captcha_config = CaptchaConfig(message.guild)

        channel = message.channel
        captcha_channel = await captcha_config.fetch_channel()

        if captcha_channel is None or channel.id != captcha_channel.id: # Message sent on another channel
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
            if captcha_msg := await channel.fetch_message(author_captcha.message_id):
                await captcha_msg.delete()
            
            # Add the verified role if it exists
            verified_role = captcha_config.get_verified_role()
            if not verified_role in [None, message.guild.default_role]: # Si le rôle existe et il n'est pas @everyone
                await message.author.add_roles(verified_role) 

            # Remove the unverified role if it exists
            unverified_role = captcha_config.get_unverified_role()
            if not unverified_role in [None, message.guild.default_role]: # Si le rôle existe et il n'est pas @everyone
                await message.author.remove_roles(unverified_role)


    captcha = SlashCommandGroup("captcha", name_localizations={"fr": "captcha"}, default_member_permissions=Permissions(administrator=True), guild_only=True)
    c_set = captcha.create_subgroup("set", name_localizations={"fr": "définir"})

    @captcha.command(
        name="enable",
        name_localizations={"fr": "activer"},
        description="Activate captcha",
        description_localizations={"fr": "Active le captcha"}
    )
    async def captcha_enable(self, ctx):
        ctx.captcha_config.enable()
        embed = SucceedEmbed(title="Captcha activé", description="Le captcha est désormais activé")
        await ctx.respond(embed=embed)

    @captcha.command(
        name="disable",
        name_localizations={"fr": "désactiver"},
        description="Disable captcha",
        description_localizations={"fr": "Désactive le captcha"}
    )
    async def captcha_disable(self, ctx):
        ctx.captcha_config.disable()
        embed = DangerEmbed(title="Captcha désactivé", description="Le captcha est désormais désactivé")
        await ctx.respond(embed=embed)

    @c_set.command(
        name="message",
        name_localizations={"fr": "message"},
        description="Message to send",
        description_localizations={"fr": "Message à envoyer"}
    )
    @option("message", type=str, max_length=2048)
    async def set_message(self, ctx, message: str):
        ctx.captcha_config.set_message(message)
        embed = CaptchaPositiveEmbed(ctx.captcha_config)
        
        embed.title = "Changement effectué"
        embed.description = "Le message du captcha a été changé"

        await ctx.respond(embed=embed)

    @c_set.command(
        name="channel",
        name_localizations={"fr": "salon"},
        description="Channel where the captcha will be performed",
        description_localizations={"fr": "Salon où le captcha sera effectué"}
    )
    @option("channel", name_localizations={"fr": "salon"}, type=GuildChannel, channel_types=[ChannelType.text])
    async def set_channel(self, ctx, channel: TextChannel):
        ctx.captcha_config.set_channel(channel)
        embed = CaptchaPositiveEmbed(ctx.captcha_config)
        
        embed.title = "Changement effectué"
        embed.description = f"Le salon où le captcha sera effectué est maintenant {channel.mention}"

        await ctx.respond(embed=embed)

    @c_set.command(
        name="size",
        name_localizations={"fr": "taille"},
        description="Size of the distorded text generated",
        description_localizations={"fr": "Taille du texte distordu généré"}
    )
    @option("size", name_localizations={"fr": "taille"}, type=int)
    async def set_size(self, ctx, size: int):
        ctx.captcha_config.set_size(size)
        embed = CaptchaPositiveEmbed(ctx.captcha_config)
        
        embed.title = "Changement effectué"
        embed.description = f"La taille du text du captcha est mainenant de {size} caractères"

        await ctx.respond(embed=embed)

    @c_set.command(
        name="unverified_role",
        name_localizations={"fr": "rôle_non_vérifié"},
        description="Role given to the member who hasn't validate the captcha",
        description_localizations={"fr": "Rôle attribué au membre qui n'a pas validé le captcha"}
    )
    @option("role", name_localizations={"fr": "rôle"}, type=Role)
    async def set_unverified_role(self, ctx, role: Role):
        ctx.captcha_config.set_unverified_role(role)
        embed = CaptchaPositiveEmbed(ctx.captcha_config)

        embed.title = "Changement effectué"
        embed.description = f"Le rôle pour les membres n'ayant pas passé le captcha est maintenant {role.mention}"

        await ctx.respond(embed=embed)
    
    @c_set.command(
        name="verified_role",
        name_localizations={"fr": "rôle_vérifié"},
        description="Role given to the member who has validate the captcha",
        description_localizations={"fr": "Rôle attribué au membre qui a validé le captcha"}
    )
    @option("role", name_localizations={"fr": "rôle"}, type=Role)
    async def set_verified_role(self, ctx, role: Role):
        ctx.captcha_config.set_verified_role(role)
        embed = CaptchaPositiveEmbed(ctx.captcha_config)
        
        embed.title = "Changement effectué"
        embed.description = f"Le rôle pour les membres ayant passé le captcha est maintenant {role.mention}"

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(CaptchaCog(bot))