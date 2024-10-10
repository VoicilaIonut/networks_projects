# Traceroute, ARP Spoofing, and TCP Hijacking Project

This project demonstrates the implementation of a traceroute application, ARP spoofing, and TCP hijacking attacks. It includes detailed analysis and reports of the results. The project is divided into several tasks.

## Table of Contents

- [Traceroute](#traceroute)
  - [Features](#features)
- [ARP Spoofing and TCP Hijacking](#arp-spoofing-and-tcp-hijacking)
  - [Container Structure](#container-structure)
     - [Containers explained](#containers-explained)
  - [ARP Spoofing](#arp-spoofing)
  - [TCP Hijacking](#tcp-hijacking)
- [Disclaimer](#disclaimer)

## Traceroute

Traceroute is a method used to trace the path packets take through routers to reach their destination. By examining the IP addresses of these nodes, we can determine the countries or regions the packets traverse. For each UDP message in transit to the destination, if the TTL (Time to Live) expires, the sender receives an ICMP message of type "Time Exceeded TTL expired in transit".

### Features

- **Location Analysis**: Uses an API to provide information about the location of IP addresses.
- **Reports**: Generates text or markdown reports that include:
  - City, Region, and Country (where available) through which your message passes to reach its destination.
  - Routes through various countries on a map using a plotting library.

### Test by running:
1. **Install Dependencies**: Ensure you have Python and the required libraries installed. You can install the necessary libraries using pip:
```sh
pip install requests folium
```
2. **Run the Script**: Execute the script from the command line, providing an IP address as a command-line argument:
```sh
python traceroute.py <IP_ADDRESS>
```

## ARP Spoofing and TCP Hijacking

### Container Structure

```
            MIDDLE------------\
        subnet2: 198.7.0.3     \
        MAC: 02:42:c6:0a:00:02  \
               forwarding        \ 
              /                   \
             /                     \
Poison ARP 198.7.0.1 is-at         Poison ARP 198.7.0.2 is-at 
           02:42:c6:0a:00:02         |         02:42:c6:0a:00:02
           /                         |
          /                          |
         /                           |
        /                            |
    SERVER <---------------------> ROUTER <---------------------> CLIENT
net2: 198.7.0.2                      |                           net1: 172.7.0.2
MAC: 02:42:c6:0a:00:03               |                            MAC eth0: 02:42:ac:0a:00:02
                           subnet1:  172.7.0.1
                           MAC eth0: 02:42:ac:0a:00:01
                           subnet2:  198.7.0.1
                           MAC eth1: 02:42:c6:0a:00:01
                           subnet1 <------> subnet2
                                 forwarding
```

To build the containers, run:

```sh
docker compose up -d
```

The image is built based on the docker/Dockerfile. If modifications are made to the file or shell scripts, run:

```sh
docker-compose build --no-cache
```

Observations

The ARP cache tables of the router and server containers may update slowly. To avoid long verification times, clear the ARP cache before or while triggering the attack using:

```sh
ip -s -s neigh flush all
```

#### Containers explained
The container architecture is defined as follows:

- *Server*: Listens for messages from the client.

- *Middle*: Sets `ip_forwarding=1` and the rule `iptables -t nat -A POSTROUTING -j MASQUERADE` to allow messages that are forwarded by it to exit the local network.

- *Router*: Acts as the default gateway for the client and server.

- *Client*: Sends messages to the server through the router.

### ARP Spoofing
[ARP spoofing](https://www.crowdstrike.com/en-us/cybersecurity-101/social-engineering/arp-spoofing/) involves sending an ARP reply packet to a target to misinform it about the MAC address associated with an IP.

The code runs the ARP table poisoning process for the server and router containers constantly, with a time.sleep of a few seconds to avoid flooding packets through two threads.

####  Test by running:
In the middle container:
```sh
python snifing.py
```
and:
```sh
tcpdump -SntvXX -i any
```
In the server container:
```sh
wget http://old.fmi.unibuc.ro
```
If the middle container can see the HTML content from the server's request, the attack was successful.

### TCP Hijacking
[TCP Hijacking](https://www.geeksforgeeks.org/tcp-ip-hijacking/) is a form of cyber attack in which an authorized user gains access to a legitimate connection of another client in the network. Having hijacked the TCP/IP session, the attacker can read and modify transmitted data packets, as well as send their own requests to the addressee.

Used [Netfilter Queue](https://www.netfilter.org/projects/libnetfilter_queue/) to queue network messages and processed them with [Scapy](https://scapy.net/).

####  Test by running:
Run `tcp_server.py`, `tcp_client.py`, and `snifing.py` from the repository on the server, client, and middle containers respectively to continuously send random messages between the client and server, with the middle container intercepting and registering them.

#### Observations
1. Used `time.sleep` to avoid flooding

2. Modifed the content of the messages sent by the client and server and inserted an additional message into the TCP payload. Both the client and server will display the inserted message


# Disclaimer
The attacks implemented in this project are for educational purposes only. 

Do not use these methods to attack other people on a local network.

*Project completed as an assignment for the Computer Networks course at the University of Bucharest.