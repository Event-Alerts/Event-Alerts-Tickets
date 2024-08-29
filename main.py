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
import os
import sys
import discord
import json
from discord.utils import get
import asyncio
from discord import app_commands
from CloseTicket import CloseTicket
from CancelButton import CancelButton
from OpenView import OpenView
import utilities

# THE HOLY CWD
cwd = os.path.dirname(os.path.abspath(sys.argv[0]))

# CONSTS
if not os.path.exists(f"{cwd}/config.json"):
    with open(f"{cwd}/config.json", "w") as f:
        json.dump({"TOKEN": "YOUR_TOKEN", "SERVER_ID": "YOUR_SERVER_ID",
                   "STORAGE_SERVER_ID": "YOUR_STORAGE_SERVER_ID", "STORAGE_CHANNEL_ID": "YOUR_STORAGE_CHANNEL_ID",
                   "MOD_ROLE_ID": "YOUR_MOD_ROLE_ID", "TRANSCRIPT_CHNL_ID": "YOUR_TRANSCRIPT_CHNL_ID",
                   "TICKET_CTGRY_ID": "YOUR_TICKET_CTGRY_ID", "PING_ROLE": "YOUR_PING_ROLE",
                   "LOG_CHNL_ID": "YOUR_LOG_CHNL_ID", "MUTED_ROLE_ID": "MUTED_ROLE_ID"}, f)

TOKEN, SERVER_ID, STORAGE_SERVER_ID, STORAGE_CHANNEL_ID, MOD_ROLE_ID, TRANSCRIPT_CHNL_ID, TICKET_CTGRY_ID, PING_ROLE, LOG_CHNL_ID, MUTED_ROLE_ID = utilities.get_config()

# SETUP
intents = discord.Intents.all()
activity = discord.Activity(
    type=discord.ActivityType.listening, name="Oink! Oink!")
client = discord.AutoShardedClient(
    shard_count=1, intents=intents, activity=activity)
tree = app_commands.CommandTree(client)


# MAIN
@client.event
async def on_ready():
    print("Bot prefix is: /")
    await tree.sync()
    print("Tree synced!")
    client.add_view(OpenView())
    print("Added start view!")
    print("READY\n")


@client.event
async def on_message(message):
    print(message)


@app_commands.command(description="ADMIN ONLY | Send the ticket msg!")
async def ticketmsg(interaction: discord.Interaction, channel: discord.TextChannel):
    if interaction.user.guild_permissions.administrator or interaction.user.id == 971316880243576862:
        em = discord.Embed(description=f'Do NOT open a ticket to "see what it does" or for matters that do not concern us\nWe **will** punish you for opening a ticket for an invalid reason',
                           title=":sos: Event Alerts Support", color=discord.Color.red())
        em.add_field(name=":handshake: Applying for Partner",
                     value="Please read all of the requirements and necessary information **[HERE](https://discord.com/channels/970411885293895801/970415677393477734/1179203344917614662)**\nOnce you're ready, you can click the ``APPLY FOR PARTNER`` button below!")
        em.add_field(name=":ticket: General server support",
                     value="If you have any other questions about the server, feel free to create a ticket to ask us\nJust click the ``OPEN A SUPPORT TICKET`` button below to get started!")
        view = OpenView()
        await channel.send(embed=em, view=view)
        await interaction.response.send_message("**Done!**", ephemeral=True)
    else:
        await interaction.response.send_message("No permission!", ephemeral=True)


@app_commands.command(description="Close the current ticket")
@app_commands.describe(time="Time until closure (e.g., 10s, 5m, 1h, 7d). Default: 10 seconds")
async def close(interaction: discord.Interaction, time: str = None):
    if "TICKET" not in interaction.channel.topic:
        await interaction.response.send_message(embed=discord.Embed(description="This command can only be used in ticket channels.", color=discord.Color.red()), ephemeral=True)
        return

    seconds = utilities.parse_time(time)

    view = CancelButton()
    embed = discord.Embed(
        title="Ticket Closure",
        description=f"This ticket will be closed in {seconds} seconds. Click 'Cancel' to stop.",
        color=discord.Color.yellow()
    )
    await interaction.response.send_message(embed=embed, view=view)

    try:
        await asyncio.wait_for(view.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        if not view.cancelled:
            await utilities.close_ticket(interaction.client, interaction.channel, interaction.user)


@app_commands.command(description="STAFF ONLY | Change the priority of the current ticket")
@app_commands.describe(priority="The priority of the current ticket")
@app_commands.choices(priority=[
    app_commands.Choice(name="Waiting to close", value="🕑"),
    app_commands.Choice(name="Waiting for something to happen", value="⏩"),
    app_commands.Choice(name="Mod Attention", value="🟡"),
    app_commands.Choice(name="ADMIN ATTENTION", value="🔴"),
    app_commands.Choice(name="Their Turn", value="👍")
])
async def priority(interaction: discord.Interaction, priority: app_commands.Choice[str]):
    if "TICKET" not in interaction.channel.topic:
        await interaction.response.send_message(embed=discord.Embed(description="This command can only be used in ticket channels.", color=discord.Color.red()), ephemeral=True)
        return
    await interaction.response.defer(thinking=True)
    member = interaction.user
    if get(member.roles, id=MOD_ROLE_ID) or member.id == 971316880243576862 or interaction.user.guild_permissions.administrator:
        try:
            await interaction.channel.edit(name=f"{priority.value}{interaction.channel.name[1:]}")
            err = 0
        except:
            err = 1
        if err == 0:
            await interaction.followup.send(f"Successfully changed the ticket priority to {priority.name}!", ephemeral=True)
        else:
            await interaction.followup.send(f"**__ERROR__** changing the ticket priority!", ephemeral=True)
    else:
        await interaction.followup.send("Sorry, this command is only for staff!", ephemeral=True)


@app_commands.command(description="STAFF ONLY | Add someone to the current ticket")
@app_commands.describe(member="The member to add to the current ticket")
async def add(interaction: discord.Interaction, member: discord.Member):
    if "TICKET" not in interaction.channel.topic:
        await interaction.response.send_message(embed=discord.Embed(description="This command can only be used in ticket channels.", color=discord.Color.red()), ephemeral=True)
        return
    await interaction.response.defer(thinking=True)

    if get(interaction.user.roles, id=MOD_ROLE_ID) or interaction.user.id == 971316880243576862 or interaction.user.guild_permissions.administrator:
        try:
            await interaction.channel.set_permissions(member, read_messages=True, send_messages=True)
            err = 0
        except:
            err = 1
        if err == 0:
            await interaction.followup.send(f"Successfully added {member.mention} to the ticket!")
            log_channel = client.get_channel(LOG_CHNL_ID)
            await log_channel.send(f"<@{str(interaction.user.id)}> Just ADDED {member.mention} from a ticket opened by: <@{str(interaction.channel.topic.split('-')[-1])}> ({interaction.channel.mention})")
        else:
            await interaction.followup.send(f"**__ERROR__** adding someone to the ticket!", ephemeral=True)
    else:
        await interaction.followup.send(f"Sorry, this command is only for staff!", ephemeral=True)


@app_commands.command(description="STAFF ONLY | Remove someone from the current ticket")
@app_commands.describe(member="The member to remove from the current ticket")
async def remove(interaction: discord.Interaction, member: discord.Member):
    if "TICKET" not in interaction.channel.topic:
        await interaction.response.send_message(embed=discord.Embed(description="This command can only be used in ticket channels.", color=discord.Color.red()), ephemeral=True)
        return
    await interaction.response.defer(thinking=True)

    if get(interaction.user.roles, id=MOD_ROLE_ID) or interaction.user.id == 971316880243576862 or interaction.user.guild_permissions.administrator:
        try:
            await interaction.channel.set_permissions(member, read_messages=False, send_messages=False)
            err = 0
        except:
            err = 1
        if err == 0:
            await interaction.followup.send(f"Successfully removed {member.mention} from the ticket!")
            log_channel = client.get_channel(LOG_CHNL_ID)
            await log_channel.send(f"<@{str(interaction.user.id)}> Just REMOVED {member.mention} from a ticket opened by: <@{str(interaction.channel.topic.split('-')[-1])}> ({interaction.channel.mention})")
        else:
            await interaction.followup.send(f"**__ERROR__** removing someone to the ticket!", ephemeral=True)
    else:
        await interaction.followup.send(f"Sorry, this command is only for staff!", ephemeral=True)


@app_commands.command(description="STAFF ONLY | Bump the current ticket")
async def bump(interaction: discord.Interaction):
    if "TICKET" not in interaction.channel.topic:
        await interaction.response.send_message(embed=discord.Embed(description="This command can only be used in ticket channels.", color=discord.Color.red()), ephemeral=True)
        return

    if get(interaction.user.roles, id=MOD_ROLE_ID) or interaction.user.id == 971316880243576862 or interaction.user.guild_permissions.administrator:
        await interaction.response.defer(thinking=True,ephemeral=True)
        try:
            member = interaction.channel.topic.split("-")[1]
            em = discord.Embed(title="Are you still here?",
                               description="We have received no feedback from your side recently", color=discord.Color.yellow())
            await interaction.channel.send(f"Hello <@{member}> :wave:", embed=em)
            err = 0
        except:
            err = 1
        if err == 0:
            await interaction.followup.send(f"Successfully bumped the ticket!", ephemeral=True)
        else:
            await interaction.followup.send(f"**__ERROR__** bumping the ticket!", ephemeral=True)
    else:
        await interaction.followup.send(f"Sorry, this command is only for staff!", ephemeral=True)

# ADDING COMMANDS
tree.add_command(ticketmsg)
tree.add_command(close)
tree.add_command(priority)
tree.add_command(add)
tree.add_command(remove)
tree.add_command(bump)

# RUNNING
client.run(TOKEN)
