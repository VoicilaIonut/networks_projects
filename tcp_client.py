import socket
import logging
import time
import sys

logging.basicConfig(
    format="[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s",
    level=logging.NOTSET,
)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)

port = 10000
adresa = "198.7.0.2"
server_address = (adresa, port)
mesaj = sys.argv[1]

logging.info("Message sent: %s", mesaj)

logging.info("Attempting to connect to %s on port %d", adresa, port)
try:
    sock.connect(server_address)
    logging.info("Connected to %s on port %d", adresa, port)
except socket.error as e:
    logging.error("Connection to %s on port %d failed", adresa, port)

while True:
    try:
        sock.send(mesaj.encode("utf-8"))
        logging.info('Content sent: "%s"', mesaj)

        data = sock.recv(1024)
        logging.info('Content received: "%s"', data)

        time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Exiting")
        sock.close()
        exit()
