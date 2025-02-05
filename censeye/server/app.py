from flask import Flask

from . import HAS_SERVER

app = None

if HAS_SERVER:
    app = Flask(__name__)
