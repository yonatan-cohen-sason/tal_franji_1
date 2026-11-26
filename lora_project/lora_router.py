import base64
import struct
import time
from loramodem import LoRaModem
import threading
import queue
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

users = {}
users_lock = threading.Lock()

class RouterHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/status":
            response = {"status": "OK"}
        elif self.path == "/users":
            with users_lock:
                response = {"status": "OK", "users" : list(users.values())}
        else:
            response = {"status": "error"}

        response_data = json.dumps(response)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response_data.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length)
        request = json.loads(body)
        print("got POST:", self.path, request)

        if self.path == "/alive":
            response = handle_alive(request)
        else:
            response = {"status": "error"}

        response_data = json.dumps(response)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response_data.encode("utf-8"))


def build_key_publish(key_b64):
    key_bytes = base64.b64decode(key_b64)
    return struct.pack("!BBI128s", \xAE, 1, int(time.time()), key_bytes)

def handle_alive(request):
    key_b64 = request["key_b64"]               
    key_bytes = base64.b64decode(key_b64)     
    key_id = struct.unpack("!I", key_bytes[:4])[0]    
    with users_lock:
        users[key_id] = {
            "key_id": key_id,
            "key_b64": key_b64,
            "nick": request.get("nick", ""),    
            "name": request.get("name", ""),
            "phone": request.get("phone", ""),
            "is_local": True,
            "delay_secs" : 0,              
        }
        print(f"alive from {key_id:08x}, now {len(users)} users")
    return {"status": "OK", "messages": []}

def radio_loop():
    with LoRaModem("sim") as modem:           
        modem.configure_packet_mode()          
        print("radio: modem ready")          
        last_send = 0                         
        while True:                                  
            now = time.time()
            if now - last_send >= 10:
                last_send = now
                with users_lock:
                    local_users = []
                    for user in users.values():
                        if user[is_local]:
                            local_users.append(user)
                if local_users:
                    user = local_users[0]
                    packet = build_key_publish(user[key_b64])
                    modem.write(packet)
                    print(f"radio: sent key-publish for {user['key_id']:08x}, {len(packet)} bytes")
            packet = modem.read_bytes()
            if packet:
                print("radio: received", len(packet), "bytes:", packet[:6].hex())
            else:
                time.sleep(1)

def main():
    radio_thread = threading.Thread(target = radio_loop, daemon = True )
    radio_thread.start()
    server_address = ("", 8080)  
    httpd = ThreadingHTTPServer(server_address, RouterHandler)
    print("Router listening...")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
