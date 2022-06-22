import socket

FLAGS = _ = None
DEBUG = False


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {sock}')

    while True:
        data, client = sock.recvfrom(2**16)
        data = data.decode('utf-8')
        print(f'Received {data} from {client}')
        data = data.encode('utf-8')
        data = data[::-1]
        sock.sendto(data, client)
        print(f'Send {data} to {client}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='localhost',
                        help='The address to serve service')
    parser.add_argument('--port', type=int, default=38442,
                        help='The port to serve service')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
