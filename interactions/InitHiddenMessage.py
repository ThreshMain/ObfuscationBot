import asyncio

import discord
from discord import Interaction, ButtonStyle
from discord.ui import View, Select, Button, button


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
        await interaction.channel.edit(topic=self.values[0], overwrites=overwrites)
        edit_view = View()
        edit_view.add_item(CancelButton())
        await interaction.message.edit(content="Cílový kanál nastaven na {0}, napiš zprávu:".format(self.values[0]),
                                       view=edit_view)


class HiddenChannelMessageView(View):
    def __init__(self, channel_list: list[discord.TextChannel]):
        super().__init__()
        self.add_item(RelayChannelSelection(channel_list))
        self.add_item(CancelButton())

