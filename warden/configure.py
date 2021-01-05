import argparse
import json
import logging
from collections import namedtuple
from pprint import pprint
from typing import Dict

from warden import HOSTS_FILE, configure_root_logger

AddHost = namedtuple("AddHost", "name host user threshold disks")
RemoveHost = namedtuple("RemoveHost", "name")
EditHost = namedtuple("EditHost", "name host user threshold disks")
GetHost = namedtuple("GetHost", "name")

EditConfig = namedtuple("EditConfig", "key value")
GetConfig = namedtuple("GetConfig", "key")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Warden configuration helper")
    subparsers = parser.add_subparsers(help="sub-commands", dest="subcommand", required=True)

    # add-host subparser
    add_host_parser = subparsers.add_parser("add-host", help="Add a host to configuration file")
    add_host_parser.add_argument("name", help="Host name to add.")
    add_host_parser.add_argument("host", help="Address/hostname of the host.")
    add_host_parser.add_argument("user", help="User of host.")
    add_host_parser.add_argument("threshold", help="Disk threshold to check against.")
    add_host_parser.add_argument("disks", nargs="+", help="Name of disks will be checked, can be '/dev/X' or 'X' format")

    # remove-host subparser
    remove_host_parser = subparsers.add_parser("remove-host", help="Remove a host from configuration file")
    remove_host_parser.add_argument("name", help="Name of the host to remove from config")

    # get-host subparser
    get_host_parser = subparsers.add_parser("get-host", help="Get a host from configuration file")
    get_host_parser.add_argument("name", help="Name of the host to get from config")

    # edit-host subparser
    edit_host_parser = subparsers.add_parser("edit-host", help="Edit a host")
    edit_host_parser.add_argument("name", help="Name of the host to edit")
    edit_host_parser.add_argument("--host", required=False, help="New host address")
    edit_host_parser.add_argument("--user", required=False, help="New username")
    edit_host_parser.add_argument("--threshold", required=False, help="New threshold value")
    edit_host_parser.add_argument("--disks", required=False, nargs="+", help="Set disks")

    # set-conf
    set_conf_parser = subparsers.add_parser("set-conf", help="Set a config parameter")
    set_conf_parser.add_argument("key", help="Key to set in config")
    set_conf_parser.add_argument("value", help="Value to set in config", default=None)

    # get-conf
    get_conf_parser = subparsers.add_parser("get-conf", help="Get a config parameter")
    get_conf_parser.add_argument("key", help="Key of config to get")

    return parser.parse_args()

# helpers
####################
def get_hosts() -> Dict:
    with open(HOSTS_FILE, "r") as f:
        return json.load(f)


def set_hosts(hosts: Dict):
    with open(HOSTS_FILE, "w") as f:
        json.dump(hosts, f, indent=4)


def find_host(hosts: Dict, name: str):
    for host in hosts:
        if host["name"] == name:
            return host
    return None
#######################


# actions
#######################
def add_host(hosts: Dict, action: AddHost):
    logger = logging.getLogger("add-host")
    new_host = {"name":  action.name, "host": action.host, "user": action.user, "disks": action.disks, "threshold": action.threshold}
    logger.info("Adding a new host. {}".format(str(new_host)))
    hosts["hosts"].append(new_host)
    logger.info("Host '{}' added".format(action.name))


def remove_host(hosts: Dict, action: RemoveHost):
    host = find_host(hosts["hosts"], action.name)
    if host:
        try:
            hosts["hosts"].remove(host)
        except ValueError:
            print("Failed to remove", action.name)
    else:
        print("No such host:", action.name)


def get_host(hosts: Dict, action: GetHost):
    host = find_host(hosts["hosts"], action.name)
    if host:
        pprint(host)


def edit_host(hosts: Dict, action: EditHost):
    pass


def get_conf(hosts: Dict, action: GetConfig):
    pass


def set_conf(hosts: Dict, action: EditConfig):
    pass
#########################


def configure():
    # entrypoint for configure
    configure_root_logger()
    logger = logging.getLogger("configure")
    try:
        args = parse_args()
        hosts = get_hosts()
        set_hosts(hosts)
        if args.subcommand == "add-host":
            add_host(hosts, AddHost(name=args.name, host=args.host, user=args.user, threshold=args.threshold, disks=args.disks))
        elif args.subcommand == "remove-host":
            remove_host(hosts, RemoveHost(name=args.name))
        elif args.subcommand == "get-host":
            get_host(hosts, GetHost(name=args.name))

        set_hosts(hosts)
    except Exception:
        logger.exception("Exception raised")
        raise


if __name__ == "__main__":
    configure()