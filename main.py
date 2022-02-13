import configparser
import os
import discord
from discord.ext import commands
import logging

from modules.anonymizer import Anonymizer, InitExchange
from modules.autopin import Autopin

VERSION = "DEV"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DiscordBot')

token: str = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="!", owner_id=470490558713036801, intents=discord.Intents.all())
guild: discord.Guild
config = configparser.ConfigParser()
config.read("config.ini", "utf-8")


def create_welcome_embed() -> discord.Embed:
    welcome_embed: discord.Embed = discord.Embed(colour=discord.Color.orange())
    welcome_embed.title = "Obfuscation bot"
    welcome_embed.url = config.get("Global", "sourceLink")
    welcome_embed.description = "Ahoj, tenhle bot slouží k naplnění různorodých náročných požadavků Lomohova na " \
                                "kvalitu tohoto serveru." \
                                "\n\nAktivní moduly:"
    welcome_embed.set_footer(text=VERSION)
    if config.getboolean("Anonymizer", "enabled"):
        welcome_embed.add_field(
            name="Anonymizer",
            value="Přepošle anonymně zprávu. Mohou se přes to např. leakovat zadání. Což nepodporujeme. Samozřejmě. "
                  "Ta feature tu je jen tak.",
            inline=False)
    if config.getboolean("Autopin", "enabled"):
        welcome_embed.add_field(
            name="Autopin",
            value="Automaticky připne zprávu na které jsou více než " + config.get("Autopin", "threshold") + " "
                  + config.get("Autopin", "emoji") + " reakce.",
            inline=False
        )
    return welcome_embed


@bot.event
async def on_ready():
    logging.info("Joined as {0.name}".format(bot.user))
    global guild
    guild = await bot.fetch_guild(config.getint("Global", "GuildId"))
    channel: discord.TextChannel = \
        [channel for channel in await guild.fetch_channels() if
         channel.id == config.getint("Global", "welcomeChannelId")][0]
    try:
        welcome_message: discord.Message = await channel.fetch_message(
            config.getint("Global", "welcomeMessageId", fallback=0))
        await welcome_message.edit(content="",
                                   embed=create_welcome_embed(),
                                   view=InitExchange(config, bot)
                                   if config.getboolean("Anonymizer", "enabled") else None)
    except discord.NotFound:
        welcome_message = await channel.send(embed=create_welcome_embed(),
                                             view=InitExchange(config, bot)
                                             if config.getboolean("Anonymizer", "enabled") else None)
        config["Global"]["welcomeMessageId"] = str(welcome_message.id)
        with open("config.ini", 'w', encoding='utf-8') as file:
            config.write(file)

    expired_channels = [channel for channel in await guild.fetch_channels()
                        if channel.category_id == config.getint("Anonymizer", "hiddenCategoryId")
                        and channel.type != discord.ChannelType.category]
    for channel in expired_channels:
        await channel.delete()


if config.getboolean("Anonymizer", "enabled"):
    logger.info("Enabling Anonymizer module")
    bot.add_cog(Anonymizer(bot, logger, config))
if config.getboolean("Autopin", "enabled"):
    logger.info("Enabling Autopin module")
    bot.add_cog(Autopin(bot, logger, config))
bot.run(token)
