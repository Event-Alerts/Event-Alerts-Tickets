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
from PartnerInfo import PartnerInfo
from TicketInfo import TicketInfo
import utilities

# OPENVIEW.PY
class OpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="APPLY FOR PARTNER", emoji="🤝", style=discord.ButtonStyle.blurple, custom_id="partner_button")
    async def partner_button(self, interaction: discord.Interaction, button: discord.Button):
        # Check for existing tickets
        TICKET_CTGRY_ID = utilities.get_config("TICKET_CTGRY_ID")
        category = interaction.guild.get_channel(TICKET_CTGRY_ID)
        try:
            user_tickets = [channel for channel in category.text_channels if str(
                interaction.user.id) in channel.topic]
        except:
            user_tickets = []
        if len(user_tickets) >= 2:
            await interaction.response.send_message("You already have 2 open tickets. Please close an existing ticket before opening a new one.", ephemeral=True)
        else:
            await interaction.response.send_modal(PartnerInfo())

    @discord.ui.button(label="OPEN A SUPPORT TICKET", emoji="🎫", style=discord.ButtonStyle.gray, custom_id="ticket_button")
    async def ticket_button(self, interaction: discord.Interaction, button: discord.Button):
        # Check for existing tickets
        TICKET_CTGRY_ID = utilities.get_config("TICKET_CTGRY_ID")
        category = interaction.guild.get_channel(TICKET_CTGRY_ID)
        try:
            user_tickets = [channel for channel in category.text_channels if str(
                interaction.user.id) in channel.topic]
        except:
            user_tickets = []
        if len(user_tickets) >= 2:
            await interaction.response.send_message("You already have 2 open tickets. Please close an existing ticket before opening a new one.", ephemeral=True)
        else:
            await interaction.response.send_modal(TicketInfo())
