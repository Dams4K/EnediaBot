import time

from discord import *
from discord.abc import GuildChannel
from discord.ext import tasks

from data_class import MemberCounter
from utils.bot_embeds import DangerEmbed, InformativeEmbed, SucceedEmbed


class MemberCounterCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @tasks.loop(minutes=2, seconds=30)
    async def update_channels_task(self):
        await self.update_channels(self.bot.guilds)

    async def update_channels(self, guilds: list):
        for guild in guilds:
            member_counter = MemberCounter(guild)
            await member_counter.update_channels()

    @Cog.listener()
    async def on_member_join(self, member):
        await self.update_channels([member.guild])

    @Cog.listener()
    async def on_raw_member_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        await self.update_channels([guild])

    @Cog.listener()
    async def on_ready(self):
        await self.update_channels(self.bot.guilds)

    @Cog.listener()
    async def on_presence_update(self, before, after):
        guilds = after.mutual_guilds
        await self.update_channels(guilds)
    
    member_counter = SlashCommandGroup("member_counter", name_localizations={"fr": "compteur_membres"}, default_member_permissions=Permissions(administrator=True), guild_only=True)

    @member_counter.command(
        name="link",
        name_localizations={"fr": "lier"},
        description="Link a channel to the updater",
        description_localizations={"fr": "Lier un salon à l'outil de mise à jour"}
    )
    @option("channel", name_localizations={"fr": "salon"}, type=GuildChannel, channel_types=[ChannelType.voice, ChannelType.text])
    @option("name", name_localizations={"fr": "nom"}, type=str)
    async def member_counter_link(self, ctx, channel, name: str):
        ctx.member_counter.link_channel(channel, name)

        embed = SucceedEmbed(title="Salon relié")
        embed.description = f"Le salon {channel.mention} comptera les membres, son nom sera mis-à-jour dans les minutes qui suivent et devrait ressembler à ça:\n\n{ctx.member_counter.get_channel_name(channel.id)}"

        await ctx.respond(embed=embed)
    
    @member_counter.command(
        name="unlink",
        name_localizations={"fr": "délier"},
        description="Unlink a channel",
        description_localizations={"fr": "Délie un salon"}
    )
    @option("channel", name_localizations={"fr": "salon"}, type=GuildChannel, channel_types=[ChannelType.voice, ChannelType.text])
    async def member_counter_unlink(self, ctx, channel):
        ctx.member_counter.unlink_channel(channel)

        embed = DangerEmbed(title="Salon dissocié")
        embed.description = f"Le salon {channel.mention} ne comptera plus les membres"

        await ctx.respond(embed=embed)

    @member_counter.command(name="help", name_localizations={"fr": "aide"})
    async def member_counter_help(self, ctx):
        embed = InformativeEmbed(title="Formatage")
        description = """Liste des *placeholders* existants

`{member_count}` : total des membres
`{connected_members}` : membres connectés
`{offline_members}` : membres en hors ligne ⚫
`{online_members}` : membres en ligne 🟢
`{idle_members}` : membres inactifs 🟡
`{dnd_members}` : membres à ne pas déranger 🔴
`{streaming_members}` : membres en stream 🟣
`{bot_members}` : bots
"""
        embed.description = description
        embed.set_footer(text="Le nom d'un salon peut prendre quelques minutes à se mettre à jour")

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(MemberCounterCog(bot))