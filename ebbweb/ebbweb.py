import threading
import time
import hashlib
import logging
import socket
import random
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - 
%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash_value, 
nonce, peer_address):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash_value
        self.nonce = nonce
        self.peer_address = peer_address

class Blockchain:
    def __init__(self, port):
        self.chain = []
        self.lock = threading.Lock()
        self.peers = set()
        self.port = port
        self.last_block_time = time.time()
        self.nonce = 0  # Nonce for ordering blocks
        self.db_path = "chain_data/chain_data.db"

        self.create_database()

    def create_database(self):
        os.makedirs("chain_data", exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index INTEGER,
                previous_hash TEXT,
                timestamp REAL,
                data TEXT,
                hash TEXT,
                nonce INTEGER,
                peer_address TEXT
            )
        ''')
        connection.commit()
        connection.close()

    def add_peer(self, peer_address):
        with self.lock:
            self.peers.add(peer_address)
            logger.info(f"Peer {peer_address} connected to the network.")

    def remove_peer(self, peer_address):
        with self.lock:
            self.peers.remove(peer_address)
            logger.info(f"Peer {peer_address} disconnected from the 
network.")

    def get_connected_peers(self):
        with self.lock:
            return list(self.peers)

    def add_block(self, data, peer_address):
        with self.lock:
            index = len(self.chain)
            previous_hash = self.chain[-1].hash if self.chain else "0"
            timestamp = time.time()
            nonce = self.nonce
            hash_value = self.calculate_hash(index, previous_hash, 
timestamp, data, nonce)

            block = Block(index, previous_hash, timestamp, data, 
hash_value, nonce, peer_address)
            self.chain.append(block)

            logger.info(f"Added Block {block.index} to the blockchain. 
Nonce: {block.nonce}")
            self.last_block_time = time.time()  # Update the last block 
time
            self.nonce += 1  # Increment nonce for ordering

            # Record block in SQLite database
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO blocks (index, previous_hash, timestamp, data, 
hash, nonce, peer_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (block.index, block.previous_hash, block.timestamp, 
block.data, block.hash, block.nonce, block.peer_address))
            connection.commit()
            connection.close()

    def calculate_hash(self, index, previous_hash, timestamp, data, 
nonce):
        block_string = f"{index}{previous_hash}{timestamp}{data}{nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class EbbNode:
    def __init__(self, initial_data, blockchain, stop_flag, port):
        self.data = initial_data
        self.blockchain = blockchain
        self.stop_flag = stop_flag
        self.port = port

    def process_data(self):
        self.data += "_processed"
        self.blockchain.add_block(self.data, 
(socket.gethostbyname(socket.gethostname()), self.port))

    def run(self):
        try:
            
self.blockchain.add_peer((socket.gethostbyname(socket.gethostname()), 
self.port))

            while not self.stop_flag.is_set():
                self.process_data()
                time.sleep(1.11)
        finally:
            
self.blockchain.remove_peer((socket.gethostbyname(socket.gethostname()), 
self.port))

def process_data_and_add_block(node):
    try:
        node.process_data()
    finally:
        
blockchain.remove_peer((socket.gethostbyname(socket.gethostname()), 
node.port))

def main():
    shared_data = "initial_data"
    stop_flag = threading.Event()
    port = 8888

    blockchain = Blockchain(port)

    random_md5 = hashlib.md5(str(random.random()).encode()).hexdigest()
    current_time = int(time.time())
    public_address = hashlib.md5((random_md5 + str(current_time / 
52494)).encode()).hexdigest()

    logger.info(f"You are now connected to the blockchain and your public 
address is {public_address}!")

    with ThreadPoolExecutor(max_workers=2) as executor:
        node1 = EbbNode(shared_data, blockchain, stop_flag, port)
        thread1 = threading.Thread(target=executor.submit, 
args=(process_data_and_add_block, node1))
        thread1.start()

        time.sleep(2)

        node2 = EbbNode(shared_data, blockchain, stop_flag, port)
        thread2 = threading.Thread(target=executor.submit, 
args=(process_data_and_add_block, node2))
        thread2.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_flag.set()

    thread1.join()
    thread2.join()

    with blockchain.lock:
        for block in blockchain.chain:
            logger.info(f"Block {block.index}: {block.data}. Nonce: 
{block.nonce}")

    connected_peers = blockchain.get_connected_peers()
    logger.info(f"Connected Peers: {connected_peers}")

    md5_key = 
hashlib.md5(socket.gethostbyname(socket.gethostname()).encode()).hexdigest()
    logger.info(f"MD5 Key: {md5_key}")

if __name__ == "__main__":
    main()

