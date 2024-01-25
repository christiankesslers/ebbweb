import threading
import time
import hashlib
import logging
import socket
import random
import signal

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ProofOfWork:
    @staticmethod
    def find_nonce(index, previous_hash, timestamp, data):
        """
        Perform proof of work to find a suitable nonce for the given block data.
        """
        nonce = 0
        while ProofOfWork.calculate_hash(index, previous_hash, timestamp, data, nonce)[:4] != "0000":
            nonce += 1
        return nonce

    @staticmethod
    def calculate_hash(index, previous_hash, timestamp, data, nonce):
        block_string = f"{index}{previous_hash}{timestamp}{data}{nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce, peer_address):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.peer_address = peer_address
        self.hash = ProofOfWork.calculate_hash(index, previous_hash, timestamp, data, nonce)

class Blockchain:
    def __init__(self, port):
        self.chain = []
        self.lock = threading.Lock()
        self.peers = set()
        self.port = port
        self.stop_flag = threading.Event()

    def add_peer(self, peer_address):
        with self.lock:
            self.peers.add(peer_address)
            logger.info(f"Peer {peer_address} connected to the network.")

    def remove_peer(self, peer_address):
        with self.lock:
            self.peers.remove(peer_address)
            logger.info(f"Peer {peer_address} disconnected from the network.")

    def get_connected_peers(self):
        with self.lock:
            return list(self.peers)

    def add_block(self, data, peer_address):
        with self.lock:
            index = len(self.chain)
            previous_hash = self.chain[-1].hash if self.chain else "0"
            timestamp = time.time()
            nonce = ProofOfWork.find_nonce(index, previous_hash, timestamp, data)

            block = Block(index, previous_hash, timestamp, data, nonce, peer_address)
            self.chain.append(block)

            logger.info(f"Added Block {block.index} to the blockchain. Nonce: {block.nonce}")

    def run_node(self):
        try:
            self.add_peer((socket.gethostbyname(socket.gethostname()), self.port))

            while not self.stop_flag.is_set():
                data = "block_data"  # Replace with actual data
                self.add_block(data, (socket.gethostbyname(socket.gethostname()), self.port))
                try:
                    time.sleep(1.77)
                except KeyboardInterrupt:
                    pass  # Continue execution on KeyboardInterrupt
        finally:
            self.remove_peer((socket.gethostbyname(socket.gethostname()), self.port))

def simulate_main(num_initial_nodes=2):
    shared_data = "initial_data"
    port = 8888

    blockchain = Blockchain(port)

    # Start initial nodes
    for _ in range(num_initial_nodes):
        node_thread = threading.Thread(target=blockchain.run_node)
        node_thread.start()

    try:
        signal.signal(signal.SIGINT, lambda *_: None)
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        blockchain.stop_flag.set()
        time.sleep(2)  # Allow time for threads to finish

        # Print blockchain information
        for block in blockchain.chain:
            logger.info(f"Block {block.index}: {block.data}. Nonce: {block.nonce}")

        connected_peers = blockchain.get_connected_peers()
        logger.info(f"Connected Peers: {connected_peers}")

if __name__ == "__main__":
    simulate_main()
