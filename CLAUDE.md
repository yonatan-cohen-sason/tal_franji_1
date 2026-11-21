# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Coursework for a Python course (instructor: Tal Franji). It's a set of standalone scripts, not a package. There's no build system, test suite, linter or requirements file. Most work belongs to the **LoRa Text** project: an encrypted, multi-hop text-messaging network built on LoRa radio modems (Waveshare SX1262 USB-to-LoRa), with a Raspberry Pi router and a Java web front end. Smaller side exercises (snake, threading) are also here.

The comments and print strings are a mix of Hebrew and English. Comments starting with `# Claude:` were written by an earlier AI session.

## Running things

Dependencies are installed by hand: `pip install pyserial requests pycryptodome` (the `Crypto` import comes from pycryptodome). The curses scripts also need `pip install windows-curses` on Windows.

Each script runs directly with `python <file>.py`:

- `python loramodem.py <device>`: runs a send/receive loopback test of the modem. `<device>` can be `COM20`, a 1-based port index (`1`), `sim`, a simulator URL, or `dummy`.
- `python radio_test.py`: probes the baud rates on `COM20` to find one where the radio answers `+++`/`AT` with `OK`.
- `python modem.py`: the counting/matrix exercise, run against the cloud simulator.
- `python spammer1.py`: the same exercise on the real modem at `COM20`.
- `python lora_common/pubkey.py`: runs the RSA self-tests (the root `pubkey.py` has no `__main__`). You can also use `pytest pubkey.py`, since the tests are named `test_*`.
- `python lora_common/router_client.py --new-user <nick> [--url http://localhost:8090] [--plain] [--verbose]`: a load-test client for the router's REST API. It creates `user_<nick>.json` (which holds a private key) in the current directory and allows only one instance per directory, enforced with `router_client.lock`.
- Snake: start `python snake_server.py` (curses game plus an HTTP server on port 8080), then run `python "snake_client .py"`. The client's filename contains a space.

## Architecture

**`loramodem.py` / `LoRaModem`** is the transport layer every LoRa script uses. One class hides three backends:
- **Real serial modem**: AT-command mode is entered with `+++` followed by a 1.1 s wait and left with `AT+EXIT`. `configure_packet_mode()` sets `AT+MODE=1`, `ADDR=65535` and `LBT=1`. In packet mode, packets go over serial as hex text lines with a 3-byte prefix `FF FF 12` (broadcast address and channel 18), which `read_packet` strips off.
- **HTTP simulator** (`"sim"` maps to Franji's cloud node `http://34.165.8.95:8080`): packets are sent as urlsafe-base64 in GET `?p=...&s=<random seq>`. Every GET (including the polls with no payload) returns a `payloads` array. Sequence numbers in `simulator_seen_seq` stop a node from receiving its own packets. HTTP 429 is retried.
- **`DummySerial`**: a no-op stub.

When the backend is the simulator, the speed argument is ignored. `modem.py` passes `10`.

**`pubkey.py` / `RSA1024`** is the crypto layer. It uses raw textbook RSA with no padding, by calling pycryptodome's private `_encrypt`/`_decrypt` directly. The method names are inverted on purpose:
- `decrypt()` uses the **private** key and doubles as *signing*.
- `encrypt()` uses the **public** key and doubles as *verifying*.
- To send, compute `crypt2 = receiver_pub.encrypt(sender.decrypt(payload))`. To receive, reverse it: `sender_pub.encrypt(receiver.decrypt(crypt2))`. `router_client.py` applies the two operations in the opposite nesting, so check that before you change either side.
- Public keys travel as 128 bytes: the DER encoding with the fixed `RSA_1024_DER_HEADER` stripped off. The **key_id** is the first 4 bytes, read as a big-endian uint32. Keys show up as base64 strings (`pub64`/`key_b64`).

Keep the two copies of `pubkey.py` (root and `lora_common/`) in sync. They differ only in the `__main__` block.

**Protocol specs** are in `lora_common/LoRa_text_protocol.md` (binary messages) and `lora_common/LoRa_Text_Router.md` (router REST API). Read them before you touch the wire format:
- Every packet starts with `0xAE` followed by a kind byte: 1 key-publish, 2 user-details, 3 text, 4 routing, 5 plain, 6 routing-plain. Then comes a big-endian `utime` and the sender key_id. The `struct` formats are given in the doc, e.g. `"!BBIII128s"`.
- The text payload is `seq, ack_seq, text_len` (`"BBB"`) followed by UTF-8. `seq` runs from 1 to 255 per sender→recipient pair and wraps back to 1, skipping 0.
- The router REST API has `GET /stats`, `GET /users`, `POST /alive`, `POST /text` and `POST /plain`. Every response carries `"status": "OK"|"error"`. `router_client.py` is the reference client. It also reports `SENT/RECEIVED/REPLIED/CLEARED` events to the coordinator's `/report` (stats at `/coordinator_stats`).

**Counting exercise (`modem.py`, `spammer1.py`)** uses its own ad-hoc packet format, not the `0xAE` protocol. A packet is a list of `"!4sH"` records (key_id, count). The first record is the sender's own sent-count. The rest are counts of packets received from each peer. Incoming records are appended to `messages.txt` as CSV lines `utime,reporter_hex,about_hex,count`. If every count in a packet is a multiple of 256, the script assumes the sender packed it little-endian and shifts the counts back.

## Gotchas

- `private_key.txt` is tracked in git and holds a real private key. Don't print it or copy its contents anywhere.
- `__pycache__/*.pyc` files are committed, and the repo has no `.gitignore`.
- The `.code-workspace` file points at a second folder outside the repo (`~/Downloads/lora_common/lora_common`), which is the upstream source of `lora_common/`.
- Serial port names (`COM20`) and the simulator IP are hardcoded in several scripts.
