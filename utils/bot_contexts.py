from discord.commands.context import ApplicationContext
from data_class import *

class BotApplicationContext(ApplicationContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.member_counter = None
        self.ticket_config = None
        if self.guild is not None:
            self.member_counter = MemberCounterData(self.guild)
            self.ticket_config = TicketConfigData(self.guild)