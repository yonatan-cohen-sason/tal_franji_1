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
        # self.path הוא מה שבא אחרי הכתובת, למשל "/status"
        if self.path == "/status":
            response = {"status": "OK"}
        else:
            response = {"status": "error"}

        response_data = json.dumps(response)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response_data.encode("utf-8"))


def main():
    server_address = ("", 8090)   # באיזה פורט הראוטר צריך להאזין? (רמז: זה כתוב ב-router_client.py)
    httpd = ThreadingHTTPServer(server_address, do_get())   # איזו מחלקה מטפלת בבקשות?
    print("Router listening...")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
