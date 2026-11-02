import pubkey
import base64

# Public key of the receiver
pub64 = "tD8az7ip4clY3wAZevQYmgT/HmHBlRfS4Gm0r3Q2cwu8Oh4SxC0yr84BnYmiqY/gVqkkaLuIdKX+WaPvYgplIIu49PipU+gbLZwfQ3WipiaAb9p1Bi0nJfAJ5ooASNSEEQ2rJiLeT7ZxH2Pxqd0qY/2qxy6Coddaqo0N+RDQecs="

# Convert Base64 to bytes
pub_key_bytes = base64.b64decode(pub64)

# Create public key object
pub_key = pubkey.RSA1024.from_public_bytes(pub_key_bytes)

# Encrypt message
message = "dear tal keinan: i think its not allowed to be so handsome you are very sexy and i know you vote only to big yahu "

message_bytes = pub_key.encrypt(message.encode("utf-8"))

# Convert to Base64
message64 = base64.b64encode(message_bytes).decode("utf-8")

print("message:" , message64)



# # Load private key
# with open("private_key.txt", "r") as f:
#     text = f.read()

# key = pubkey.RSA1024.from_private_text(text)

# # Encrypted message received
# text64 = "m5x9une7ylPs5awdV0GMMKP5eH8q1LM3MgsAE0RjXuFohS9Q/QwhUzY2ehbBIhPLWBe7JfreNGJ15ExuQAkpamQqMagjxQaXmz4iv+UYL+rD+wRk0ob0n0oRlRnU2n3PNWG61ie5jn+o3mWuuAGRIl99/ahJHssSAJfF99Un63k="

# # Convert Base64 to bytes
# message_bytes = base64.b64decode(text64)

# # Decrypt
# message_plain = key.decrypt(message_bytes).decode("utf-8")

# print(message_plain)