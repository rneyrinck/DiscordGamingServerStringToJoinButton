from flask import Flask, request, send_from_directory
import urllib.parse
import socket
import a2s
import os

app = Flask(__name__, static_folder="static")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        app.static_folder,
        "CS2_join_bot_icon.png",
        mimetype="image/vnd.microsoft.icon"
    )

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

    except Exception as e:
        print(f"Query failed: {e}")
        return None

@app.route("/<path:server>")
def connect(server):
    
    # get password if present
    password = request.args.get("pw")

    # decode URL characters
    server = urllib.parse.unquote(server)

    # split host and port
    try:
        host, port = server.rsplit(":", 1)
    except ValueError:
        return "Invalid server format. Expected host:port"

    # resolve hostname to IP
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        # fallback if DNS fails
        ip = host

    server_ip = f"{ip}:{port}"
    info = get_server_info(server_ip)
    if info:
        server_display = f"""
            <h2>{info['name']}</h2>
            <p>Map: {info['map']}</p>
            <p>Players: {info['players']} / {info['max_players']}</p>
        """
    else:
        server_display = f"<p>Server: {server_ip}</p>"
    # build steam connect URI
    if password:
        steam_url = f"steam://connect/{server_ip}/{password}"
    else:
        steam_url = f"steam://connect/{server_ip}"

    print(f"Launching: {steam_url}")

    # return HTML launcher page (browsers allow this)
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>Joining CS2 Server...</title>

    <link rel="icon" href="/favicon.ico">

    <style>
    body {{
        margin:0;
        background:#111827;
        color:#f3f4f6;
        font-family:Arial, Helvetica, sans-serif;
        text-align:center;
    }}

    .container {{
        max-width:600px;
        margin:60px auto;
        padding:32px;
        background:#1f2937;
        border-radius:16px;
        box-shadow:0 10px 30px rgba(0,0,0,.35);
    }}

    .profile {{
        width:80px;
        height:80px;
        border-radius:50%;
        margin-top:30px;
        border:3px solid #5865F2;
    }}

    .join-button {{
        display:inline-block;
        margin-top:18px;
        padding:14px 26px;
        background:#5865F2;
        color:white;
        text-decoration:none;
        border-radius:10px;
        font-weight:bold;
        transition:.2s;
    }}

    .join-button:hover {{
        background:#4752C4;
    }}

    .steam-button {{
        display:inline-block;
        margin-top:18px;
        padding:14px 26px;
        background:#16a34a;
        color:white;
        text-decoration:none;
        border-radius:10px;
        font-weight:bold;
    }}

    .footer {{
        margin-top:35px;
        color:#9ca3af;
        font-size:14px;
    }}
    </style>

    <script>
    setTimeout(function(){{
        window.location.href="{steam_url}";
    }}, 500);
    </script>

    </head>

    <body>

    <div class="container">

    <h1>🎮 Joining Counter-Strike 2 Server</h1>

    {server_display}

    <p>Launching Counter-Strike...</p>

    <a class="steam-button" href="{steam_url}">
    Launch Manually
    </a>

    <hr style="margin:40px 0;border:none;border-top:1px solid #374151;">
    
    <a href="https://discord.gg/5UdvRPSVg" target="_blank">
    <img class="profile" src="/static/JebusFace.png">
    </a>
    
    <h3>Built by Robert Neyrinck(JebusKrispy)</h3>

    <p>
    Have an idea, found a bug, or want to request a feature?
    </p>

    <a
    class="join-button"
    href="https://discord.gg/5UdvRPSVg"
    target="_blank">
    💬 Join the JebusKrispy Community
    </a>

    <p style="margin-top:25px;font-size:14px;">
⭐ <a
    href="https://github.com/rneyrinck/DiscordGamingServerStringToJoinButton"
    target="_blank"
    style="color:#60A5FA;">
    View on GitHub
    </a>
    </p>
    
    <div class="footer">
    Thanks for using CS2 Join Bot ❤️
    </div>

    </div>

    </body>
    </html>
    """


@app.route("/", methods=["GET", "POST"])
def home():
    return "CS2 Connect Service Running"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )