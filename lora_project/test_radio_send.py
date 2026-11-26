import base64, struct, time
from loramodem import LoRaModem
from pubkey import RSA1024

key_bytes = RSA1024.generate().public_bytes()
packet = struct.pack("!BBI128s", 0xAE, 1, int(time.time()), key_bytes)

with LoRaModem("sim") as modem:
    modem.configure_packet_mode()
    modem.write_bytes(packet)
    print("sent key-publish for", key_bytes[:4].hex())