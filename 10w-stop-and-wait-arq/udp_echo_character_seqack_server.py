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
            print(f'Received {data} from {client}')

            seq = 0
            i = 0
            excepting = True
            transferring = True

            sock.settimeout(FLAGS.timeout)

            while transferring:
                d = data[i]
                try:
                    if excepting:  # exception case 1: server -> client time expired
                        print("sleeping...")
                        excepting = False
                        time.sleep(5)
                    else:
                        if i == 0:  # send first data to client
                            chunk = struct.pack('>B', seq) + d.encode('utf-8')
                            sock.sendto(chunk, client)
                            print(f'Sending {d}... {seq}')
                        else:  # receive ack from client
                            chunk, client = sock.recvfrom(FLAGS.mtu)
                            ack = chunk[:1]
                            ack = struct.unpack('>B', ack)[0]
                            print(f"ACK from client: {ack}")
                            if ack == seq + 1:  # check if client ack equals with next seq
                                seq = (seq+1)%MAXSEQ
                except socket.timeout:
                    print("timeout...")
                if i == len(data):
                    transferring = False

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