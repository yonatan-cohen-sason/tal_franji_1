import time
import base64
import requests
from pubkey import RSA1024

ROUTER_URL = "http://localhost:8080"


def make_user(nick, name, phone):
    key = RSA1024.generate()
    key_b64 = base64.b64encode(key.public_bytes()).decode("utf-8")
    return {"key_b64": key_b64, "nick": nick, "name": name, "phone": phone}


def send_alive(user):
    r = requests.post(ROUTER_URL + "/alive" ,  json=user)
    if r.json()["status"] != "OK":
        print(f"alive {user['nick']} FAILED: {r.json()}")


def print_users():
    r = requests.get(ROUTER_URL + "/users")
    users = r.json()["users"]
    print(f"--- router knows {len(users)} users ---")
    for u in users:
        where = "local" if u["is_local"] else "radio"
        print(f"  {u['key_id']:08x}  {u['nick']:10}  {where}")


def main():
    my_users = [
        make_user("yonatan", "Yonatan", "050-1111111"),
        make_user("guy", "Guy" , "053-0876542"),
        make_user("nehorai", "Nehorai", "052-6767676"),
    ]
    while True:
        for user in my_users:
            send_alive(user)
        print_users()
        time.sleep(5)


if __name__ == "__main__":
    main()