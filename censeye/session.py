import json
import logging
from dataclasses import dataclass

import requests
from requests.auth import HTTPBasicAuth

from .config import Config
from .const import USER_AGENT

DEFAULT_UPLOAD_PATH = "/upload"
DEFAULT_VIEW_PATH = "/view/{id}"

requests.utils.default_user_agent = lambda: USER_AGENT


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
        self.username = None
        self.password = None
        self.auth = None

        if conf and conf.session_server:
            if conf.session_server.username and conf.session_server.password:
                self.username = conf.session_server.username
                self.password = conf.session_server.password
                self.auth = HTTPBasicAuth(self.username, self.password)
            self.server = conf.session_server.server

    def view_url(self, id, path=DEFAULT_VIEW_PATH):
        return f"{self.server}{path.format(id=id)}"

    def _fetch_session(self, id, path=DEFAULT_VIEW_PATH):
        url = f"{self.server}{path.format(id=id)}/raw"
        rsp = requests.get(url, auth=self.auth)

        if rsp.status_code != 200:
            raise ValueError(f"failed to fetch session {id}: {rsp.text}")

        return json.loads(rsp.text)

    """
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
    """

    def load(self, input):
        if isinstance(input, str):
            sess = self._fetch_session(input)
        else:
            sess = json.load(input)

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

    def upload(self, path=DEFAULT_UPLOAD_PATH):
        url = f"{self.server}{path}"
        rsp = requests.post(url, json=self._create_session(), auth=self.auth)

        logging.debug(f"upload response: {rsp.text}")

        if rsp.status_code != 200:
            raise ValueError(f"failed to upload session: {rsp.text}")

        return rsp.json().get("id", None)
