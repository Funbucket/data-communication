import socket
import struct
import time

FLAGS = _ = None
DEBUG = False


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f'Ready to send using {sock}')

    while True:
        try:
            data = input('Data: ').strip()
            request = f'{data}'
            size = len(request)
            i = 0
            transferring = True
            server = (FLAGS.address, FLAGS.port)
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            prev_seq = -1

            sock.settimeout(FLAGS.timeout)
            while transferring:
                try:
                    chunk = sock.recvfrom(FLAGS.chunk_maxsize)
                    print(chunk)
                    seq = struct.unpack('>B', chunk[:1])[0]
                    if prev_seq != seq:  # check if current req is not same with prev one
                        i += 1  # increase index
                        data = chunk[1:].decode('utf-8')
                        print(f'Received {data} from {server} with {seq}')
                        prev_seq = seq

                        # send ack to server
                        ack = (seq+1) % 2
                        chunk = struct.pack('>B', ack) + data.encode('utf-8')
                        sock.sendto(chunk, server)

                except socket.timeout:  # exception case 1 handling
                    # resend ack to server
                    print("resending ack to server")
                    ack = (prev_seq+1) % 2
                    chunk = struct.pack('>B', ack) + data.encode('utf-8')
                    sock.sendto(chunk, server)
                if i == size:
                    transferring = False

        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='localhost',
                        help='The address to send data')
    parser.add_argument('--port', type=int, default=38442,
                        help='The port to send data')
    parser.add_argument('--chunk_maxsize', type=int, default=2**16,
                        help='The recvfrom chunk max size')
    parser.add_argument('--timeout', type=int, default=3,
                        help='The timeout seconds')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
