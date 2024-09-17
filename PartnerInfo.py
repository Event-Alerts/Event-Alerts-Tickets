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

# PARTNERINFO.PY
class PartnerInfo(discord.ui.Modal, title='PARTNER INFORMATION'):

    servername = discord.ui.TextInput(
        label='Your servers name',
        placeholder='Oink events',
        max_length=20,
        required=True,
    )
    partnerreason = discord.ui.TextInput(
        label='Why do you want to apply for partner?',
        style=discord.TextStyle.long,
        placeholder='My server is pog!',
        required=True,
        max_length=400,
    )
    invite = discord.ui.TextInput(
        label='Your invite link',
        placeholder='https://discord.com/invite/yourserver',
        max_length=100,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'**_Creating ticket channel..._**', ephemeral=True)
        try:
            member_count, self.invite = utilities.format_url(str(self.invite))
        except:
            member_count = None
        if member_count:
            cid = await utilities.create_partner_ticket(client=interaction.client, username=interaction.user.name, servername=self.servername, memberid=interaction.user.id, invite=self.invite, reason=self.partnerreason)
            await interaction.edit_original_response(content=f'**_Done! -> <#{cid}>_**')
        else:
            await interaction.edit_original_response(content='**_Error! Invalid invite link!_**')

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            await interaction.response.send_message(f'**_Oops! Something went wrong._**', ephemeral=True)
        except:
            await interaction.edit_original_response(content='**_Oops! Something went wrong._**')
        print(error)
