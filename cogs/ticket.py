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

        await interaction.response.send_message(ticket_config.get_creation_response(channel), ephemeral=True)

class TicketCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    ticket = SlashCommandGroup("ticket",
        name_localizations={"fr": "ticket"},
        default_member_permissions=Permissions(administrator=True), guild_only=True)
    
    embed_creation = ticket.create_subgroup(
        "embed_creation",
        name_localizations={"fr": "embed_de_création"})

    category = ticket.create_subgroup("category")

    @Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CreateTicketView())
        self.bot.add_view(CloseTicketView())

    def get_embed_creation(self, ticket_config):
        return InformativeEmbed(title=ticket_config.embed_creation_title, description=ticket_config.embed_creation_description)

    @embed_creation.command(
        name="send",
        name_localizations={"fr": "envoyer"},
        description="Send ticket creation embed",
        description_localizations={"fr": "Envoyer l'embed de création de ticket"}
    )
    @option("channel", name_localizations={"fr": "salon"}, type=TextChannel, required=False)
    async def embed_creation_send(self, ctx, channel):
        if channel == None:
            channel = ctx.channel

        await channel.send(embed=self.get_embed_creation(ctx.ticket_config), view=CreateTicketView(ctx.ticket_config.create_button_label))
        await ctx.respond("Message envoyé", ephemeral=True)

    @embed_creation.command(
        name="see",
        name_localizations={"fr": "apercevoir"},
        description="See how the creation embed will looks like, without sending it",
        description_localizations={"fr": "Regarder à quoi ressemblera l'intégration de la création, sans l'envoyer"}
    )
    async def embed_creation_see(self, ctx):
        await ctx.respond(embed=self.get_embed_creation(ctx.ticket_config), view=CreateTicketView(ctx.ticket_config.create_button_label), ephemeral=True)

    @embed_creation.command(
        name="set",
        name_localizations={"fr": "définir"},
        description="Set ticket creation embed",
        description_localizations={"fr": "Défini l'embed de création de ticket"}
    )
    @option("title", name_localizations={"fr": "titre"}, type=str, max_length=128, default=None)
    @option("description", name_localizations={"fr": "description"}, type=str, max_length=1024, default=None)
    async def embed_creation_set(self, ctx, title: str = None, description: str = None) -> None:
        ctx.ticket_config.set_embed_creation(title, description)

        embed = SucceedEmbed(title="Message de création de ticket")
        embed_description = []
        if title:
            embed_description.append("Titre modifié")
        if description:
            embed_description.append("Descriptions modifié")
        
        embed.description = "\n".join(embed_description) or "Rien n'a été modifié"

        await ctx.respond(embed=embed)
        await ctx.respond(embed=self.get_embed_creation(ctx.ticket_config), ephemeral=True)

    @category.command(
        name="set",
        name_localizations={"fr": "définir"},
        description="Set category in which all ticket channels will be created",
        description_localizations={"fr": "Défini la catégorie dans laquelle tous les salons de tickets seront créés"}
    )
    @option("category", name_localizations={"fr": "catégorie"}, type=GuildChannel, channel_types=[ChannelType.category])
    async def set_category(self, ctx, category):
        ctx.ticket_config.set_category(category)

        embed = SucceedEmbed(title="Catégorie redéfinie", description=f"Les salons seront créé dans la catégorie {category.mention}")
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(TicketCog(bot))