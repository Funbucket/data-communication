import socket
import struct
import time

FLAGS = _ = None
DEBUG = False


def is_resending(prev, cur):
    return prev == cur


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
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))

            excepting = False
            i = 0

            sock.settimeout(FLAGS.timeout)
            while i < size:
                try:
                    chunk, server = sock.recvfrom(FLAGS.chunk_maxsize)
                    seq = struct.unpack('>B', chunk[:1])[0]
                    data = chunk[1:].decode('utf-8')
                    print(f'Received {data} from {server} with {seq}')

                    if i == 0:
                        cur_seq = seq
                        prev_seq = 1
                    else:
                        prev_seq = cur_seq
                        cur_seq = seq

                    if excepting:  # exception case 2
                        print("exception case 2...")
                        time.sleep(5)
                        excepting = False
                    else:
                        if prev_seq != cur_seq:
                            ack = (cur_seq+1)%2
                            chunk = struct.pack('>B', ack) + data.encode('utf-8')
                            sock.sendto(chunk, server)
                            i += 1

                except socket.timeout:  # handling exception case 1: resending ack
                    print("resending to handle exception case 1")
                    ack = (prev_seq+1)%2
                    chunk = struct.pack('>B', ack) + data.encode('utf-8')
                    sock.sendto(chunk, server)

            sock.settimeout(None)
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