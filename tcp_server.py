import socket
import logging
import time

logging.basicConfig(
    format="[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s",
    level=logging.NOTSET,
)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

port = 10000
adresa = "0.0.0.0"
server_address = (adresa, port)
sock.bind(server_address)
logging.info("The server started on %s and port %d", adresa, port)
sock.listen(5)

conexiune = None
while conexiune == None:
    logging.info("Waiting for connections...")
    conexiune, address = sock.accept()
    logging.info("Handshake with %s", address)

while True:
    try:
        data = conexiune.recv(1024)
        logging.info(b"Server received: " + data)

        conexiune.send(b"Server received: " + data)
        time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Exiting")
        conexiune.close()
        sock.close()
        exit()
