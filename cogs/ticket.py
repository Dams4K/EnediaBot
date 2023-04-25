from discord import *
from discord.ui import *
from discord.abc import GuildChannel
from data_class import TicketConfigData

class CreateTicketView(View):
    def __init__(self, button_label=None):
        super().__init__(timeout=None)
        
        if button_label is not None:
            item = self.get_item("create-button")
            item.label = button_label

    @button(label="Create a Ticket", custom_id="create-button", style=ButtonStyle.primary)
    async def create_button_callback(self, button, interaction):
        ticket_config = TicketConfigData(interaction.guild)

        await ticket_config.create_ticket_channel(interaction.user)

        await interaction.response.send_message(ticket_config.message_response, ephemeral=True)

class TicketCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    ticket = SlashCommandGroup("ticket", default_member_permissions=Permissions(administrator=True), guild_only=True)
    message = ticket.create_subgroup("message")
    t_set = ticket.create_subgroup("set")

    @Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CreateTicketView())

    @message.command(name="send")
    @option("channel", type=TextChannel, required=False)
    async def message_send(self, ctx, channel):
        if channel == None:
            channel = ctx.channel
        
        title = ctx.ticket_config.message_title
        description = ctx.ticket_config.message_description

        embed = Embed(title=title, description=description, colour=Colour.blurple())

        await channel.send(embed=embed, view=CreateTicketView(ctx.ticket_config))
        await ctx.respond("Message envoyé", ephemeral=True)

    @t_set.command(name="category")
    @option("category", type=GuildChannel, channel_types=[ChannelType.category])
    async def set_category(self, ctx, category):
        ctx.ticket_config.set_category(category)


def setup(bot):
    bot.add_cog(TicketCog(bot))