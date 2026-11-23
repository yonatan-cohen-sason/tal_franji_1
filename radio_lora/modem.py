import base64
import struct
import time
from tal_franji_1.loramodem import LoRaModem
import random
senders = {
    b'\xb2\x01\xa5\xbd': "itaiyehuda22@gmail.com",
    b'\xa3G\xac\xe2': "enriquecostro2@gmail.com",
    b'\x9c\x80[\x98': "juk.crusher@gmail.com",
    b'\xba\x7f|7': "gal.oron.main@gmail.com",
    b'\xb4?\x1a\xcf': "talkeinan11@gmail.com",
    b'\xb4H\xe8C': "eyal.mass2011@gmail.com",
    b'\xbc\xa2O\x08': "nehorai0210@gmail.com",
    b'\xc2J\xf3\xf2': "jonathan@jbiton.com",
    b'\xa5\x1c\xd6Z': "cohensason1@mail.tau.ac.il",
    b'\xcb\xc2\xe7\xf6': "ariel.zalait1@gmail.com",
    b'\x89\x87\xa5A': "adva.gerenrot@gmail.com",
    b'\xc4\x88\x03\xcb': "dariadobriyan@gmail.com",
    b'\xb8K\x02h': "lielkolani@mail.tau.ac.il",
    b'\x9e\xd1\xf3\x00': "shtars88@gmail.com",
    b'\xc3\x88-V': "yotamsofer2011@gmail.com",
    b"\xe1'\xe8\x02": "ivry.guy@gmail.com",
    b'\xbc\x1e?5': "reshefamit11@gmail.com",
    b'0\x81\x9f0': "betteshitamar@gmail.com",
    b'\xb2\xbeZ2': "yoaveventzor@gmail.com",
    b'\xbb\xc0\xf4\x0b': "leannenissenson@gmail.com",
}

keys = dict()       # sender -> כמה הודעות שלח
last_msg = dict()   # sender -> ההודעה האחרונה שלו

# Claude: key_id מתוך המפתח הציבורי - cohensason1
pub64 = "pRzWWkFqhM2Mf7tYy6zm9z1BGRQYXJWehINhKD2HVgprg9/5S7kosOhv/UdqNbGFdiJZEkjnzARlk6BeTnEpSXMvgSphJ54wXY3oTrt2WgJEtcH1bEAsuVzuo1f4lh0u5X6LMiWtuqAhoT6uqSNpWp+xM/6Kas+eGxWAsi9lIZc="
key_id_bytes = base64.b64decode(pub64)[:4]
print("My key_id:", key_id_bytes.hex())
LOG_FILE = "messages.txt"
sent_count = 0
next_send = time.time()

# Claude: מטריצה של כולם - matrix[מי מדווח][על מי] = כמה
matrix = {}

# Claude: שם קצר לטבלה
def short(k):
    return senders.get(k, k.hex()).split("@")[0][:10]

# Claude: הדפסת המטריצה
def print_matrix():
    matrix[key_id_bytes] = {key_id_bytes: sent_count, **keys}
    people = sorted(set(matrix) | {k for row in matrix.values() for k in row}, key=short)
    print("=== Matrix (row = reporter, column = about) ===")
    print(" " * 11 + "".join(f"{short(p):>11}" for p in people))
    for r in people:
        row = matrix.get(r, {})
        print(f"{short(r):<11}" + "".join(f"{row.get(c, ''):>11}" for c in people))

modem = LoRaModem("sim", 10)

while True:
    data = modem.read_from_simulator()
    if data and data[:4] != key_id_bytes:
        sender = data[:4]
        content = data[4:]
        name = senders.get(sender, f"Unknown ({sender.hex()})")

        if sender not in keys:
            keys[sender] = 1
        else:
            keys[sender] += 1
        last_msg[sender] = content

        print(f"{name} sent: {content.decode('utf-8', errors='replace')}")

        if len(data) % 6 == 0:
            recs = [struct.unpack_from("!4sH", data, i) for i in range(0, len(data), 6)]
            # Claude: מי ששלח בלי "!" - הבתים של המונה הפוכים (כל המספרים כפולות של 256) -> הופכים בחזרה
            if any(c for _, c in recs) and all(c % 256 == 0 for _, c in recs):
                recs = [(k, c >> 8) for k, c in recs]
            with open(LOG_FILE, "a") as f:
                for key, count in recs:
                    f.write(f"{int(time.time())},{sender.hex()},{key.hex()},{count}\n")
                    matrix.setdefault(sender, {})[key] = count   # Claude: שמירה במטריצה

    if time.time() >= next_send:
        sent_count += 1
        message = bytearray()
        message.extend(struct.pack("!4sH", key_id_bytes, sent_count))
        for key, count in keys.items():
            message.extend(struct.pack("!4sH", key, count))
        modem.send_to_simulator(bytes(message))
        # Claude: הדפסה ברורה של מה שנשלח
        print(f">>> שלחתי הודעה מספר {sent_count}")
        for key, count in keys.items():
            print(f"    אמרתי שקיבלתי {count} הודעות מ-{short(key)}")

        print("=== Message counts ===")
        for key, count in sorted(keys.items(), key=lambda t: t[1], reverse=True):
            name = senders.get(key, f"Unknown ({key.hex()})")
            last = last_msg[key].decode("utf-8", errors="replace")
            print(f"{name}: {count} | last: {last}")
        print("======================")
        print_matrix()   # Claude: הצגת המטריצה

        next_send = time.time() + random.uniform(5, 10)

    time.sleep(0.1)
