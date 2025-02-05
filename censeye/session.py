import json
import jsonpickle

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

    def load(self, input):
        try:
            sess = json.load(input)
        except json.JSONDecodeError:
            raise ValueError("Invalid session file")

        jconf = json.dumps(sess.get("conf", {}))
        rconf = jsonpickle.decode(jconf)

        if not isinstance(rconf, Config):
            raise ValueError("Invalid config object in session file")

        self.conf = rconf
        self.args = sess.get("args", {})
        self.results = sess.get("results", [])
        self.searches = sess.get("searches", [])

    def load_file(self, path):
        with open(path, "r") as f:
            self.load(f)

    def save(self, output):
        sess = {
            "conf": json.loads(jsonpickle.encode(self.conf)),
            "args": self.args,
            "results": self.results,
            "searches": self.searches,
        }
        json.dump(sess, output)
