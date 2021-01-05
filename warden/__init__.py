import logging
import os
import json

from dataclasses import dataclass
from collections import namedtuple
from logging.handlers import RotatingFileHandler
from typing import List, Any

PATH = os.path.split(os.path.abspath(__file__))[0]
HOSTS_FILE = os.path.join(PATH, "etc", "hosts.json")

CONFIG_FILE = os.path.join(PATH, "etc", "config.json")
with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)

LOG_PATH = os.path.join(PATH, "etc", "warden.log")

DiskUsage = namedtuple("DiskUsage", "name usage")


@dataclass
class Host:
    name: str
    host: str
    user: str
    disks: List[str]
    threshold: int

    @staticmethod
    def parse_from(conf: dict):
        return Host(name=conf["name"], user=conf["user"], host=conf["host"], disks=conf["disks"],
                    threshold=conf["threshold"])


@dataclass
class Notification:
    host: str
    threshold: int
    disks: List[DiskUsage]

    @staticmethod
    def from_disk(host: Host, disks: List[DiskUsage]):
        return Notification(host=host.name, threshold=host.threshold, disks=disks)


with open(HOSTS_FILE) as f:
    HOSTS = [Host.parse_from(c) for c in json.load(f)["hosts"]]


def get_config(key: str):
    conf = CONFIG
    try:
        for subkey in key.split("."):
            conf = conf[subkey]
        return conf
    except Exception:
        return None


def set_config(key: str, value: Any):
    conf = CONFIG
    try:
        for subkey in key.split(".")[:1]:
            conf = conf[subkey]
        last_key = key.split(".")[-1]
        assert type(conf[last_key]) == type(value), "Cannot assign '{}' to '{}'".format(repr(type(conf[last_key])), repr(type(value)))
        conf[last_key] = value
        return True
    except AssertionError:
        raise
    except Exception:
        return False


def configure_root_logger():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = []
    file_formatter = logging.Formatter("[%(asctime)s] | %(name)-15s | %(levelname)-8s %(message)s")
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5000)
    file_handler.setFormatter(file_formatter)
    root.addHandler(file_handler)
