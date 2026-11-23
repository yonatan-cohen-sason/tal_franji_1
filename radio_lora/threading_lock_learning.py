import threading
import time

transactions = []
worker_lock = threading.Lock()
def worker():
   global transactions
   for i in range(10000):
        with worker_lock:
            transactions.append(10)
            balance = sum(transactions)
            assert balance == 10 * len(transactions)

threads = []
for i in range(10):
   threads.append(threading.Thread(target=worker))

# Start each thread
for t in threads:
   t.start()

# Wait for all threads to finish
for t in threads:
   t.join()

