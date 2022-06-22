import os
import socket
import struct
import time
import sys

FLAGS = _ = None
DEBUG = False

def get_filedict(rootpath):
    files = {}
    with os.scandir(rootpath) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                info = get_fileinfo(entry.path)
                info['path'] = entry.path
                files[entry.name] = info
    return files


def get_fileinfo(path):
    size = 0
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(FLAGS.mtu)
            chunk_size = len(chunk)
            if chunk_size == 0: # if not data:
                break
            size = size + chunk_size
    return {'size': size}


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    files = get_filedict(FLAGS.files)
    if DEBUG:
        print(f'Ready to file transfer')
        for key, value in files.items():
            print(f'{key}: {value}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {sock}')

    while True:
        try:
            data, client = sock.recvfrom(FLAGS.mtu)
            data = data.decode('utf-8')
            data = data.split(' ')

            if len(data) < 2:
                response = 'Error'
                sock.sendto(response.encode('utf-8'), client)
                continue

            command = data[0].upper()
            target = ' '.join(data[1:])
            print(f'{command} {target} from {client}')

            if target not in files.keys():
                print(f'{target} was not found (requested by {client})')
                response = '404 Not Found'
                sock.sendto(response.encode('utf-8'), client)
                continue

            info = files[target]
            path = info['path']
            size = info['size']
            remain = size
            length = int(size/FLAGS.data_size)
            seq = 0
            i = 0

            if command == 'INFO':
                size_b = str(size).encode('utf-8')
                sock.sendto(size_b, client)
            elif command == 'DOWNLOAD':
                with open(path, 'rb') as output:

                    sock.settimeout(FLAGS.timeout)
                    while i < length + 1:
                        data = output.read(FLAGS.data_size)
                        chunk = struct.pack('>B', seq) + data
                        sock.sendto(chunk, client)

                        data_size = len(data)
                        if data_size == 0:
                            break
                        remain = remain - data_size

                        print(f'Transferring to {client} with {seq}: {size-remain}/{size}')

                        ack_flag = False

                        while not ack_flag:
                            if FLAGS.exception1:  # exception case 1
                                print("exception case 1...")
                                time.sleep(5)
                                FLAGS.exception1 = False
                            else:
                                try:
                                    chunk, client = sock.recvfrom(FLAGS.mtu)
                                    ack = struct.unpack('>B', chunk[:1])[0]
                                    print(f"ACK from client: {ack}")
                                    next_seq = (seq+1)%MAXSEQ
                                    if ack == next_seq:
                                        seq = next_seq
                                        i += 1
                                        ack_flag = True
                                except socket.timeout:  # handling exception case 2
                                    print("resending to handle exception case 2...")
                                    sock.sendto(chunk, client)

                    sock.settimeout(None)

                    sock.settimeout(FLAGS.timeout*2)
                    try:
                        chunk, client = sock.recvfrom(FLAGS.mtu)
                    except socket.timeout:  # handling exception case 3
                        print(f'File transfer complete {target}')
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
    parser.add_argument('--address', type=str, default='0.0.0.0',
                        help='The address to serve service')
    parser.add_argument('--port', type=int, default=38442,
                        help='The port to serve service')
    parser.add_argument('--timeout', type=int, default=3,
                        help='The timeout seconds')
    parser.add_argument('--data_size', type=int, default=1379,
                        help='The maximum transmission unit')
    parser.add_argument('--mtu', type=int, default=1380,
                        help='The maximum transmission unit')
    parser.add_argument('--files', type=str, default='./files',
                        help='The file directory path')
    parser.add_argument('--exception1', type=bool, default=False,
                        help='The file directory path')
    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    FLAGS.files = os.path.abspath(os.path.expanduser(FLAGS.files))

    main()
