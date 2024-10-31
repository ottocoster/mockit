import socket
import threading
import logging
from src.telnet_server.telnet_handler import Telnet_Handler

# Server Configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 23  # Default Telnet port, but requires admin rights to run on Unix-based OS

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

# Start Telnet Server
def start_telnet(options):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    logger.debug(f"Telnet server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print(f"Connection established with {addr}")
        handler = Telnet_Handler(conn, options)
        threading.Thread(target=handler.run, args=()).start()