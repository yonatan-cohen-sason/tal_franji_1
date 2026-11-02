import pubkey
import base64

# Public key of the receiver
pub64 = "vKJPCApGefea7+8AOG71NlUpuh/rAMQzQSxC3DHQEP/sQQHOrNRcoPi3YJqLqPF1FmKZnYSOIR4/Oo3G/7J6cPTkBHXMErJXofME3Pp8eMl639gLE/hF0QJPL+W1+TRDM6oGpcXOrKoIdsKB39B0kF2++DcFM6qcbaI5mBzYFCc="

# Convert Base64 to bytes
pub_key_bytes = base64.b64decode(pub64)

# Create public key object
pub_key = pubkey.RSA1024.from_public_bytes(pub_key_bytes)

# Encrypt message
message = "ValueError: Ciphertext too large"

message_bytes = pub_key.encrypt(message.encode("utf-8"))

# Convert to Base64
message64 = base64.b64encode(message_bytes).decode("utf-8")

print("message:" , message64)



# # Load private key
# with open("private_key.txt", "r") as f:
#     text = f.read()

# key = pubkey.RSA1024.from_private_text(text)

# # Encrypted message received
# text64 = "P+SzMcxUuGRp2VdaVvMbOi5utdqTGG+zjN1knQSAfW6dpt3BAkT5wQ8dCUsQTH9/sg8WsXFzDkwzw1z9lSWAbUzKCeFJ2sZ6PftBJqlUXVNyoT4v44/kNJtw6NsA7EhKWTTYIo6l2UXjij6wp6Y7KhAoFC7+U/j/czLg2EX3XDQ="

# # Convert Base64 to bytes
# message_bytes = base64.b64decode(text64)

# # Decrypt
# message_plain = key.decrypt(message_bytes).decode("utf-8")

# print(message_plain)