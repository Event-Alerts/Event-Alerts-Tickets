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

# Set to keep track of channels scheduled for closure
scheduled_closures = set()

# CLOSETICKET.PY
class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="<:eatickettrash:1371926108555055215>", custom_id="close_ticket_button")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await closeTicket(interaction)

async def closeTicket(interaction: discord.Interaction):
    channel_id = interaction.channel.id

    # Check if already scheduled for closure
    if channel_id in scheduled_closures:
        await interaction.response.send_message(
            "This ticket is already scheduled for closure.", ephemeral=True
        )
        return

    if "TICKET" not in (interaction.channel.topic or ""):
        await interaction.response.send_message(
            "This button can only be used in ticket channels.", ephemeral=True
        )
        return

    # Mark as scheduled for closure
    scheduled_closures.add(channel_id)

    view = CancelButton(close_callback=utilities.close_ticket, close_args=[interaction.client, interaction.channel, interaction.user])
    embed = discord.Embed(
        title="Ticket Closure",
        description=f"This ticket will be closed in 10 seconds. Click ``Cancel`` to stop.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, view=view)

    try:
        await asyncio.wait_for(view.wait(), timeout=10)
    except asyncio.TimeoutError:
        if not getattr(view, "cancelled", False):
            await utilities.close_ticket(interaction.client, interaction.channel, interaction.user)
    finally:
        # Remove from scheduled closures regardless of outcome
        scheduled_closures.discard(channel_id)
