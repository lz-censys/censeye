import click
import os
import logging

from . import HAS_SERVER
from .app import app
from .routes import *


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-l", "--listen", default="127.0.0.1:5000", help="listen host:port")
@click.option("-u", "--upload-path", default="/tmp/.ceyes", help="upload path")
def server(listen, upload_path):
    host, port = listen.split(":")

    os.makedirs(upload_path, exist_ok=True)
    app.config["UPLOAD_PATH"] = upload_path

    print(f"Starting server on {host}:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    if HAS_SERVER:
        server()
    else:
        logging.error(
            "Flask is not installed. Please install it with 'pip install flask'"
        )
