import requests

data = {"key_b64": "AAAA", "nick": "yonatan"}
r = requests.post("http://localhost:8090/alive", json=data)
print(r.json())