import discord
from bot import EnediaBot
from utils.references import References

intents = discord.Intents(
    guilds=True,
    members=True,
    presences=True,
    guild_messages=True,
    message_content=True
)

bot = EnediaBot(debug_guilds=References.DEBUG_GUILDS, intents=intents)
bot.load_cogs(References.COGS_FOLDER)
bot.run(References.BOT_TOKEN)