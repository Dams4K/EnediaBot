import discord
from bot import EnediaBot
from utils.references import References

intents = discord.Intents.all()

bot = EnediaBot(intents=intents, debug_guilds=References.DEBUG_GUILDS)
bot.load_cogs(References.COGS_FOLDER)
bot.run(References.BOT_TOKEN)