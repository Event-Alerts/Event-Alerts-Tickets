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
import utilities

# TICKETINFO.PY
class TicketInfo(discord.ui.Modal, title='TICKET INFORMATION'):

    ticketreason = discord.ui.TextInput(
        label='Why do you want to open a ticket?',
        style=discord.TextStyle.long,
        placeholder='Help! Someone is spamming!',
        required=True,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'**_Creating ticket channel..._**', ephemeral=True)
        cid = await utilities.create_ticket(client=interaction.client, username=interaction.user.name, memberid=interaction.user.id, reason=self.ticketreason)
        await interaction.edit_original_response(content=f'**_Done! -> <#{cid}>_**')
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            await interaction.response.send_message(f'**_Oops! Something went wrong._**', ephemeral=True)
        except:
            await interaction.edit_original_response(content='**_Oops! Something went wrong._**')
        print(error)