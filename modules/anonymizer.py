import asyncio
import random
from configparser import ConfigParser
from logging import Logger

import discord
from discord import Guild, ButtonStyle, Interaction
from discord.ui import View, Button, Select
from discord.utils import escape_mentions


class CancelButton(Button):
    def __init__(self):
        super().__init__(label="Zrušit", style=ButtonStyle.danger)

    async def callback(self, interaction: Interaction):
        overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False,
                                                                                 send_messages=False),
                     interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=False)
                     }
        await interaction.message.edit(content="Kanál se smaže za pár sekund", view=None)
        await interaction.channel.edit(topic="Deleting...", overwrites=overwrite)
        asyncio.create_task(self.delete(interaction.channel))

    async def delete(self, channel: discord.TextChannel):
        await asyncio.sleep(10)
        await channel.delete()


class RelayChannelSelection(Select):
    def __init__(self, channels: list[discord.TextChannel]):
        options: Select.options = []
        for channel in channels:
            options.append(discord.SelectOption(label=channel.name))
        super().__init__(options=options)

    async def callback(self, interaction: Interaction):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        try:
            await interaction.channel.edit(topic=self.values[0], overwrites=overwrites)
        except discord.Forbidden:
            pass
        edit_view = View()
        edit_view.add_item(CancelButton())
        await interaction.message.edit(content="Cílový kanál nastaven na {0}, napiš zprávu:".format(self.values[0]),
                                       view=edit_view)


class HiddenChannelMessageView(View):
    def __init__(self, channel_list: list[discord.TextChannel]):
        super().__init__()
        self.add_item(RelayChannelSelection(channel_list))
        self.add_item(CancelButton())


class InitExchange(Button):
    def __init__(self, config: ConfigParser, bot: discord.Bot) -> None:
        super().__init__(style=ButtonStyle.primary,
                         label="Let's go leak something",
                         custom_id="init_exchange")
        self.hidden_category_id: int = config.getint("Anonymizer", "hiddenCategoryId")
        self.study_category_id: int = config.getint("Anonymizer", "studyCategoryId")
        self.welcome_channel_id: int = config.getint("Global", "welcomeChannelId")
        self.bot = bot

    async def callback(self, interaction: discord.Interaction) -> None:
        channel_list = [channel for channel in await interaction.guild.fetch_channels()
                        if channel.category_id == self.hidden_category_id
                        and interaction.user in channel.members]

        response_content: str
        if len(channel_list) == 0:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=False)
            }
            new_channel = await interaction.guild.create_text_channel(
                name=str(random.randint(1, 10000)),
                category=await interaction.guild.fetch_channel(self.hidden_category_id),
                overwrites=overwrites
            )

            member: discord.Member = await interaction.guild.fetch_member(interaction.user.id)

            study_channels = [channel for channel in await interaction.guild.fetch_channels()
                              if channel.category_id == self.study_category_id
                              and channel.id != self.welcome_channel_id
                              and member in channel.members]
            study_channels.sort(key=lambda channel: channel.name)
            init_view: discord.ui.View = HiddenChannelMessageView(study_channels)
            await new_channel.send("Vyber si cílový kanál:", view=init_view)

            response_content = "Vytvořen kanál {0}.\nKanál se sám smaže za 10 minut".format(new_channel.mention)
            asyncio.create_task(channel_timeout(new_channel))

        else:
            response_content = "Kanál vytvořený pro tebe již existuje: {0}".format(channel_list[0].mention)

        await interaction.response.send_message(response_content, ephemeral=True)


async def channel_timeout(channel: discord.TextChannel):
    await asyncio.sleep(600)
    try:
        await channel.delete()
    except discord.NotFound:
        pass


class Anonymizer(discord.Cog):
    guild: Guild

    def __init__(self, bot: discord.Bot, logger: Logger, config: ConfigParser):
        self.bot = bot
        self.logger = logger
        self.hidden_category_id: int = config.getint("Anonymizer", "hiddenCategoryId")
        self.guild_id: int = config.getint("Global", "GuildId")

    @discord.Cog.listener()
    async def on_ready(self):
        self.guild = await self.bot.fetch_guild(self.guild_id)

    @discord.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.id == self.bot.user.id:
            return
        if msg.channel.type != discord.ChannelType.text:
            return
        if msg.channel.category_id != self.hidden_category_id:
            return

        channels = await self.guild.fetch_channels()

        target_channel: list[discord.TextChannel] = [channel for channel in channels if
                                                     channel.name == msg.channel.topic]
        if len(target_channel) == 0:
            self.logger.error("Didn't find channel {0}".format(msg.channel.topic))
            await msg.reply("Nenalezen cílový kanál {0}. Existuje ještě?".format(msg.channel.topic))
            return

        webhook: list[discord.Webhook] = await target_channel[0].webhooks()

        if len(webhook) == 0:
            name = "Hello there"
            webhook.append(await target_channel[0].create_webhook(name=name))

        avatar = "https://cdn.discordapp.com/icons/914813122689241129/042d4c00a55cb2b2a8ef6d5db652b8df.png?size=96"
        content = escape_mentions(msg.content)
        files = []
        for attachment in msg.attachments:
            f = await attachment.to_file()
            files.append(f)
        await webhook[0].send(content, files=files, avatar_url=avatar)

        overwrite = {msg.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                     msg.author: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
        await msg.reply(content="Odesláno\nKanál se smaže za pár sekund :+1:", view=None)
        await msg.channel.edit(topic="Deleting...", overwrites=overwrite)
        await asyncio.sleep(10)
        await msg.channel.delete()
