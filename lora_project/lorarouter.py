import base64
import struct
import time
from loramodem import LoRaModem
import threading
import queue
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class RouterHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/status":
            response = {"status": "OK"}
        else:
            response = {"status": "error"}

        response_data = json.dumps(response)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response_data.encode("utf-8"))


def radio_loop():
    while True:
        print("radio: tick")
        time.sleep(2)

def main():
    radio_thread = threading.Thread(target = radio_loop, daemon = True )
    server_address = ("", 8090)  
    httpd = ThreadingHTTPServer(server_address, RouterHandler)
    print("Router listening...")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
