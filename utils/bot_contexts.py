from discord.commands.context import ApplicationContext

from data_class import *


class BotApplicationContext(ApplicationContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.member_counter = None
        self.ticket_config = None
        self.captcha_config = None

        if self.guild is not None:
            self.member_counter = MemberCounter(self.guild)
            self.ticket_config = TicketConfig(self.guild)
            self.captcha_config = CaptchaConfig(self.guild)
            self.welcome_config = WelcomeConfig(self.guild)