# Claude: בדיקת רדיו - מנסה מהירויות שונות ומדפיס מה הרדיו עונה
import time
import serial

PORT = "COM20"

for speed in [115200, 9600, 19200, 38400, 57600]:
    for plus in [b"+++", b"+++\r\n"]:
        try:
            s = serial.Serial(PORT, speed, timeout=0.3)
        except Exception as e:
            print("cannot open port:", e)
            raise SystemExit
        s.reset_input_buffer()
        time.sleep(1.2)
        s.write(plus)            # כניסה למצב פקודות
        time.sleep(1.2)
        s.write(b"AT\r\n")       # פקודת בדיקה - צריך לקבל OK
        time.sleep(0.5)
        resp = s.read(200)
        s.write(b"AT+EXIT\r\n")  # יציאה ממצב פקודות
        time.sleep(0.3)
        s.close()
        ok = b"OK" in resp
        print(f"speed={speed:<7} plus={plus!r:<12} {'<<< OK!' if ok else ''} answer={resp!r}")
        if ok:
            print(f"\n==> use: LoRaModem(\"{PORT}\", {speed})")
            raise SystemExit
print("\nno answer at any speed")
