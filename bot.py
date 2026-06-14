import discord
import re
import os
from dotenv import load_dotenv
import a2s
import socket
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost:5000"
)
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

CONNECT_REGEX = r"connect\s+([^\s;]+)(?:;\s*password\s+(\S+))?"

IP_PORT_REGEX = r"\b((?:\d{1,3}\.){3}\d{1,3}:\d{2,5})\b"

HOST_PORT_REGEX = r"\b([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:\d{2,5})\b"

def get_server_info(server):

    try:
        host, port = server.split(":")
        address = (host, int(port))

        info = a2s.info(address)
        players = a2s.players(address)

        return {
            "name": info.server_name,
            "map": info.map_name,
            "players": len(players),
            "max_players": info.max_players
        }

    except Exception:
        return None

class JoinView(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        self.add_item(discord.ui.Button(label="Join Server", url=url))


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):

    if message.author.bot:
        return

    # Only allow messages from voice channel chats
    if message.channel.type not in [discord.ChannelType.voice]:
        return
    
    server = None
    password = None

    # FIRST: detect full connect command
    match = re.search(CONNECT_REGEX, message.content)

    if match:
        server = match.group(1)
        password = match.group(2)

    else:
        # SECOND: detect raw IP:PORT
        ip_match = re.search(IP_PORT_REGEX, message.content)

        if ip_match:
            server = ip_match.group(1)
        else:
            # THIRD: detect hostname:PORT
            host_match = re.search(HOST_PORT_REGEX, message.content)

            if host_match:
                server = host_match.group(1)
    # If nothing detected, exit
    if not server:
        return

    # Build join URL
    if password:
        url = f"{BASE_URL}/{server}?pw={password}"
    else:
        url = f"{BASE_URL}/{server}"

    # Query server info
    info = get_server_info(server)

    if info:
        description = (
            f"**{info['name']}**\n"
            f"Map: `{info['map']}`\n"
            f"Players: `{info['players']} / {info['max_players']}`"
        )
    else:
        description = f"Server: `{server}`"

    embed = discord.Embed(
        title="🎮 Counter-Strike Server",
        description=description,
        color=0x2ecc71
    )

    await message.reply(embed=embed, view=JoinView(url))

client.run(TOKEN)