import socket
import time
import traceback
import random
import folium
import sys

import requests


# Global variables
# fmt: off
random_ips = ["1.85.52.250:9797", "1.179.144.41:8080", "1.179.148.9:36476", "2.58.217.1:8080", "2.138.28.204:3128", "3.20.236.208:49205", "3.94.253.49:8118", "3.215.177.148:49205", "4.16.68.158:443", "5.8.53.7:18081", "5.9.180.204:8080", "5.54.186.76:8080", "5.75.144.136:8080", "5.78.40.148:8080", "5.78.42.62:50001", "5.78.42.170:8080", "5.78.45.181:8080", "5.78.65.102:8080", "5.78.65.154:8080", "5.78.66.187:8080", "5.78.67.98:8080", "5.78.74.216:8080", "5.78.77.53:8080", "5.78.77.147:8080", "5.78.78.180:8080", "5.78.79.86:8080", "5.78.79.113:8080", "5.78.80.192:8080", "5.78.82.23:8080", "5.78.82.159:8080", "5.78.83.223:8080", "5.78.84.83:8080", "5.78.84.152:8080", "5.78.84.238:8080", "5.78.85.193:8080", "5.78.86.51:8080", "5.78.88.74:8080", "5.78.88.155:8080", "5.78.88.216:8080", "5.78.89.219:8080", "5.78.91.40:8080", "5.78.91.180:8080", "5.78.91.200:8080", "5.78.91.242:8080", "5.78.92.65:8080", "5.78.92.68:50001", "5.78.93.237:8080", "5.78.94.70:8080", "5.78.95.138:8080", "5.78.95.164:8080", "5.78.96.218:8080", "5.78.98.67:8080", "5.78.98.128:8080", "5.78.99.122:8080", "5.78.99.255:50001", "5.78.100.167:8080", "5.78.100.214:8080", "5.78.102.25:8080", "5.78.102.164:8080", "5.78.103.177:8080", "5.78.103.222:8080", "5.78.103.224:8080", "5.104.174.199:23500", "5.135.1.146:25275", "5.135.170.126:8080", "5.160.101.234:8080", "5.160.175.226:8383", "5.161.110.95:50001", "5.161.180.82:50001", "5.187.9.10:8080", "5.206.236.154:8080", "8.140.3.10:8083", "8.219.115.145:3128", "8.219.176.202:8080", "8.242.178.3:999", "8.242.205.41:9991", "12.36.95.132:8080", "12.88.29.66:9080", "14.161.26.100:8080", "14.161.31.192:53281", "14.161.33.150:8080", "14.170.154.193:19132", "14.207.6.195:8080", "14.207.44.76:8080", "14.207.59.165:8080", "14.207.97.67:8080", "14.239.24.238:8080", "14.241.46.131:8080", "14.241.225.167:80", "14.250.20.146:8080", "18.205.24.179:9999", "18.216.72.10:5678", "18.222.17.49:49205", "20.74.169.104:8118", "20.239.171.216:80", "23.88.46.48:8080", "23.88.47.183:8080", "23.88.63.221:8080", "23.132.185.101:53128", "24.51.32.59:8080", "24.152.49.226:999", "24.192.227.234:8080", "24.230.33.96:3128", "27.54.71.231:8080", "27.54.71.234:8080", "27.111.45.29:55443", "27.121.82.44:8085", "27.130.64.124:8080", "27.130.67.110:8080", "27.130.126.171:8080", "27.147.209.215:8080", "27.150.35.112:8089", "31.28.8.196:9898", "31.43.52.176:41890", "31.46.33.59:53281", "31.145.154.138:9093", "31.146.116.18:8080", "31.146.216.246:8080", "31.161.38.233:8090", "31.214.171.62:3128", "34.118.65.91:3128", "34.228.116.189:9999", "34.229.130.62:49205", "36.6.145.1:8089", "36.6.145.251:8089", "36.37.86.27:9812", ]

fake_HTTP_header = {
    "referer": "https://ipinfo.io/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36",
}
# fmt: on
# End global variables


def traceroute(ip):
    # UDP socket
    udp_send_sock = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP
    )

    # RAW socket for reading ICMP responses
    icmp_recv_socket = socket.socket(
        socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP
    )

    # Set timeout if the ICMP socket for the recvfrom call does not receive anything in the buffer
    icmp_recv_socket.settimeout(10)

    # Set the UDP port number with something between 33434 to 33534.
    port = 33435

    latitudes = []
    longitudes = []

    # counter of fails to recieve an answer
    cnt_fails = 0

    TTL = 1
    while True:
        # Set TTL in the IP header for the UDP socket
        udp_send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)

        # Send a UDP message to a tuple (IP, port)
        udp_send_sock.sendto(b"", (ip, port))

        try:
            data, addr = icmp_recv_socket.recvfrom(1024)

            info, lat, lon = get_info_ip(addr[0])
            if info == "Unavailable":
                print("Failed to get info of IP address, retrying in 60 seconds")
                time.sleep(60)
                info, lat, lon = get_info_ip(addr[0])
            print(info)
            if lat != "Unavailable" and lon != "Unavailable":
                latitudes.append(lat)
                longitudes.append(lon)

            if addr[0] == ip:
                break
            # Reset the fails count
            cnt_fails = 0
        except Exception as e:
            cnt_fails += 1
            if cnt_fails > 3:
                print("Failed to many times :(")
                print(traceback.format_exc())
                break
            print("Failed to recieve an answer, retrying")
        TTL += 1

    print("Done!")
    udp_send_sock.close()
    icmp_recv_socket.close()

    if len(latitudes) > 0:
        m = folium.Map()
        for lat, lon in zip(latitudes, longitudes):
            folium.Marker(
                location=[lat, lon],  # lat, lon for the marker
                icon=folium.Icon(icon="cloud"),  # icon for the marker
            ).add_to(m)
        points = list(zip(latitudes, longitudes))
        folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
        m.save(f"raports/map_{ip}.html")
        print(f"Saved the map as map_{ip}.html")


def get_info_ip(ip):
    """
    Returns city, region and country of the IP as string or "Unavailable".
    """
    url = f"http://ip-api.com/json/{ip}"
    client = random.choice(random_ips)
    fake_HTTP_header["X-Forwarded-For"] = f"{client}"
    fake_HTTP_header["X-Real-IP"] = client

    r = requests.get(url, headers=fake_HTTP_header)

    if r.status_code != 200:
        return "Unavailable"
    data = r.json()

    city = data["city"] if "city" in data else "Unavailable"
    region = data["region"] if "region" in data else "Unavailable"
    country = data["country"] if "country" in data else "Unavailable"
    lat = data["lat"] if "lat" in data else "Unavailable"
    lon = data["lon"] if "lon" in data else "Unavailable"
    return (f"City: {city}, Region: {region}, Country: {country}", lat, lon)


if len(sys.argv) > 1:
    ip = sys.argv[1]
    print(ip)
    traceroute(ip)
else:
    print("Please provide an IP address as a command-line argument.")
