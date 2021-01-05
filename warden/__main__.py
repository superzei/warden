from typing import List
from fabric import Connection

import re
from warden import HOSTS, Notification, Host, DiskUsage, configure_root_logger


def notify(notifiations: List[Notification]):
    if len(notifiations) <= 0:
        print("No notifications")
        return


def parse_line(line: str) -> DiskUsage:
    name = line.split()[0]
    usage = re.findall(r'(\w+)%', line)
    usage = int(usage[0]) if len(usage) > 0 else 0
    return DiskUsage(name=name, usage=usage)


def get_disks(host: Host, df: str) -> List[DiskUsage]:
    usages = []
    for disk in df.splitlines()[1:]:
        usage = parse_line(disk)
        if (usage.name in host.disks or usage.name.replace("/dev/", "") in host.disks) \
                and usage.usage >= host.threshold:
            usages.append(usage)
    return usages


def check(hosts: List[Host]) -> List[Notification]:
    # check all hosts and disks
    notifications = []
    for host in hosts:
        try:
            con = Connection(host=host.host, user=host.user)
            result = con.run("df -h", hide=True)
        except Exception as e:
            print("Unable to run commands on {}: {}", host.name, str(e))
            continue
        else:
            if result.ok:
                # successful df command
                disks = get_disks(host, result.stdout)
                notifications.append(Notification.from_disk(host, disks))
            else:
                # failed to get usage
                continue
    return notifications


def main():
    configure_root_logger()
    notifications = check(HOSTS)
    print(notifications)


if __name__ == "__main__":
    main()
