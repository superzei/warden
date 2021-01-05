import logging
import os
import json

from dataclasses import dataclass
from collections import namedtuple
from logging.handlers import RotatingFileHandler
from typing import List

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
    disks: List[DiskUsage]

    @staticmethod
    def from_disk(host: Host, disks: List[DiskUsage]):
        return Notification(host=host.name, disks=disks)


with open(HOSTS_FILE) as f:
    HOSTS = [Host.parse_from(c) for c in json.load(f)["hosts"]]


def configure_root_logger():
    root = logging.getLogger()
    root.handlers = []
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5000)
    root.addHandler(file_handler)
