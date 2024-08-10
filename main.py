#Copyright (C) 2024  QWERTZexe

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published
#by the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU Affero General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

######################################################

# IMPORTS
import os
import sys
import requests
import discord
import json
from operator import itemgetter
from discord.ext import commands
from discord.utils import get
import mimetypes
import asyncio
from bs4 import BeautifulSoup
import re
import io
import html
from discord.ext import tasks
from discord import app_commands

### THE HOLY CWD
cwd = os.path.dirname(os.path.abspath(sys.argv[0]))

### CONSTS
if not os.path.exists(f"{cwd}/config.json"):
    with open(f"{cwd}/config.json", "w") as f:
        json.dump({"TOKEN":"YOUR_TOKEN","SERVER_ID":"YOUR_SERVER_ID",
                   "STORAGE_SERVER_ID":"YOUR_STORAGE_SERVER_ID","STORAGE_CHANNEL_ID":"YOUR_STORAGE_CHANNEL_ID",
                   "MOD_ROLE_ID":"YOUR_MOD_ROLE_ID","TRANSCRIPT_CHNL_ID":"YOUR_TRANSCRIPT_CHNL_ID",
                   "TICKET_CTGRY_ID":"YOUR_TICKET_CTGRY_ID","PING_ROLE":"YOUR_PING_ROLE",
                   "LOG_CHNL_ID":"YOUR_LOG_CHNL_ID"}, f)


with open(f"{cwd}/config.json", "r") as f:
    config = json.load(f)
    TOKEN = config["TOKEN"]
    SERVER_ID = int(config["SERVER_ID"])
    STORAGE_SERVER_ID = int(config["STORAGE_SERVER_ID"])
    STORAGE_CHANNEL_ID = int(config["STORAGE_CHANNEL_ID"])
    MOD_ROLE_ID = int(config["MOD_ROLE_ID"])
    TRANSCRIPT_CHNL_ID = int(config["TRANSCRIPT_CHNL_ID"])
    TICKET_CTGRY_ID = int(config["TICKET_CTGRY_ID"])
    PING_ROLE = int(config["PING_ROLE"])
    LOG_CHNL_ID = int(config["LOG_CHNL_ID"])
### SETUP
intents = discord.Intents.all()
activity = discord.Activity(type=discord.ActivityType.listening, name="Oink! Oink!")
client = discord.AutoShardedClient(shard_count=1,intents=intents, activity=activity)
tree = app_commands.CommandTree(client)

### MAIN

def get_discord_member_count(invite_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    if invite_url.startswith("https://discord.com/") or invite_url.startswith("http://discord.com/") or invite_url.startswith("https://discord.gg/") or invite_url.startswith("http://discord.gg/"):
        response = requests.get(invite_url, headers=headers)
    elif invite_url.startswith("discord.com/") or invite_url.startswith("discord.gg/"):
        response = requests.get(f"https://{invite_url}", headers=headers)
    elif invite_url.startswith(".gg/"):
        response = requests.get(f"https://discord{invite_url}", headers=headers)   
    elif invite_url.startswith("gg/"):
        response = requests.get(f"https://discord.{invite_url}", headers=headers)   
    else:
        response = requests.get(f"https://discord.gg/{invite_url}", headers=headers)   
    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract member count from the HTML
    member_count_element = soup.find('meta', property='og:description')
    if member_count_element:
        description = member_count_element['content']
        member_count = extract_member_count(description)
        return member_count
    else:
        print("Member count element not found in the page.")
        return None

def extract_member_count(description):
    try:
        parts = description.split()
        for i, part in enumerate(parts):
            if part.lower() == 'members':
                return parts[i-1]
        return None
    except Exception as e:
        print(f"Error extracting member count: {e}")
        return None

def parse_time(time_str):
    if not time_str:
        return 10  # Default to 10 seconds
    
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.match(r"(\d+)([smhd])?$", time_str.lower())
    
    if not match:
        return 10  # Default to 10 seconds if invalid format
    
    value, unit = match.groups()
    return int(value) * units.get(unit, 1)

async def close_ticket(channel):
    storage_guild = await client.fetch_guild(STORAGE_SERVER_ID)
    storage_channel = await storage_guild.fetch_channel(STORAGE_CHANNEL_ID)

    # Generate markdown and HTML transcripts
    markdown_transcript = f"# Transcript for {channel.name}\n\n"
    html_transcript = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
                color: #FFFFFF;
                transition: background 0.3s ease;
                margin: 0;
                padding: 20px;
            }}
            .gradient-bg {{
            background: linear-gradient(270deg, #7289DA, #4E5D94, #2C2F33);
            transition: background 0.3s ease;
            animation: gradient 15s ease infinite;
            background-size: 400% 400%;

            }}
            .simple-bg {{
            background:  #36393F;
            }}
            #toggle-bg {{
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px;
            background: #333;
            color: #fff;
            border: none;
            cursor: pointer;
            }}
            @keyframes gradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            .message {{
                margin-bottom: 20px;
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 5px;
                padding: 10px;
            }}
            .message-header {{
                display: flex;
                align-items: center;
                margin-bottom: 5px;
            }}
            .avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin-right: 10px;
            }}
            .username {{
                font-weight: bold;
                margin-right: 10px;
            }}
            .timestamp {{
                color: #99AAB5;
                font-size: 0.8em;
            }}
            .content {{
                white-space: pre-wrap;
            }}
            .embed {{
                border-left: 4px solid #7289DA;
                padding: 8px;
                margin: 5px 0;
                background-color: rgba(0, 0, 0, 0.6);
            }}
            .embed-title {{ font-weight: bold; }}
            .embed-field {{ margin-top: 5px; }}
            .embed-field-name {{ font-weight: bold; }}
            .attachment {{ margin-top: 5px; }}
        </style>
    </head>
    <body class="simple-bg">
    <button id="toggle-bg">Toggle Background</button>
    <h1>Transcript for {channel.name}</h1>
    """

    async for message in channel.history(limit=None, oldest_first=True):
        # Markdown format
        markdown_transcript += f"**{message.author.name}** ({message.created_at.strftime('%Y-%m-%d %H:%M:%S')}): {message.content}\n"
        
        # HTML format
        avatar_url = message.author.avatar.url if message.author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        html_transcript += f"""
        <div class="message">
            <div class="message-header">
                <img src="{avatar_url}" class="avatar" alt="{html.escape(message.author.name)}">
                <span class="username">{html.escape(message.author.name)}</span>
                <span class="timestamp">{message.created_at.strftime("%Y-%m-%d %H:%M:%S")}</span>
            </div>
            <div class="content">{format_content_html(message.content)}</div>
        """

        # Handle attachments
        for attachment in message.attachments:
            mime_type, _ = mimetypes.guess_type(attachment.filename)
            if mime_type and mime_type.startswith('image'):
                file = await attachment.to_file()
                storage_message = await storage_channel.send(file=file)
                new_url = storage_message.attachments[0].url
                html_transcript += f'<div class="attachment"><img src="{new_url}" alt="{html.escape(attachment.filename)}" style="max-width: 300px;"></div>'
            else:
                file = await attachment.to_file()
                storage_message = await storage_channel.send(file=file)
                new_url = storage_message.attachments[0].url
                markdown_transcript += f"[Attachment: {attachment.filename}]({new_url})\n"
                html_transcript += f'<div class="attachment"><a href="{new_url}">Attachment: {html.escape(attachment.filename)}</a></div>'

        # Add embeds to transcript
        for embed in message.embeds:
            markdown_transcript += format_embed_markdown(embed) + "\n"
            html_transcript += format_embed_html(embed)

        html_transcript += '</div>'
        markdown_transcript += "\n"

    html_transcript += """
        <script>
        const body = document.body;
        const toggleBtn = document.getElementById('toggle-bg');
        toggleBtn.addEventListener('click', () => {
            body.classList.toggle('gradient-bg');
            body.classList.toggle('simple-bg');
        });
        </script>
        </body>
        </html>"""

    markdown_file = discord.File(io.StringIO(markdown_transcript), filename=f"{channel.name}_transcript.md")
    html_file = discord.File(io.StringIO(html_transcript), filename=f"{channel.name}_transcript.html")

    transcript_channel = channel.guild.get_channel(TRANSCRIPT_CHNL_ID)
    await transcript_channel.send(embed=discord.Embed(description=f"Transcripts for {channel.name}", color=discord.Color.blue()), files=[markdown_file, html_file])

    # Close the ticket
    await channel.delete()

def format_embed_markdown(embed):
    md = f"**{embed.title or ''}**\n{embed.description or ''}\n"
    for field in embed.fields:
        md += f"\n**{field.name}**\n{field.value}\n"
    if embed.footer:
        md += f"\n*{embed.footer.text}*"
    return md

def format_embed_html(embed):
    embed_html = '<div class="embed">'
    if embed.title:
        embed_html += f'<div class="embed-title">{html.escape(embed.title)}</div>'
    if embed.description:
        embed_html += f'<div class="embed-description">{format_content_html(embed.description)}</div>'
    for field in embed.fields:
        embed_html += f'<div class="embed-field"><div class="embed-field-name">{html.escape(field.name)}</div><div class="embed-field-value">{format_content_html(field.value)}</div></div>'
    if embed.footer:
        embed_html += f'<div class="embed-footer">{html.escape(embed.footer.text)}</div>'
    embed_html += '</div>'
    return embed_html

def format_content_html(content):
    # Convert markdown to HTML
    content = html.escape(content)
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    content = re.sub(r'__(.*?)__', r'<u>\1</u>', content)
    content = re.sub(r'~~(.*?)~~', r'<strike>\1</strike>', content)
    content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
    content = content.replace('\n', '<br>')
    return content
async def create_partner_ticket(username: str, servername: str, members: str | int, memberid: int, invite: str, reason: str) -> str:
    guild = await client.fetch_guild(SERVER_ID)
    category: discord.CategoryChannel = await client.fetch_channel(TICKET_CTGRY_ID)
    done_user = username.lower().replace(" ","-")
    channel = await category.create_text_channel(name=f"🟡p-{done_user}")
    await channel.edit(topic=f"TICKET-{str(memberid)}")
    # Set up permissions
    await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
    
    # Allow the ticket creator to see and write in the channel
    member = await guild.fetch_member(memberid)
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    
    # Allow users with the mod role to see and write in the channel
    mod_role = guild.get_role(MOD_ROLE_ID)
    await channel.set_permissions(mod_role, read_messages=True, send_messages=True)
    em=discord.Embed(title=f"Partner Application - {servername}", description=f"Hello {username}! Your application ticket has been created!\n\n**__Information:__**\n**Servername:** ``{servername}``\n**Members:** ``{str(members)}``\n**Invite:** ``{invite}``\n**Partner reason:** ``{reason}``",color=discord.Color.yellow())
    em.set_footer(text="EVENT ALERTS - TICKETS",icon_url="https://cdn.discordapp.com/avatars/1142603508827299883/8115d0ff74451c2450da1f58733cf22d.png")
    await channel.send(content=f"<@{str(memberid)}>",embed=em,view=CloseTicketView())
    return str(channel.id)
async def create_ticket(username: str, memberid: int, reason: str) -> str:
    guild = await client.fetch_guild(SERVER_ID)
    category: discord.CategoryChannel = await client.fetch_channel(TICKET_CTGRY_ID)
    done_user = username.lower().replace(" ","-")
    channel = await category.create_text_channel(name=f"🟡t-{done_user}")
    await channel.edit(topic=f"TICKET-{str(memberid)}")
    # Set up permissions
    await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
    
    # Allow the ticket creator to see and write in the channel
    member = await guild.fetch_member(memberid)
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    
    # Allow users with the mod role to see and write in the channel
    mod_role = guild.get_role(MOD_ROLE_ID)
    await channel.set_permissions(mod_role, read_messages=True, send_messages=True)
    em=discord.Embed(title=f"Ticket - {username}", description=f"Hello {username}! Your ticket has been created!\n\n**__Information:__**\n**Ticket Reason:** ``{reason}``",color=discord.Color.yellow())
    em.set_footer(text="EVENT ALERTS - TICKETS",icon_url="https://cdn.discordapp.com/avatars/1142603508827299883/8115d0ff74451c2450da1f58733cf22d.png")
    await channel.send(content=f"<@{str(memberid)}>",embed=em,view=CloseTicketView())
    return str(channel.id)
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "TICKET" not in interaction.channel.topic:
            await interaction.response.send_message("This button can only be used in ticket channels.", ephemeral=True)
            return

        view = CancelButton()
        embed = discord.Embed(
            title="Ticket Closure",
            description=f"This ticket will be closed in 10 seconds. Click 'Cancel' to stop.",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed, view=view)

        try:
            await asyncio.wait_for(view.wait(), timeout=10)
        except asyncio.TimeoutError:
            if not view.cancelled:
                await close_ticket(interaction.channel)
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
            member_count = get_discord_member_count(str(self.invite))
        except:
            member_count = None
        if member_count:
            cid = await create_partner_ticket(username=interaction.user.name, servername=self.servername,members=member_count,memberid=interaction.user.id,invite=self.invite,reason=self.partnerreason)
            await interaction.edit_original_response(content=f'**_Done! -> <#{cid}>_**')
        else:
            await interaction.edit_original_response(content='**_Error! Invalid invite link!_**')
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            await interaction.response.send_message(f'**_Oops! Something went wrong._**', ephemeral=True)
        except:
            await interaction.edit_original_response(content='**_Oops! Something went wrong._**')
        print(error)
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
        cid = await create_ticket(username=interaction.user.name,memberid=interaction.user.id,reason=self.ticketreason)
        await interaction.edit_original_response(content=f'**_Done! -> <#{cid}>_**')
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            await interaction.response.send_message(f'**_Oops! Something went wrong._**', ephemeral=True)
        except:
            await interaction.edit_original_response(content='**_Oops! Something went wrong._**')
        print(error)

class OpenView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
            @discord.ui.button(label="APPLY FOR PARTNER", emoji="🤝", style=discord.ButtonStyle.blurple,custom_id="partner_button")
            async def partner_button(self, interaction: discord.Interaction, button: discord.Button):
                # Check for existing tickets
                category = interaction.guild.get_channel(TICKET_CTGRY_ID)
                try:
                    user_tickets = [channel for channel in category.text_channels if str(interaction.user.id) in channel.topic]
                except:
                    user_tickets = []
                if len(user_tickets) >= 2:
                    await interaction.response.send_message("You already have 2 open tickets. Please close an existing ticket before opening a new one.", ephemeral=True)
                else:
                    await interaction.response.send_modal(PartnerInfo())
            @discord.ui.button(label="OPEN A SUPPORT TICKET", emoji="🎫", style=discord.ButtonStyle.gray, custom_id="ticket_button")
            async def ticket_button(self, interaction: discord.Interaction, button: discord.Button):
                # Check for existing tickets
                category = interaction.guild.get_channel(TICKET_CTGRY_ID)
                try:
                    user_tickets = [channel for channel in category.text_channels if str(interaction.user.id) in channel.topic]
                except:
                    user_tickets = []
                if len(user_tickets) >= 2:
                    await interaction.response.send_message("You already have 2 open tickets. Please close an existing ticket before opening a new one.", ephemeral=True)
                else:
                    await interaction.response.send_modal(TicketInfo())


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
async def ticketmsg(interaction:discord.Interaction, channel: discord.TextChannel):
    if interaction.user.guild_permissions.administrator or interaction.user.id == 971316880243576862:
        em = discord.Embed(description=f'Do NOT open a ticket to "see what it does" or for matters that do not concern us\nWe **will** punish you for opening a ticket for an invalid reason', title=":sos: Event Alerts Support",color=discord.Color.red())
        em.add_field(name=":handshake: Applying for Partner",value="Please read all of the requirements and necessary information **[HERE](https://discord.com/channels/970411885293895801/970415677393477734/1179203344917614662)**\nOnce you're ready, you can click the ``APPLY FOR PARTNER`` button below!")
        em.add_field(name=":ticket: General server support",value="If you have any other questions about the server, feel free to create a ticket to ask us\nJust click the ``OPEN A SUPPORT TICKET`` button below to get started!")
        view = OpenView()
        await channel.send(embed=em,view=view)
        await interaction.response.send_message("**Done!**",ephemeral=True)
    else:
        await interaction.response.send_message("No permission!",ephemeral=True)
@app_commands.command(description="Close the current ticket")
@app_commands.describe(time="Time until closure (e.g., 10s, 5m, 1h, 7d). Default: 10 seconds")
async def close(interaction: discord.Interaction, time: str = None):
    if "TICKET" not in interaction.channel.topic:
        await interaction.response.send_message(embed=discord.Embed(description="This command can only be used in ticket channels.", color=discord.Color.red()), ephemeral=True)
        return

    seconds = parse_time(time)

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
            await close_ticket(interaction.channel)
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
        except:
            pass
        await interaction.followup.send(f"Successfully changed the ticket priority to {priority.name}!", ephemeral=True)
    else:
        await interaction.followup.send("Sorry, this command is only for staff!",ephemeral=True)

### ADDING COMMANDS
tree.add_command(ticketmsg)
tree.add_command(close)
tree.add_command(priority)

### RUNNING
client.run(TOKEN)