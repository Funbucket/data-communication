import time
import socket
import struct
import unittest

FLAGS = _ = None
DEBUG = False
ADDRESS = '127.0.0.1'
PORT = 38442


class TestGoBackNServer(unittest.TestCase):
    def setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        request = f'INFO unittest'
        self.sock.sendto(request.encode('utf-8'), (ADDRESS, PORT))
        request = f'DOWNLOAD unittest'
        self.sock.sendto(request.encode('utf-8'), (ADDRESS, PORT))
        self.sock.settimeout(0.5)
        while True:
            try:
                self.sock.recvfrom(1380)
            except socket.timeout:
                break
        self.sock.settimeout(3*2)

    def tearDown(self):
        ack = 0
        while True:
            try:
                chunk, server = self.sock.recvfrom(1380)
                byte_seq = chunk[:1]
                ack = struct.unpack('<B', byte_seq)[0]
                ack = (ack+1)%16
                self.sock.sendto(struct.pack('>B', ack), (ADDRESS, PORT))
            except socket.timeout:
                break
        self.sock.close()

    def test_loop1(self):
        ack = 15
        self.sock.sendto(struct.pack('>B', ack), (ADDRESS, PORT))
        ack = 4
        self.sock.sendto(struct.pack('>B', ack), (ADDRESS, PORT))
        self.sock.settimeout(1)
        while True:
            try:
                chunk, server = self.sock.recvfrom(1380)
            except socket.timeout:
                self.sock.settimeout(3*2)
                break
        ack = 2
        self.sock.sendto(struct.pack('>B', ack), (ADDRESS, PORT))
        while True:
            try:
                chunk, server = self.sock.recvfrom(1380)
                byte_seq = chunk[:1]
                byte_chunk = chunk[1:]
                if struct.unpack('>B', byte_seq)[0] != 2:
                    ack = 2
                    self.sock.sendto(struct.pack('>B', ack), (ADDRESS, PORT))
                else:
                    break
            except socket.timeout:
                ack = 2
                self.sock.sendto(struct.pack('>B', ack), (ADDRESS, PORT))
        self.assertEqual(byte_chunk[:2].hex(), '1212')


if __name__ == '__main__':
    unittest.main()

