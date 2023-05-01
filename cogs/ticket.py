from discord import *
from discord.ui import *
from discord.abc import GuildChannel
from data_class import TicketConfig
from utils.bot_embeds import InformativeEmbed

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Close Ticket", custom_id="close-ticket", style=ButtonStyle.danger)
    async def close_ticket_callback(self, button, interaction):
        message = interaction.message
        if len(message.embeds) > 0:
            embed = message.embeds[0]
            text = embed.footer.text
            if text is not Embed.Empty and text.isnumeric():
                ticket_author_id = int(text)
                if interaction.user.id != ticket_author_id:
                    await interaction.response.send_message("Tu n'es pas l'auteur de ce ticket", ephemeral=True)
                    return
        
        channel = interaction.channel
        await channel.delete()

class CreateTicketView(View):
    def __init__(self, button_label=None):
        super().__init__(timeout=None)
        
        if button_label is not None:
            item = self.get_item("create-button")
            item.label = button_label

    @button(label="Create a Ticket", custom_id="create-button", style=ButtonStyle.primary)
    async def create_button_callback(self, button, interaction):
        ticket_config = TicketConfig(interaction.guild)
        channel = await ticket_config.create_ticket_channel(interaction.user)

        embed = InformativeEmbed(title="Ticket ouvert")
        embed.set_footer(text=str(interaction.user.id))

        await channel.send(f"{interaction.user.mention} voilà votre ticket", embed=embed, view=CloseTicketView())

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
        self.bot.add_view(CloseTicketView())

    @message.command(name="send")
    @option("channel", type=TextChannel, required=False)
    async def message_send(self, ctx, channel):
        if channel == None:
            channel = ctx.channel
        
        title = ctx.ticket_config.message_title
        description = ctx.ticket_config.message_description

        embed = Embed(title=title, description=description, colour=Colour.blurple())

        await channel.send(embed=embed, view=CreateTicketView(ctx.ticket_config.message_button_label))
        await ctx.respond("Message envoyé", ephemeral=True)

    @t_set.command(name="category")
    @option("category", type=GuildChannel, channel_types=[ChannelType.category])
    async def set_category(self, ctx, category):
        ctx.ticket_config.set_category(category)


def setup(bot):
    bot.add_cog(TicketCog(bot))