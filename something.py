import base64
import struct
pub64 = "pRzWWkFqhM2Mf7tYy6zm9z1BGRQYXJWehINhKD2HVgprg9/5S7kosOhv/UdqNbGFdiJZEkjnzARlk6BeTnEpSXMvgSphJ54wXY3oTrt2WgJEtcH1bEAsuVzuo1f4lh0u5X6LMiWtuqAhoT6uqSNpWp+xM/6Kas+eGxWAsi9lIZc="
pub_key_bytes = base64.b64decode(pub64)
pub_key_bytes[:4]  # this is the key_id
# key_id as 32 bit integer (from 4 bytes)
key_id = struct.unpack("!I", pub_key_bytes[:4])[0]  
print(key_id)
# converting integer key_id back to 4 bytes
key_id_bytes = struct.pack("!I", key_id)
