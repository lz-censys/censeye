import os

import click

from .app import init_server


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-l", "--listen", default="127.0.0.1:5000", help="listen host:port")
@click.option("-u", "--upload-path", default="/tmp/.ceyes", help="upload path")
@click.option("-r", "--root", default="/", help="root path")
def server(listen, upload_path, root):
    host, port = listen.split(":")

    os.makedirs(upload_path, exist_ok=True)
    app = init_server(upload_path=upload_path, application_root=root)

    print(f"Starting server on {host}:{port}")
    for rule in app.url_map.iter_rules():
        print(f" * {rule}")
    app.run(host=host, port=int(port))


if __name__ == "__main__":
    server()
