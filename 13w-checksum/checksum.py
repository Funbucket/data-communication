if __name__ == "__main__":
    import struct

    byte_chunk = b'\x45\x00\x00\x73\x00\x00\x40\x00\x40\x11\xc0\xa8\x00\x01\xc0\xa8\x00\xc7'

    check = 0
    for i in range(0, len(byte_chunk), 2):
        d = byte_chunk[i:i + 2]
        d = d + b'\x00' * (2 - len(d))
        check = check + int.from_bytes(d, byteorder='big')
        print('Processed:', d.hex(), d, check)
    print('Total:', check, struct.pack('>I', check).hex())
