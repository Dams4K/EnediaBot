from discord.commands.context import ApplicationContext
from data_class import MemberCounterData

class BotApplicationContext(ApplicationContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.member_counter = None
        if self.guild is not None:
            self.member_counter = MemberCounterData(self.guild.id)