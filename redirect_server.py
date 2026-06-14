from flask import Flask, request
import urllib.parse
import socket
import a2s

app = Flask(__name__)
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

@app.route("/<path:server>")
def connect(server):
    
    # get password if present
    password = request.args.get("pw")

    # decode URL characters
    server = urllib.parse.unquote(server)

    # split host and port
    try:
        host, port = server.split(":")
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
    <html>
    <head>
    <title>Joining CS2 Server</title>
    </head>

    <body style="font-family:sans-serif;text-align:center;padding-top:40px;">

    <h1>🎮 Joining Counter-Strike Server</h1>

    {server_display}

    <p>Launching game...</p>

    <script>
    window.location.href="{steam_url}";
    </script>

    <p>If the game doesn't open automatically:</p>
    <a href="{steam_url}" style="font-size:20px;">Click Here to Join</a>

    </body>
    </html>
    """


@app.route("/", methods=["GET", "POST"])
def home():
    return "CS2 Connect Service Running"


if __name__ == "__main__":
    app.run(port=5000)