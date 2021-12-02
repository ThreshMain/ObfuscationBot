import os
from config import Config
import discord
from discord.ext import commands
import logging
import re

DEBUG = False
VERSION = "1.0-ALPHA-1"

if DEBUG:
    loggingLevel = logging.INFO
else:
    loggingLevel = logging.ERROR

logging.basicConfig(level=loggingLevel)
logger = logging.getLogger('DiscordBot')

config: Config = Config(logger)
token: str = os.getenv("TOKEN")
pattern = re.compile("^(.{3}):", re.IGNORECASE)

bot = commands.Bot(command_prefix="!", owner_id=470490558713036801, intents=discord.Intents.all())
guild: discord.Guild

welcome = "Ahoj, já jsem {0}, bot na anonymizaci zpráv.\n\
Napiš do tohoto kanálu jakoukoliv zprávu začínající prefixem obashující kód předmětu a já do něj odešlu danou zprávu.\n\
Zprávy mohou obsahovat obrázkové přílohy, soubory jako přílohy nebyly testovány.\n\
Momentálně podporuji:\n\
`dml:` pro #dml\n\
`la1:` pro #la1\n\
`pa1:` pro #pa1\n\
`uos:` pro #uos\n\
`tzp:` pro #tzp\n\
*Nezapomeň na dvoutečku*\n\n\
Bot je momentálně ve verzi {1}, pokud se chceš zapojit do vývoje nebo nahlásit chybu, můžeš tak udělat na {2}"

@bot.event
async def on_ready():
    logging.info("Joined as {0.name}".format(bot.user))
    global guild
    guild = await bot.fetch_guild(config.GuildId)


@bot.event
async def on_message(msg: discord.Message):
    if msg.author.id == bot.user.id:
        return
    if msg.channel.id != config.listeningChannel and msg.channel.type != discord.ChannelType.private:
        return

    if msg.content.startswith("updateWelcome") and await bot.is_owner(msg.author):
        await msg.channel.delete_messages(await msg.channel.history(limit=20).flatten())
        await updateWelcome(msg)
        return

    match: re.Match = re.match(pattern, msg.content)
    if match is None or config.channelMap.get(match.group(1)) is None:
        content = "Invalid taget channel, use prfixes like `dml:` or `uos:` to send message to corresponding channel"
        content += "\n" + msg.content
        for attachment in msg.attachments:
            content += "\n" + attachment.url
        await msg.author.send(content)
        await msg.delete()
        return

    if msg.mention_everyone:
        myMessage: discord.Message = await msg.reply("Just don't try that you slut")
        await msg.delete()
        await myMessage.delete(delay=30)
        return

    channels = await guild.fetch_channels()

    targetChannel: list[discord.TextChannel] = [channel for channel in channels if channel.id == config.channelMap.get(match.group(1))]

    webhook: list[discord.Webhook] = await targetChannel[0].webhooks()

    if len(webhook) == 0:
        name = "Hello there"
        webhook.append(await targetChannel[0].create_webhook(name=name))

    avatar = "https://cdn.discordapp.com/icons/914813122689241129/042d4c00a55cb2b2a8ef6d5db652b8df.png?size=96"
    content = msg.content[4:]
    for attachment in msg.attachments:
        content += "\n" + attachment.url
    await webhook[0].send(content, avatar_url=avatar)
    await msg.delete()


async def updateWelcome(msg: discord.Message):
    await msg.channel.send(welcome.format(bot.user.name, VERSION, config.sourceLink), embed=None)

bot.run(token)
