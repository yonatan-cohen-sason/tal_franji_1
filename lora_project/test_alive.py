import base64
import requests
from pubkey import RSA1024

key = RSA1024.generate()
key_b64 = base64.b64encode(key.public_bytes()).decode("utf-8")

data = {"key_b64": key_b64, "nick": "yonatan", "name": "Yonatan", "phone": "050"}
r = requests.post("http://localhost:8090/alive", json=data)
print(r.json())