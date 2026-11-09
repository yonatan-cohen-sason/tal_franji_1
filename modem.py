from loramodem import LoRaModem
import base64
import struct
import time

pub64 = "pRzWWkFqhM2Mf7tYy6zm9z1BGRQYXJWehINhKD2HVgprg9/5S7kosOhv/UdqNbGFdiJZEkjnzARlk6BeTnEpSXMvgSphJ54wXY3oTrt2WgJEtcH1bEAsuVzuo1f4lh0u5X6LMiWtuqAhoT6uqSNpWp+xM/6Kas+eGxWAsi9lIZc="

pub_key_bytes = base64.b64decode(pub64)
key_id = struct.unpack("!I", pub_key_bytes[:4])[0]
key_id_bytes = struct.pack("!I", key_id)

# First 8 Base64 characters of each public key
users = {
    "itaiyehuda22": "sgGlvSpa",
    "enriquecostro2": "o0es4jND",
    "juk.crusher": "nIBbmPe7",
    "gal.oron.main": "un98NxTY",
    "talkeinan11": "tD8az7ip",
    "eyal.mass2011": "tEjoQ8ac",
    "nehorai0210": "vKJPCApG",
    "jonathan": "wkrz8gA4",
    "cohensason1": "pRzWWkFq",
    "ariel.zalait1": "y8Ln9jy7",
    "adva.gerenrot": "iYelQTjZ",
    "dariadobriyan": "xIgDy//f",
    "lielkolani": "uEsCaJlP",
    "shtars88": "ntHzAOgq",
    "yotamsofer2011": "w4gtVixi",
    "ivry.guy": "4SfoAmpa",
    "reshefamit11": "vB4/NQUy",
    "betteshitamar": "MIGfMA0G",
    "yoaveventzor": "sr5aMiui",
    "leannenissenson": "u8D0CxR6",
    "ratzabieliran10": "uQey2g8S"
}

# Map 4-byte key IDs to usernames
key_to_user = {
    base64.b64decode(prefix)[:4]: username
    for username, prefix in users.items()
}



with LoRaModem("sim") as modem: 
    #     ^^ use "1" instead of "sim" for radio
	modem.configure_packet_mode()

# def send_message(text):
#     message = key_id_bytes + text.encode("utf-8")
#     modem.send_to_simulator(message)

dict = {}
i =0 
while True:
    data = modem.read_from_simulator()

    if data and len(data) >= 4:
        sender_id = data[:4]
        message = data[4:].decode("utf-8", errors="replace")
        username = key_to_user.get(sender_id,f"Unknown ({sender_id.hex()})")
        print(f"{username}: {message}")

        sender_key = struct.unpack("!I", sender_id)[0]

        if sender_key in dict:
            dict[sender_key] += 1
        else:
            dict[sender_key] = 1

    if i >= 25:
        M = list(dict.items())
        M.sort(key = lambda x: x[1])
        packed = b""
        for sender_key, count in M:
            packed += struct.pack("!IH", sender_key, count)
        modem.write_bytes(key_id_bytes + packed)
        i = -1

    i+= 1
    time.sleep(0.2)
