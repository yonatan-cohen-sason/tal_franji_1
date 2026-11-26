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
    return struct.pack("!BBI128s", 0xAE, 1, int(time.time()), key_bytes)

def handle_alive(request):
    key_b64 = request["key_b64"]               
    key_bytes = base64.b64decode(key_b64)     
    key_id = struct.unpack("!I", key_bytes[:4])[0]    
    with users_lock:
        if key_id not in users:
            users[key_id] = {
                "key_id": key_id,
                "key_b64": key_b64,
                "is_local": True,
                "delay_secs": 0,
                "publish_count": 0,
                "last_published": 0,
            }
            print(f"new user {key_id:08x}")
        user = users[key_id]
        user["nick"] = request.get("nick", "") 
        user["name"] = request.get("name", "")
        user["phone"] = request.get("phone", "")
        print(f"alive from {key_id:08x}, now {len(users)} users")
    return {"status": "OK", "messages": []}




def choose_user_to_publish(now, last_send):
    with users_lock:
        local_users = []
        new_users = []
        for user in users.values():
            if user["is_local"]:
                local_users.append(user)
                if user["publish_count"] < 3:
                    new_users.append(user)

        if not local_users:
            return None

        if new_users:
            interval = 60
            candidates = new_users
        else:
            interval = 15*60
            candidates = local_users

        if now - last_send < interval:
            return None

        return min(candidates, key=lambda u: u["last_published"])



def handle_radio_packet(packet):
    # 1. לבדוק שזו הודעת key-publish
    if len(packet) != 134 or packet[0] != 0xAE or packet[1] != 1:
        print("radio: ignoring packet", packet[:6].hex())
        return
    ae, kind, utime, key_bytes = struct.unpack("!BBI128s", packet)

    key_id = struct.unpack("!I", key_bytes[:4])[0]
    key_b64 = base64.b64encode(key_bytes).decode("utf-8")

    delay_secs = int(time.time()) - utime
    with users_lock:
        if key_id in users and users[key_id]["is_local"]:
            return
        users[key_id] = {
            "key_id": key_id,
            "key_b64": key_b64,
            "nick": "",
            "name": "",
            "phone": "",
            "is_local": False,
            "delay_secs": delay_secs,
        }
        print(f"radio: learned user {key_id:08x}, delay {delay_secs}s, now {len(users)} users")




def radio_loop():
    with LoRaModem("sim") as modem:           
        modem.configure_packet_mode()          
        print("radio: modem ready")          
        last_send = 0                         
        while True:                                  
            now = time.time()
            user = choose_user_to_publish(now, last_send)
            if user is not None:
                packet = build_key_publish(user["key_b64"])
                modem.write_bytes(packet)
                last_send = now
                with users_lock:
                    user["publish_count"] += 1
                    user["last_published"] = int(now)
                print(f"radio: sent key-publish for {user['key_id']:08x} (time #{user['publish_count']})")
            packet = modem.read_bytes()
            if packet:
                handle_radio_packet(packet)
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
