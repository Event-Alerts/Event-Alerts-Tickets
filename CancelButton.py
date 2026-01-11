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
    def __init__(self, close_callback=None, close_args=None):
        super().__init__(timeout=None)
        self.cancelled = False
        self.closed_now = False
        self.close_callback = close_callback  # Function to call for closing
        self.close_args = close_args or []    # Arguments for the close function

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="<:vnnocleardark:1095912337162129418>", custom_id="cancel_button")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cancelled = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            embed=discord.Embed(
                description=f"Ticket closure cancelled by {interaction.user.mention}",
                color=discord.Color.green()
            )
        )
        self.stop()

    @discord.ui.button(label="Close Now", style=discord.ButtonStyle.gray, emoji="<:vntrashclear:1095912428597948507>", custom_id="close_now_button")
    async def close_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.closed_now = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            embed=discord.Embed(
                description=f"Ticket closed immediately by {interaction.user.mention}",
                color=discord.Color.red()
            )
        )
        if self.close_callback:
            await self.close_callback(*self.close_args)
        self.stop()
