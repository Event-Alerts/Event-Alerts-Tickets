
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
import os
import sys
import requests
from bs4 import BeautifulSoup
import html
import re
import mimetypes
import io
import json

# UTILITIES.PY
def format_url(invite_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    if invite_url.startswith("https://discord.com/") or invite_url.startswith("http://discord.com/") or invite_url.startswith("https://discord.gg/") or invite_url.startswith("http://discord.gg/"):
        response = requests.get(invite_url, headers=headers)
    elif invite_url.startswith("discord.com/") or invite_url.startswith("discord.gg/"):
        response = requests.get(f"https://{invite_url}", headers=headers)
        invite_url = f"https://{invite_url}"
    elif invite_url.startswith(".gg/"):
        response = requests.get(
            f"https://discord{invite_url}", headers=headers)
        invite_url = f"https://discord{invite_url}"
    elif invite_url.startswith("gg/"):
        response = requests.get(
            f"https://discord.{invite_url}", headers=headers)
        invite_url = f"https://discord.{invite_url}"
    else:
        response = requests.get(
            f"https://discord.gg/{invite_url}", headers=headers)
        invite_url = f"https://discord.gg/{invite_url}"
    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return None, invite_url

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract member count from the HTML
    member_count_element = soup.find('meta', property='og:description')
    if member_count_element:
        description = member_count_element['content']
        member_count = extract_member_count(description)
        return member_count, invite_url
    else:
        print("Member count element not found in the page.")
        return None, invite_url


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


def parse_time(time_str):
    if not time_str:
        return 10  # Default to 10 seconds

    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.match(r"(\d+)([smhd])?$", time_str.lower())

    if not match:
        return 10  # Default to 10 seconds if invalid format

    value, unit = match.groups()
    return int(value) * units.get(unit, 1)


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


def get_config(key=None):
    cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
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
        MUTED_ROLE_ID = int(config["MUTED_ROLE_ID"])
    if key == None:
        return TOKEN, SERVER_ID, STORAGE_SERVER_ID, STORAGE_CHANNEL_ID, MOD_ROLE_ID, TRANSCRIPT_CHNL_ID, TICKET_CTGRY_ID, PING_ROLE, LOG_CHNL_ID, MUTED_ROLE_ID
    else:
        return config[key]


async def create_partner_ticket(client: discord.Client, username: str, servername: str, memberid: int, invite: str, reason: str) -> str:
    TOKEN, SERVER_ID, STORAGE_SERVER_ID, STORAGE_CHANNEL_ID, MOD_ROLE_ID, TRANSCRIPT_CHNL_ID, TICKET_CTGRY_ID, PING_ROLE, LOG_CHNL_ID, MUTED_ROLE_ID = get_config()

    guild = await client.fetch_guild(SERVER_ID)
    category: discord.CategoryChannel = await client.fetch_channel(TICKET_CTGRY_ID)
    done_user = username.lower().replace(" ", "-")
    channel = await category.create_text_channel(name=f"🟡p-{done_user}")
    
    await channel.edit(topic=f"TICKET-{str(memberid)}")
    # Set up permissions
    await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)

    # Allow the ticket creator to see and write in the channel
    member = await guild.fetch_member(memberid)
    await channel.set_permissions(member, read_messages=True, send_messages=True)


    # Allow the bot too
    await channel.set_permissions(await guild.fetch_member(client.user.id), read_messages=True, send_messages=True)
    # Dont Allow muted role to use / cmds
    await channel.set_permissions(guild.get_role(MUTED_ROLE_ID), use_application_commands=False, use_embedded_activities=False, use_external_apps=False)

    # Allow users with the mod role to see and write in the channel
    mod_role = guild.get_role(MOD_ROLE_ID)


    await channel.set_permissions(mod_role, read_messages=True, send_messages=True)


    em = discord.Embed(title=f"Partner Application",
                       description=f"{reason}", color=discord.Color.yellow())
    em.add_field(name=servername, value=invite)
    em.set_footer(text="EVENT ALERTS | TICKETS",
                  icon_url="https://cdn.discordapp.com/avatars/1142603508827299883/8115d0ff74451c2450da1f58733cf22d.png")
    from CloseTicket import CloseTicket
    await channel.send(content=f"||<@{str(memberid)}> <@&{str(PING_ROLE)}>|| {invite}", embed=em, view=CloseTicket())
    return str(channel.id)


async def close_ticket(client, channel, user):
    TOKEN, SERVER_ID, STORAGE_SERVER_ID, STORAGE_CHANNEL_ID, MOD_ROLE_ID, TRANSCRIPT_CHNL_ID, TICKET_CTGRY_ID, PING_ROLE, LOG_CHNL_ID, MUTED_ROLE_ID = get_config()
    storage_guild = await client.fetch_guild(STORAGE_SERVER_ID)
    storage_channel = await storage_guild.fetch_channel(STORAGE_CHANNEL_ID)
    voicechannels = channel.topic.split('-')[2:]
    for vc in voicechannels:
        vchannel = await client.fetch_channel(int(vc))
        await vchannel.delete()
    print(voicechannels)
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

#    markdown_file = discord.File(io.StringIO(
#        markdown_transcript), filename=f"{channel.name}_transcript.md")
    html_file = discord.File(io.StringIO(
        html_transcript), filename=f"{channel.name}_transcript.html")

    storage_message = await storage_channel.send(file=html_file)
    transcript_channel = channel.guild.get_channel(TRANSCRIPT_CHNL_ID)
    url = storage_message.attachments[0].url
    x = await transcript_channel.send(embed=discord.Embed(description=f"Transcript for {channel.name}\n[Transcript]({url})", color=discord.Color.blue()))
    log_channel = client.get_channel(LOG_CHNL_ID)
    em = discord.Embed(title="TICKET CLOSED", color=discord.Color.red(), description=f"<@{str(user.id)}> Just closed a ticket opened by: <@{str(channel.topic.split('-')[1])}> (Transcript: https://discord.com/channels/{x.guild.id}/{x.channel.id}/{x.id})")
    await log_channel.send(embed=em)
    # Close the ticket
    await channel.delete()


async def create_ticket(client: discord.Client, username: str, memberid: int, reason: str) -> str:
    TOKEN, SERVER_ID, STORAGE_SERVER_ID, STORAGE_CHANNEL_ID, MOD_ROLE_ID, TRANSCRIPT_CHNL_ID, TICKET_CTGRY_ID, PING_ROLE, LOG_CHNL_ID, MUTED_ROLE_ID = get_config()
    guild = await client.fetch_guild(SERVER_ID)
    category: discord.CategoryChannel = await client.fetch_channel(TICKET_CTGRY_ID)
    done_user = username.lower().replace(" ", "-")
    channel = await category.create_text_channel(name=f"🟡t-{done_user}")
    await channel.edit(topic=f"TICKET-{str(memberid)}")
    # Set up permissions
    await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
    # Allow the ticket creator to see and write in the channel
    member = await guild.fetch_member(memberid)
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    # Allow the bot too
    await channel.set_permissions(await guild.fetch_member(client.user.id), read_messages=True, send_messages=True)
    # Dont Allow muted role to use / cmds
    await channel.set_permissions(guild.get_role(MUTED_ROLE_ID), use_application_commands=False, use_embedded_activities=False, use_external_apps=False)
    # Allow users with the mod role to see and write in the channel
    mod_role = guild.get_role(MOD_ROLE_ID)
    await channel.set_permissions(mod_role, read_messages=True, send_messages=True)
    em = discord.Embed(
        title=f"Ticket - {username}", description=f"Hello {username}! Your ticket has been created!\n\n**__Information:__**\n**Ticket Reason:** ``{reason}``", color=discord.Color.yellow())
    em.set_footer(text="EVENT ALERTS | TICKETS",
                  icon_url="https://cdn.discordapp.com/avatars/1142603508827299883/8115d0ff74451c2450da1f58733cf22d.png")
    from CloseTicket import CloseTicket
    await channel.send(content=f"||<@{str(memberid)}> <@&{str(PING_ROLE)}>||", embed=em, view=CloseTicket())
    log_channel = client.get_channel(LOG_CHNL_ID)
    em = discord.Embed(title="TICKET OPENED", color=discord.Color.green(), description=f"<@{str(memberid)}> Just opened a ticket!\n<#{str(channel.id)}>")
    await log_channel.send(embed=em)
    return str(channel.id)
