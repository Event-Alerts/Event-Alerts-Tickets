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
from AdminInfo import AdminInfo
from TicketInfo import TicketInfo
import utilities

# OPENVIEW.PY
class OpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open a support ticket", emoji="🎫", style=discord.ButtonStyle.gray, custom_id="ticket_button")
    async def ticket_button(self, interaction: discord.Interaction, button: discord.Button):
        # Check for existing tickets
        TICKET_CATEGORY_ID = utilities.get_config("TICKET_CATEGORY_ID")
        category = await interaction.client.fetch_channel(TICKET_CATEGORY_ID)
        user_tickets = []
        for channel in category.channels:
            try:
                if str(interaction.user.id) in channel.topic:
                    user_tickets.append(channel)
            except:
                pass
        if len(user_tickets) >= 2:
            await interaction.response.send_message("You already have 2 open tickets. Please close an existing ticket before opening a new one.", ephemeral=True)
        else:
            await interaction.response.send_modal(TicketInfo())

    @discord.ui.button(label="Contact the Admins", emoji="⚠️", style=discord.ButtonStyle.red, custom_id="admin_button")
    async def admin_button(self, interaction: discord.Interaction, button: discord.Button):
        # Check for existing tickets
        ADMIN_TICKET_CATEGORY_ID = utilities.get_config("ADMIN_TICKET_CATEGORY_ID")
        category = await interaction.client.fetch_channel(ADMIN_TICKET_CATEGORY_ID)
        user_tickets = []
        for channel in category.channels:
            try:
                if str(interaction.user.id) in channel.topic:
                    user_tickets.append(channel)
            except:
                pass
        if len(user_tickets) >= 2:
            await interaction.response.send_message("You already have 2 open tickets. Please close an existing ticket before opening a new one.", ephemeral=True)
        else:
            await interaction.response.send_modal(AdminInfo())