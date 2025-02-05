import os
import io
import uuid
import json

from flask import request, Response
from rich.console import Console

import rich.terminal_theme

from .app import app
from ..session import Session
from ..cli import CenseyeRunner

HTML_FORMAT = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{stylesheet}
body {{
    color: {foreground};
    background-color: {background};
    a:link {{
        color: #578fa4; 
        background-color: {background};
        text-decoration: none;
    }}
    a:visited {{
        color: {foreground};
        background-color: {background};
        text-decoration: none;
    }}
}}
</style>
</head>
<body>
    <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><code style="font-family:inherit">{code}</code></pre>
</body>
</html>
"""



@app.route("/upload", methods=["POST"])
def upload():
    if not request.is_json:
        return "invalid input", 400

    payload = request.json
    print(payload)

    try:
        Session().load(io.BytesIO(request.data))
    except ValueError as e:
        return f"not a valid session {e}", 400

    uid = uuid.uuid4().hex

    with open(f'{app.config["UPLOAD_PATH"]}/{uid}', "w") as f:
        f.write(json.dumps(payload))

    return {"id": uid}, 200


@app.route("/view/<uid>/raw", methods=["GET"])
def view_raw(uid):
    try:
        with open(f'{app.config["UPLOAD_PATH"]}/{uid}', "r") as f:
            return f.read(), 200
    except FileNotFoundError:
        return "not found", 404


@app.route("/view/<uid>", methods=["GET"])
def view(uid):
    format = request.args.get("format", "html")
    theme = rich.terminal_theme.DIMMED_MONOKAI

    console = Console(record=True, file=open(os.devnull, "w"), soft_wrap=True)
    session = Session()

    try:
        session.load_file(f'{app.config["UPLOAD_PATH"]}/{uid}')
    except FileNotFoundError:
        return "session not found", 404
    except Exception as e:
        return f"unknown error: {e}", 500

    try:
        CenseyeRunner(
            session.args.get("ip", None),
            console=console,
            config=session.conf,
            depth=session.args.get("depth", 0),
            at_time=session.args.get("at_time", None),
            query_prefix=session.args.get("query_prefix", None),
        ).report(session.results, session.searches)
    except Exception as e:
        return str(e), 500

    if format in ("text", "txt"):
        return (
            Response(console.export_text(), content_type="text/plain; charset=utf-8"),
            200,
        )
    elif format == "svg":
        return console.export_svg(), 200

    return console.export_html(theme=theme, code_format=HTML_FORMAT), 200
