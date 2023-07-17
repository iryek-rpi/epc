import threading
import socket
import logging

define LOG_FILE = '/home/ubuntu/epc/log.txt'

def setup_logger(log_file):
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)d] - %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

logger = setup_logger(LOG_FILE)

def encrypt(s, token):
    s2 = ''
    for i in range(len(s)):
        b1 = ord(s[i])
        b = b1 ^ token
        temp = chr(b)
        s2 += temp
    return s2

def decrypt(s, token):
    temp = bytearray(len(s))
    for i in range(len(s)):
        b = ord(s[i:i+1])
        b = b ^ token
        temp[i:i+1] = bytes([b])
    return temp.decode()

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def init_enc_server():
    try:
        enc_socket = socket.socket()
        enc_socket.bind(('0.0.0.0', 8503))
        enc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        enc_socket.listen(100)
    except Exception as e:
        enc_socket = None
        logger.info(e)
        return None
    else:
        while True:
            logger.info(" ")
            logger.info("Waiting for encrytion client connection...")
            conn, address = enc_socket.accept()  # accept new connection
            logger.info(f"Connected from: {address}. Waiting for plaintext...")

            data = conn.recv(1024)
            if not data:
                logger.info("암호화서버 중지됨 on receiving plaintext")
                break
            token = data[0]
            msg = data[1:]
            logger.info(f"data: {data} token: {token} msg: {msg} msg.decode():{msg.decode()}")
            cipher = encrypt(msg.decode(), token)
            logger.info(f'cipher: {cipher}')

            conn.send(cipher.encode())  # send data to the client
            conn.close()  # close the connection


def init_dec_server():
    try:
        dec_socket = socket.socket()
        dec_socket.bind(('0.0.0.0', 8504))
        dec_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        dec_socket.listen(100)
    except Exception as e:
        dec_socket = None
        logger.info(e)
        return None
    else:
        while True:
            logger.info("")
            logger.info("Waiting for decryption client connection...")
            conn, address = dec_socket.accept()
            logger.info(f"Connected from: {address}. Waiting for ciphertext...")

            data = conn.recv(1024)
            if not data:
                logger.info("복호화서버 중지됨 on receiving ciphertext")
                break
            token = data[0]
            msg = data[1:]
            logger.info(f"data: {data} token: {token} msg: {msg} msg.decode():{msg.decode()}")
            plaintext = decrypt(msg.decode(), token)
            logger.info(f'plaintext: {plaintext}')

            conn.send(plaintext.encode())  # send data to the client
            conn.close()  # close the connection

plaintext_thread = None
ciphertext_thread = None

if __name__ == "__main__":
    if plaintext_thread:
        plaintext_thread.stop()
        plaintext_thread.join()
        plaintext_thread = None

    plaintext_thread = StoppableThread(target=init_enc_server,args=())
    plaintext_thread.start()

    if ciphertext_thread:
        ciphertext_thread.stop()
        ciphertext_thread.join()
        ciphertext_thread = None

    ciphertext_thread = StoppableThread(target=init_dec_server,args=())
    ciphertext_thread.start()

    while True:
        pass
