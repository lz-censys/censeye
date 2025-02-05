try:
    from flask import Flask

    HAS_SERVER = True
except ImportError:
    HAS_SERVER = False
