import pubkey
import base64

x = pubkey.RSA1024.generate()
data = x.public_bytes()
encoded = base64.b64encode(data).decode("utf-8")

print("public key:", encoded)