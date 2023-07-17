import time
import socket

IP = "146.56.151.119"

def init_connection(port):
  try:
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.connect((IP, port))
  except socket.error:
    _socket.close()
    print(f"Error connecting {IP}:{port}")
    return None

  return _socket

def make_msg(s:str, token:bytearray) -> bytearray:
  return token + s.encode()

def request_transform(s:str, token:bytearray, crypto_socket:socket.socket, port:int) -> str:
    if not crypto_socket:
        crypto_socket = init_connection(port)
        if not crypto_socket:
            return

    msg = make_msg(s, token)
    crypto_socket.send(msg)
    received = crypto_socket.recv(1024)
    return received.decode()

if __name__ == "__main__":
  enc_socket = None
  dec_socket = None
  while True:
    token = input(f"\n{'- '*30}\nPlease input a token(1 byte): ")
    token = token.encode()[:1]
    s = input("Please input a plain text: ")

    cipher = request_transform(s, token, enc_socket, 8503)
    print(f'ciphertext received: {cipher}')

    plain = request_transform(cipher, token, dec_socket, 8504)
    print(f'plaintext received: {plain}')

