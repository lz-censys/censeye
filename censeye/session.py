import json
import requests

from dataclasses import dataclass
from .config import Config


@dataclass
class Arguments:
    ip: str
    depth: int
    max_search_results: int
    pivot_threshold: int
    at_time: str
    query_prefix: str
    min_pivot_weight: float


@dataclass
class Session:
    conf: Config
    args: dict
    results: list
    searches: list

    def __init__(self, conf=None, args=None, results=None, searches=None):
        self.conf = conf or Config()
        self.args = args or {}
        self.results = results or []
        self.searches = searches or []
        self.server = None

    def _fetch_session(self, server, id):
        if not server.startswith("http") and not server.startswith("https"):
            server = f"http://{server}"

        url = f"{server}/view/{id}/raw"
        rsp = requests.get(url)

        if rsp.status_code != 200:
            raise ValueError(f"failed to fetch session {id}: {rsp.text}")

        return json.loads(rsp.text)

    def load(self, input, server=None):
        sess = None

        if server:
            sess = self._fetch_session(server, input)
        else:
            try:
                sess = json.load(input)
            except json.JSONDecodeError:
                raise ValueError("Invalid session file")

        jconf = sess.get("conf", {})
        rconf = Config.from_dict(jconf)

        if not isinstance(rconf, Config):
            raise ValueError("Invalid config object in session file")

        self.conf = rconf
        self.args = sess.get("args", {})
        self.results = sess.get("results", [])
        self.searches = sess.get("searches", [])

    def load_file(self, path):
        with open(path, "r") as f:
            self.load(f)

    def _create_session(self):
        return {
            "conf": self.conf.to_dict(),
            "args": self.args,
            "results": self.results,
            "searches": self.searches,
        }

    def save(self, output):
        json.dump(self._create_session(), output)

    def upload(self, server):
        if not server.startswith("http") and not server.startswith("https"):
            server = f"http://{server}"

        url = f"{server}/upload"
        rsp = requests.post(url, json=self._create_session())

        if rsp.status_code != 200:
            raise ValueError(f"failed to upload session: {rsp.text}")

        return rsp.text
