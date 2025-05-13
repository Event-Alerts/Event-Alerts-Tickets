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

# ADMININFO.PY
class AdminInfo(discord.ui.Modal, title='Admin Ticket Information'):

    ticketreason = discord.ui.TextInput(
        label='Ticket Reason',
        style=discord.TextStyle.long,
        placeholder='Help, someone is spamming!',
        required=True,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'**_Creating ticket channel..._**', ephemeral=True)
        cid = await utilities.create_admin_ticket(client=interaction.client, username=interaction.user.name, memberid=interaction.user.id, reason=self.ticketreason)
        await interaction.edit_original_response(content=f'<:eaticketyes:1371503431356911818> Ticket created! <#{cid}>')

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            await interaction.response.send_message(f'<:eaticketno:1371503463673892988> Encountered an unexpected error, please contact server staff!', ephemeral=True)
        except:
            await interaction.edit_original_response(content='<:eaticketno:1371503463673892988> Encountered an unexpected error, please contact server staff!')
        print(error)
