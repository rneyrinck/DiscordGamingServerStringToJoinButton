import discord
import re
import os
from dotenv import load_dotenv
import a2s
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

# Keeps track of which bot reply belongs to which user message
BOT_REPLIES: dict[int, discord.Message] = {}


def get_server_info(server):
    try:
        host, port = server.rsplit(":", 1)
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
        self.add_item(
            discord.ui.Button(
                label="Join Server",
                url=url
            )
        )


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


async def process_message(message):

    server = None
    password = None

    # -------------------------
    # Detect connect string
    # -------------------------

    match = re.search(CONNECT_REGEX, message.content)

    if match:
        server = match.group(1)
        password = match.group(2)

    else:

        ip_match = re.search(IP_PORT_REGEX, message.content)

        if ip_match:
            server = ip_match.group(1)

        else:

            host_match = re.search(HOST_PORT_REGEX, message.content)

            if host_match:
                server = host_match.group(1)

    # -------------------------
    # Nothing detected
    # -------------------------

    if not server:

        if message.id in BOT_REPLIES:

            try:
                await BOT_REPLIES[message.id].delete()
            except Exception:
                pass

            BOT_REPLIES.pop(message.id, None)

        return

    # -------------------------
    # Build Join URL
    # -------------------------

    if password:
        url = f"{BASE_URL}/{server}?pw={password}"
    else:
        url = f"{BASE_URL}/{server}"

    # -------------------------
    # Query Server
    # -------------------------

    info = get_server_info(server)

    if info:

        description = (
            f"**{info['name']}**\n"
            f"Map: `{info['map']}`\n"
            f"Players: `{info['players']} / {info['max_players']}`"
        )

        color = 0x2ecc71

    else:

        description = (
            "⚠️ **Couldn't query the server.**\n\n"
            "The server may:\n"
            "• Be starting up\n"
            "• Be offline\n"
            "• Be blocking A2S queries\n"
            "• Be temporarily unreachable\n\n"
            f"You can still try joining:\n`{server}`"
        )

        color = 0xf39c12

    embed = discord.Embed(
        title="🎮 Counter-Strike Server",
        description=description,
        color=color
    )

    embed.set_footer(
        text="Powered by CS2 Join Bot"
    )

    view = JoinView(url)

    # -------------------------
    # Update existing reply
    # -------------------------

    if message.id in BOT_REPLIES:

        try:

            await BOT_REPLIES[message.id].edit(
                embed=embed,
                view=view
            )

            return

        except discord.NotFound:
            BOT_REPLIES.pop(message.id, None)

    # -------------------------
    # Create new reply
    # -------------------------

    reply = await message.reply(
        embed=embed,
        view=view
    )

    BOT_REPLIES[message.id] = reply


@client.event
async def on_message(message):

    if message.author.bot:
        return

    await process_message(message)


@client.event
async def on_message_edit(before, after):

    if after.author.bot:
        return

    if before.content == after.content:
        return

    await process_message(after)


@client.event
async def on_message_delete(message):

    if message.id not in BOT_REPLIES:
        return

    try:
        await BOT_REPLIES[message.id].delete()
    except Exception:
        pass

    BOT_REPLIES.pop(message.id, None)


client.run(TOKEN)