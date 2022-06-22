import socket
import struct
import sys
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
            stime = time.time()  # start counting time
            request = f'DOWNLOAD {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            print(f'Request {filename} to ({FLAGS.address}, {FLAGS.port})')

            remain = size
            resending = False
            communicating = True

            with open(filename, 'wb') as f:
                expected_seq = 0
                while communicating:
                    sock.settimeout(FLAGS.timeout)
                    while True:
                        try:
                            if not resending:
                                chunk, server = sock.recvfrom(FLAGS.mtu)
                                byte_seq = chunk[:1]
                                seq = struct.unpack('<B', byte_seq)[0]
                                ack = (seq + 1) % 2 ** FLAGS.msb
                                data = chunk[1:]
                                data_size = len(data)

                                if seq == expected_seq:
                                    remain = remain - data_size
                                    print(f'Receiving from {server} with {seq}: {size - remain}/{size}')
                                    expected_seq = (expected_seq + 1) % (2**FLAGS.msb)
                                    sock.sendto(struct.pack('>B', ack), server)
                                    print(f'Send ack {ack}')
                                    f.write(data)

                                    if remain == 0:  # 성공적으로 다운로드시 통신 종료
                                        etime = time.time()  # end time
                                        print(f'> Throughput: {round((data_size * 8 * 2) / (etime - stime)):,d} bps')
                                        print(f'File download success')
                                        communicating = False
                                        break
                                else:
                                    sock.sendto(struct.pack('>B', expected_seq), server)
                                    print(f'Receiving from {server} with {seq}')
                                    print(f'Send ack {expected_seq}')
                            else:  # resending case
                                sock.sendto(struct.pack('>B', expected_seq), server)
                                print(f'Resend ack {expected_seq}')
                                resending = False
                        except socket.timeout:
                            resending = True

                sys.exit()

        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='13.209.49.183',
                        help='The address to send data')
    parser.add_argument('--port', type=int, default=38442,
                        help='The port to send data')
    parser.add_argument('--mtu', type=int, default=1380,
                        help='The maximum transmission unit')
    parser.add_argument('--timeout', type=int, default=3,
                        help='The timeout seconds')
    parser.add_argument('--msb', type=str, default=4,
                        help='The maximum sequence bit')
    parser.add_argument('--exception2', type=bool, default=False,
                        help='The timeout seconds')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()

