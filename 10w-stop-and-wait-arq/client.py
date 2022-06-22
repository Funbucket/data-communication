import socket
import struct
import sys
import time

FLAGS = _ = None
DEBUG = False
MAXSEQ = 2


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f'Ready to send using {sock}')
    while True:
        try:
            filename = input('Filename: ').strip()
            request = f'INFO {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))

            response, server = sock.recvfrom(FLAGS.mtu)
            response = response.decode('utf-8')
            if response == '404 Not Found':
                print(response)
                continue

            size = int(response)
            print(f"file size in bytes: {size}")

            print(f"length{int(size/1379)}")

            length = int(size/FLAGS.data_size)
            stime = time.time()  # start counting time
            request = f'DOWNLOAD {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            print(f'Request {filename} to ({FLAGS.address}, {FLAGS.port})')

            i = 0
            remain = size

            with open(filename, 'wb') as f:
                sock.settimeout(FLAGS.timeout)
                while i < length + 1:
                    try:
                        chunk, server = sock.recvfrom(FLAGS.mtu)
                        seq = struct.unpack('>B', chunk[:1])[0]
                        data = chunk[1:]
                        byte_chunk = chunk[1:]
                        print(byte_chunk[:2].hex())

                        data_size = len(data)
                        if data_size == 0:
                            break

                        if i == 0:
                            cur_seq = seq
                            prev_seq = 1
                        else:
                            prev_seq = cur_seq
                            cur_seq = seq

                        if FLAGS.exception2:  # exception case 2
                            print("exception case 2...")
                            time.sleep(5)
                            FLAGS.exception2 = False
                        else:
                            if prev_seq != cur_seq:
                                ack = (cur_seq + 1) % MAXSEQ
                                chunk = struct.pack('>B', ack) + data
                                sock.sendto(chunk, server)
                                i += 1
                                f.write(data)
                                remain = remain - data_size

                                print(f'Receiving from {server} with {cur_seq}: {size - remain}/{size}')
                                if remain == 0:
                                    etime = time.time()  # end time
                                    print(f'> Throughput: {round((data_size * 8 * 2) / (etime - stime)):,d} bps')
                                    print(f'File download success')

                    except socket.timeout:  # handling exception case 1: resending ack
                        print("resending to handle exception case 1")
                        ack = (prev_seq + 1) % MAXSEQ
                        chunk = struct.pack('>B', ack) + data
                        sock.sendto(chunk, server)

                    if DEBUG:
                        print(f'Receiving from {server}: {size-remain}/{size}')

                sock.settimeout(None)

                sock.settimeout(FLAGS.timeout * 2)
                try:
                    chunk, server = sock.recvfrom(FLAGS.mtu)
                except socket.timeout:  # handling exception case 4
                    sys.exit()
                sock.settimeout(None)

        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='127.0.0.1',
                        help='The address to send data')
    parser.add_argument('--port', type=int, default=38442,
                        help='The port to send data')
    parser.add_argument('--mtu', type=int, default=1380,
                        help='The maximum transmission unit')
    parser.add_argument('--data_size', type=int, default=1379,
                        help='The maximum transmission unit')
    parser.add_argument('--timeout', type=int, default=5,
                        help='The timeout seconds')
    parser.add_argument('--exception2', type=bool, default=False,
                        help='The timeout seconds')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()

