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

async def closeTicket(interaction: discord.Interaction, timer: int = 10, force: bool = False):
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
    if (str(interaction.user.id) in interaction.channel.topic or force):
        await closeTicketCountdown(interaction, timer)
    else:
        await closeTicketRequest(interaction)

async def closeTicketCountdown(interaction: discord.Interaction, timer: int = 10):
    channel_id = interaction.channel.id
    # Mark as scheduled for closure
    scheduled_closures.add(channel_id)

    view = CancelButton(close_callback=utilities.close_ticket, close_args=[interaction.client, interaction.channel, interaction.user])
    embed = discord.Embed(
        title="Ticket Closure",
        description=f"This ticket will be closed in {timer} seconds. Click ``Cancel`` to stop.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, view=view)

    try:
        await asyncio.wait_for(view.wait(), timeout=timer)
    except asyncio.TimeoutError:
        if not getattr(view, "cancelled", False):
            await utilities.close_ticket(interaction.client, interaction.channel, interaction.user)
    finally:
        # Remove from scheduled closures regardless of outcome
        scheduled_closures.discard(channel_id)

# CLOSETICKETREQUEST.PY
class CloseTicketRequest(discord.ui.View):
    def __init__(self, requester, client, channel):
        super().__init__(timeout=60)  # Timeout after 60 seconds if no response
        self.requester = requester
        self.client = client
        self.channel = channel
        self.response_handled = False

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.response_handled:
            return
        self.response_handled = True
        await interaction.response.edit_message(content="Ticket has been closed.", view=self)
        await utilities.close_ticket(self.client, self.channel, self.requester)
        self.disable_all_buttons()

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.response_handled:
            return
        self.response_handled = True
        self.disable_all_buttons()
        cancel_embed = discord.Embed(
            title="Ticket Closure Cancelled",
            description=f"Ticket close request by {self.requester.mention} has been rejected.",
            color=discord.Color.orange()
        )
        await interaction.response.edit_message(embed=cancel_embed, view=self)

async def closeTicketRequest(interaction: discord.Interaction):
    """Ask other users for confirmation before closing a ticket."""
    embed = discord.Embed(
        title="Can this ticket be closed?",
        description=f"{interaction.user.mention} wants to close this ticket. "
                    "Click **Accept** to close it now, or **Reject** if you still need help.",
        color=discord.Color.yellow()
    )
    view = CloseTicketRequest(interaction.user, interaction.client, interaction.channel)
    userid = interaction.channel.topic.split("-")[1]
    await interaction.response.send_message(f"<@{userid}>", embed=embed, view=view, ephemeral=False)