import socket
import struct
import time

FLAGS = _ = None
DEBUG = False
MAXSEQ = 2


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {sock}')

    while True:
        try:
            data, client = sock.recvfrom(FLAGS.mtu)
            data = data.decode('utf-8')
            size = len(data)
            print(f'Received {data} from {client}')

            seq = 0
            i = 0
            excepting = False

            sock.settimeout(FLAGS.timeout)
            while i < size:
                d = data[i]
                chunk = struct.pack('>B', seq) + d.encode('utf-8')
                sock.sendto(chunk, client)
                print(f'Sending {d}... {seq}')

                ack_flag = False

                while not ack_flag:
                    if excepting:  # exception case 1
                        print("exception case 1...")
                        time.sleep(5)
                        excepting = False
                    else:
                        try:
                            chunk, client = sock.recvfrom(FLAGS.mtu)
                            ack = struct.unpack('>B', chunk[:1])[0]
                            print(f"ACK from client: {ack}")
                            next_seq = (seq+1)%MAXSEQ
                            if ack == next_seq:  # check if ack equals with next seq
                                seq = next_seq
                                i += 1
                                ack_flag = True


                        except socket.timeout:  # handling exception case 2
                            print("resending to handle exception case 2...")
                            sock.sendto(chunk, client)

            print(f'Send {data} to {client}')
            sock.settimeout(None)
        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='0.0.0.0',
                        help='The address to serve service')
    parser.add_argument('--port', type=int, default=38442,
                        help='The port to serve service')
    parser.add_argument('--mtu', type=int, default=1400,
                        help='The maximum transmission unit')
    parser.add_argument('--timeout', type=int, default=3,
                        help='The timeout seconds')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()


