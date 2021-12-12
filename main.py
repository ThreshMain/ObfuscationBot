import os
from config import Config
import discord
from discord.ext import commands
from interactions.InitExchangeButton import InitExchange
import logging
import re

VERSION = "DEV"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DiscordBot')

config: Config = Config(logger)
token: str = os.getenv("TOKEN")
pattern = re.compile("^(.{3}):", re.IGNORECASE)

bot = commands.Bot(command_prefix="!", owner_id=470490558713036801, intents=discord.Intents.all())
guild: discord.Guild


def create_welcome_embed() -> discord.Embed:
    welcome_embed: discord.Embed = discord.Embed(colour=discord.Color.orange())
    welcome_embed.title = "Obfuscation bot"
    welcome_embed.url = config.sourceLink
    welcome_embed.description = "Ahoj, tenhle bot anonymně přeposílá veškeré zprávy v tomto kanále do cílového kanálu tvé volby.\n\
    Zprávy mohou obsahovat přílohy."
    welcome_embed.set_footer(text=VERSION)
    welcome_embed.add_field(
        name="Formát zprávy",
        value="Zprávy potřebují prefix ve formátu kódu předmětu a dvojtečky.\nEg. `pa1:Špagetový kód je překrásný`",
        inline=False)
    return welcome_embed


@bot.event
async def on_ready():
    logging.info("Joined as {0.name}".format(bot.user))
    global guild
    guild = await bot.fetch_guild(config.GuildId)
    channel: discord.TextChannel = [channel for channel in await guild.fetch_channels() if channel.id == config.welcomeChannelId][0]
    try:
        welcome_message: discord.Message = await channel.fetch_message(config.welcomeMessageId)
        await welcome_message.edit(content="",
                                   embed=create_welcome_embed(),
                                   view=InitExchange(config, bot))
    except discord.NotFound:
        await channel.send(embed=create_welcome_embed(),
                           view=InitExchange(config, bot))

"""
@bot.event
async def on_message(msg: discord.Message):
    if msg.author.id == bot.user.id:
        return
    if msg.channel.id != config.listeningChannel and msg.channel.type != discord.ChannelType.private:
        return

    match: re.Match = re.match(pattern, msg.content)
    if match is None or config.channelMap.get(match.group(1)) is None:
        content = "Invalid taget channel, use prefixes like `dml:` or `uos:` to send a message to the corresponding channel"
        content += "\n" + msg.content
        await msg.author.send(content)
        await msg.delete()
        return

    channels = await guild.fetch_channels()

    targetChannel: list[discord.TextChannel] = [channel for channel in channels if channel.id == config.channelMap.get(match.group(1))]

    webhook: list[discord.Webhook] = await targetChannel[0].webhooks()

    if len(webhook) == 0:
        name = "Hello there"
        webhook.append(await targetChannel[0].create_webhook(name=name))

    avatar = "https://cdn.discordapp.com/icons/914813122689241129/042d4c00a55cb2b2a8ef6d5db652b8df.png?size=96"
    content = escape_mentions(msg.content[4:])
    files = []
    for attachment in msg.attachments:
        f = await attachment.to_file()
        files.append(f)
    await webhook[0].send(content, files=files, avatar_url=avatar)
    await msg.delete()
"""

bot.run(token)
