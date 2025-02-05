import json
import logging
from dataclasses import dataclass

import requests

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

    def _fetch_session(self, server, id, path="/view/{id}/raw"):
        if not server.startswith("http") and not server.startswith("https"):
            server = f"http://{server}"

        url = f"{server}{path.format(id=id)}"
        rsp = requests.get(url)

        if rsp.status_code != 200:
            raise ValueError(f"failed to fetch session {id}: {rsp.text}")

        return json.loads(rsp.text)

    def load_from_url(self, url):
        rsp = requests.get(url)
        if rsp.status_code != 200:
            raise ValueError(f"failed to fetch session {url}: {rsp.text}")

        try:
            sess = json.loads(rsp.text)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid session file: {rsp.text}")

        jconf = sess.get("conf", {})
        rconf = Config.from_dict(jconf)

        if not isinstance(rconf, Config):
            raise ValueError("Invalid config object in session file")

        self.conf = rconf
        self.args = sess.get("args", {})
        self.results = sess.get("results", [])
        self.searches = sess.get("searches", [])

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
        with open(path) as f:
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

    def upload(self, server, path="/upload"):
        if not server.startswith("http") and not server.startswith("https"):
            server = f"https://{server}"

        url = f"{server}{path}"
        rsp = requests.post(url, json=self._create_session())

        logging.debug(f"upload response: {rsp.text}")

        if rsp.status_code != 200:
            raise ValueError(f"failed to upload session: {rsp.text}")

        return rsp.json().get("id", None)
