# Copyright (C) 2024  QWERTZexe

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

######################################################

# IMPORTS
import discord
import asyncio
from CancelButton import CancelButton
import utilities

# CLOSETICKET.PY
class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "TICKET" not in interaction.channel.topic:
            await interaction.response.send_message("This button can only be used in ticket channels.", ephemeral=True)
            return

        view = CancelButton()
        embed = discord.Embed(
            title="Ticket Closure",
            description=f"This ticket will be closed in 10 seconds. Click 'Cancel' to stop.",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed, view=view)

        try:
            await asyncio.wait_for(view.wait(), timeout=10)
        except asyncio.TimeoutError:
            if not view.cancelled:
                await utilities.close_ticket(interaction.client, interaction.channel, interaction.user)
