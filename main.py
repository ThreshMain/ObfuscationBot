import configparser
import os
import discord
import logging

from modules.anonymizer import Anonymizer, InitExchange
from modules.autopin import Autopin

VERSION = "DEV"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DiscordBot')

token: str = os.getenv("TOKEN")

bot = discord.Bot(owner_id=470490558713036801, intents=discord.Intents.all())
guild: discord.Guild
config = configparser.ConfigParser()
config.read("config.ini", "utf-8")


def create_welcome_embed() -> discord.Embed:
    """
    Creates embed used in welcome message
    :return: DiscordEmbed used in the message
    """
    welcome_embed: discord.Embed = discord.Embed(colour=discord.Color.green())
    welcome_embed.title = "Obfuscation bot"
    welcome_embed.description = "Ahoj, tenhle bot slouží k naplnění různorodých náročných požadavků Lomohova na " \
                                "kvalitu tohoto serveru." \
                                "\n\nAktivní moduly:"
    welcome_embed.set_footer(text=VERSION)
    if config.getboolean("Anonymizer", "enabled"):
        welcome_embed.add_field(
            name="Anonymizer",
            value="Přepošle zprávu plně anonymně. Mohou se přes to např. leakovat zadání. Což nepodporujeme. "
                  "Samozřejmě. Ta feature tu je jen tak. Výměnu zahájíte stisknutím tlačítka.",
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
async def on_ready() -> None:
    """
    Creates/updates welcome message. Deletes all channels in hiddencategory
    """
    logging.info("Joined as {0.name}".format(bot.user))
    global guild
    guild = await bot.fetch_guild(config.getint("Global", "GuildId"))
    channel: discord.TextChannel = \
        [channel for channel in await guild.fetch_channels() if
         channel.id == config.getint("Global", "welcomeChannelId")][0]
    buttons = discord.ui.View(timeout=None)
    if config.getboolean("Anonymizer", "enabled", fallback=False):
        buttons.add_item(InitExchange(config, bot))
    buttons.add_item(discord.ui.Button(label="Zdroják", url=config.get("Global", "sourcelink"), emoji="〽"))
    try:
        welcome_message: discord.Message = await channel.fetch_message(
            config.getint("Global", "welcomeMessageId", fallback=0))
        await welcome_message.edit(content="",
                                   embed=create_welcome_embed(),
                                   view=buttons)
    except discord.NotFound:
        welcome_message = await channel.send(embed=create_welcome_embed(),
                                             view=buttons)
        config["Global"]["welcomeMessageId"] = str(welcome_message.id)
        with open("config.ini", 'w', encoding='utf-8') as file:
            config.write(file)

    expired_channels = [channel for channel in await guild.fetch_channels()
                        if channel.category_id == config.getint("Anonymizer", "hiddenCategoryId")
                        and channel.type != discord.ChannelType.category]
    for channel in expired_channels:
        await channel.delete()


@bot.event
async def on_thread_join(thread: discord.Thread):
    if config.getboolean("Global", "autojointhreads") and bot.user not in thread.members:
        await thread.join()


if config.getboolean("Anonymizer", "enabled"):
    logger.info("Enabling Anonymizer module")
    bot.add_cog(Anonymizer(bot, logger, config))
if config.getboolean("Autopin", "enabled"):
    logger.info("Enabling Autopin module")
    bot.add_cog(Autopin(bot, logger, config))
bot.run(token)
