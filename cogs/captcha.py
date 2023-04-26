import io
import asyncio
from discord import *
from discord.abc import GuildChannel
from captcha.image import ImageCaptcha
from string import ascii_uppercase, digits
from random import choice
from data_class import CaptchaConfigData, MemberCaptcha

class CaptchaCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def generate_captcha_text(self, size: int = 5):
        chars = digits + ascii_uppercase

        return "".join([choice(chars) for _ in range(size)])

    def generate_captcha_image(self, text):
        image_captcha = ImageCaptcha(width = 300, height = 100)
        return image_captcha.generate_image(text)

    @Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        captcha_config = CaptchaConfigData(guild)

        if not captcha_config.enabled: # The captcha is disabled
            return

        channel = captcha_config.get_channel() or guild.system_channel
        if channel is None: # The channel doesn't exist
            return

        text = self.generate_captcha_text()
        img = self.generate_captcha_image(text)

        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)

            file = File(image_binary, filename="captcha.png")
            msg = await channel.send(captcha_config.message.format(member=member), file=file)

            member_captcha = MemberCaptcha()
            member_captcha.text = text
            member_captcha.message_id = msg.id

            captcha_config.add_member_captcha(member, member_captcha)

    @Cog.listener()
    async def on_message(self, message):
        captcha_config = CaptchaConfigData(message.guild)

        channel = message.channel
        captcha_channel = captcha_config.get_channel()

        if channel.id != captcha_channel.id:
            return
        
        author_captcha = captcha_config.get_member_captcha(message.author.id)
        if author_captcha is None: # Author has no captcha
            return

        if message.content == author_captcha.text:
            captcha_config.remove_member_captcha(message.author.id)

            reply_msg = await message.reply("Réponse correct !")
            captcha_msg = self.bot.get_message(author_captcha.message_id)

            await asyncio.sleep(2)

            await message.delete()
            await reply_msg.delete()
            if captcha_msg is not None:
                await captcha_msg.delete()


    captcha = SlashCommandGroup("captcha", default_member_permissions=Permissions(administrator=True), guild_only=True)
    c_set = captcha.create_subgroup("set")

    @captcha.command(name="enable")
    async def captcha_enable(self, ctx):
        ctx.captcha_config.enable()

    @captcha.command(name="disable")
    async def captcha_disable(self, ctx):
        ctx.captcha_config.disable()

    @c_set.command(name="channel")
    @option("channel", type=GuildChannel, channel_types=[ChannelType.text])
    async def set_channel(self, ctx, channel: TextChannel):
        ctx.captcha_config.set_channel(channel)


def setup(bot):
    bot.add_cog(CaptchaCog(bot))