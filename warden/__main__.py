import logging
from typing import List
from fabric import Connection
import smtplib, ssl
import re
from warden import HOSTS, Notification, Host, DiskUsage, configure_root_logger, get_config


def notify(notifications: List[Notification]):
    if len(notifications) <= 0:
        print("No notifications")
        return

    message = "Subject:[Warden] Disk status warning\n\nFollowing hosts needs your attention:\n"
    for notification in notifications:
        notification_string = "\n\t{} [threshold={}%]: ".format(notification.host, notification.threshold)
        for disk in notification.disks:
            notification_string += "\n\t\t{} -> {}%".format(disk.name, disk.usage)
        message += notification_string

    # connect to mail server and send notifications
    context = ssl.create_default_context()
    with smtplib.SMTP(get_config("mail.host"), get_config("mail.port")) as server:
        server.starttls(context=context)
        server.login(get_config("mail.user"), get_config("mail.password"))

        server.sendmail(get_config("mail.user"), get_config("mail.wardens"), message)


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
    logger = logging.getLogger("check")
    notifications = []
    for host in hosts:
        try:
            con = Connection(host=host.host, user=host.user)
            result = con.run("df -h", hide=True)
        except Exception as e:
            print("Unable to run commands on {}: {}".format(host.name, str(e)))
            continue
        else:
            if result.ok:
                # successful df command
                disks = get_disks(host, result.stdout)
                if len(disks) > 0:
                    notifications.append(Notification.from_disk(host, disks))
                else:
                    logger.info("No notification is needed for '{}'".format(host.name))
            else:
                # failed to get usage
                continue
    return notifications


def main():
    configure_root_logger()
    notifications = check(HOSTS)
    notify(notifications)


if __name__ == "__main__":
    main()
