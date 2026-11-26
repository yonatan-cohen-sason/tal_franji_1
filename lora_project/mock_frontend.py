import requests

key_b64 = "pRzWWkFqhM2Mf7tYy6zm9z1BGRQYXJWehINhKD2HVgprg9/5S7kosOhv/UdqNbGFdiJZEkjnzARlk6BeTnEpSXMvgSphJ54wXY3oTrt2WgJEtcH1bEAsuVzuo1f4lh0u5X6LMiWtuqAhoT6uqSNpWp+xM/6Kas+eGxWAsi9lIZc="

data = {"key_b64": key_b64, "nick": "yonatan", "name": "Yonatan", "phone": "050"}
r = requests.post("http://localhost:8080/alive", json=data)
print(r.json())