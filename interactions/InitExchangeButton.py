from discord.ui import button, View, Button
from discord.enums import ButtonStyle
import discord

import interactions.InitHiddenMessage
from config import Config


class InitExchange(View):
    def __init__(self, config: Config, bot: discord.Bot) -> None:
        super().__init__(timeout=None)
        self.config = config
        self.bot = bot

    @button(style=ButtonStyle.primary, label="Let's go leak something", custom_id="init_exchange")
    async def callback(self, but: Button, interaction: discord.Interaction) -> None:
        channel_list = [channel for channel in await interaction.guild.fetch_channels()
                        if channel.category_id == self.config.hiddenCategoryId and channel.name == interaction.user.name]

        response_content: str
        if len(channel_list) == 0:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                self.bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_roles=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=False)
            }
            new_channel = await interaction.guild.create_text_channel(
                name=interaction.user.name,
                category=await interaction.guild.fetch_channel(self.config.hiddenCategoryId),
                overwrites=overwrites
            )

            study_channels = [channel for channel in await interaction.guild.fetch_channels()
                              if channel.category_id == self.config.studyCategoryId and channel.id != self.config.welcomeChannelId]
            init_view: discord.ui.View = interactions.InitHiddenMessage.HiddenChannelMessageView(study_channels)
            await new_channel.send("Vyber si cílový kanál:", view=init_view)

            response_content = "Vytvořen kanál {0}.".format(new_channel.mention)

        else:
            response_content = "Kanál vytvořený pro tebe již existuje: {0}".format(channel_list[0].mention)

        await interaction.response.send_message(response_content, ephemeral=True)
