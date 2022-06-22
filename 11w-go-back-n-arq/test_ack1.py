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

    def test_ack1(self):
        ack = 1
        self.sock.sendto(struct.pack('>B', ack), (ADDRESS, PORT))
        try:
            chunk, server = self.sock.recvfrom(1380)
            byte_seq = chunk[:1]
            self.assertEqual(byte_seq.hex(), '01')
        except socket.timeout:
            self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()

