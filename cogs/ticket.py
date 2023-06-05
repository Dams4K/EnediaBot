from discord import *
from discord.abc import GuildChannel
from discord.ui import *

from data_class import TicketConfig
from utils.bot_embeds import DangerEmbed, InformativeEmbed, SucceedEmbed


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

        await interaction.response.send_message(ticket_config.get_message_response(channel), ephemeral=True)

class TicketCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    ticket = SlashCommandGroup("ticket", default_member_permissions=Permissions(administrator=True), guild_only=True)
    create_message = ticket.create_subgroup("create_message")

    category = ticket.create_subgroup("category")

    @Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CreateTicketView())
        self.bot.add_view(CloseTicketView())

    def get_creation_message(self, ticket_config):
        return InformativeEmbed(title=ticket_config.creation_message_title, description=ticket_config.creation_message_description)

    @create_message.command(name="send")
    @option("channel", type=TextChannel, required=False)
    async def create_message_send(self, ctx, channel):
        if channel == None:
            channel = ctx.channel

        await channel.send(embed=self.get_creation_message(ctx.ticket_config), view=CreateTicketView(ctx.ticket_config.message_button_label))
        await ctx.respond("Message envoyé", ephemeral=True)

    @create_message.command(name="view")
    async def create_message_view(self, ctx):
        await ctx.respond(embed=self.get_creation_message(ctx.ticket_config), view=CreateTicketView(ctx.ticket_config.message_button_label), ephemeral=True)

    @create_message.command(name="set")
    @option("title", type=str, max_length=128, default=None)
    @option("description", type=str, max_length=1024, default=None)
    async def cm_set_message(self, ctx, title: str = None, description: str = None) -> None:
        ctx.ticket_config.set_creation_message(title, description)

        embed = SucceedEmbed(title="Message de création de ticket")
        embed_description = ""
        if title:
            embed_description += "Titre modifié\n"
        if description:
            embed_description += "Descriptions modifié\n"
        
        if embed_description == "":
            embed_description = "Rien n'a été modifié"

        embed.description = embed_description

        await ctx.respond(embed=embed)
        await ctx.respond(embed=self.get_creation_message(ctx.ticket_config), ephemeral=True)

    @category.command(name="set")
    @option("category", type=GuildChannel, channel_types=[ChannelType.category])
    async def set_category(self, ctx, category):
        ctx.ticket_config.set_category(category)

        embed = SucceedEmbed(title="Catégorie redéfinie", description=f"Les salons seront créé dans la catégorie {category.mention}")
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(TicketCog(bot))