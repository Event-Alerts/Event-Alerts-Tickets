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

# CANCELBUTTON.PY
class CancelButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cancelled = False

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel_button")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cancelled = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=discord.Embed(description=f"Ticket closure cancelled by {interaction.user.mention}", color=discord.Color.green()))
        self.stop()