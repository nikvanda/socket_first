import socket
import struct
import datetime
import typing
from decoder import Decoder

def crc16_teltonika(p_data: bytes):
    crc16_result = 0x0000
    for i in range(len(p_data)):
        val = p_data[i]
        crc16_result ^= val
        for j in range(8):
            if crc16_result & 0x0001:
                crc16_result = (crc16_result >> 1) ^ 0xA001
            else:
                crc16_result >>= 1
    return crc16_result


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 1050
    s.bind(('', port))

    s.listen(1)
    conn, addr = s.accept()

    data = conn.recv(1024)
    enc_1, length = data[:2]
    rest_data = data[2:]

    if len(rest_data) == length:
        response = 1
        conn.send(response.to_bytes(1, byteorder='big'))
        data_full = conn.recv(1024)
        print(data_full)
        crc_sum_raw = data_full[-4:]
        avl_data_len = data_full[4:8]
        items = [int(item) for item in data_full]
        avl_data_raw = data_full[8:-4]
        if ((sum(items[:4]) != 0) or (
                crc16_teltonika(avl_data_raw) != int(str(crc_sum_raw.hex()), base=16)) or
                (len(avl_data_raw) != int(str(avl_data_len.hex()), base=16))):
            pass

    conn.close()


def decode_time(raw_date: int):
    date = datetime.datetime.fromtimestamp(raw_date/1e3)
    return date
#     b'\x00\x0f866897050116377'
# b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'
# new data b'\x00\x00\x00\x00\x00\x00\x00E\x08\x01\x00\x00\x01\x8e\xe5\xc4X\x90\x00\x14\x95j.\x1d\x89\xf1[\x00\x8e\x00\x00\x0c\x00\x00\x00\x0f\t\x05\x00\x06\x00\x01\x00\x15\x05\xcf\x00E\x07f\xb3\xd0\x0c\xd1\x00\x06B\rWC\r.p\x00\x00d\x00\x00q\x00\x00e\x00\x00\x00\x00\x01\x00\x00K\xbb'


def decode_io_data(io_data: bytes) -> typing.List[int]:
    tracker_length = 2, 3, 5, 9
    byte_type = 'B', 'H', 'I', 'Q'
    io_data_dec = [io_data[0], io_data[1]]

    current_byte_idx = 2
    current_byte_type_idx = 0
    for i in tracker_length:
        amount = io_data[current_byte_idx]
        io_data_dec.append(amount)
        current_byte_idx += 1
        print(f'{i - 1} byte trackers amount: {amount}')
        end_tracker = current_byte_idx + amount * i
        for y in range(current_byte_idx, end_tracker, i):
            if i == 2:
                print(y, y + 1)
                print(f'ID: {io_data[y]},'
                      f' Value: {io_data[y + 1]}')
                io_data_dec.extend([io_data[y], io_data[y + 1]])
            else:
                print(y, range(y + 1, y + i))
                print(f'ID: {io_data[y]},'
                      f' Value: {struct.unpack(f">{byte_type[current_byte_type_idx]}", io_data[y + 1: y + i])[0]}')
                io_data_dec.extend([io_data[y],
                                        struct.unpack(f">{byte_type[current_byte_type_idx]}", io_data[y + 1: y + i])[0]])

        current_byte_type_idx += 1
        current_byte_idx = end_tracker

    return io_data_dec


if __name__ == '__main__':
    # main()
    raw_data = b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'
    # raw_data = b'\x00\x00\x00\x00\x00\x00\x00E\x08\x01\x00\x00\x01\x8e\xe5\xc4X\x90\x00\x14\x95j.\x1d\x89\xf1[\x00\x8e\x00\x00\x0c\x00\x00\x00\x0f\t\x05\x00\x06\x00\x01\x00\x15\x05\xcf\x00E\x07f\xb3\xd0\x0c\xd1\x00\x06B\rWC\r.p\x00\x00d\x00\x00q\x00\x00e\x00\x00\x00\x00\x01\x00\x00K\xbb'
    # items = [int(item) for item in raw_data]
    # print(raw_data[4:8])  # datalen
    # print(struct.unpack('>I', raw_data[4:8])[0])
    # print(raw_data[8])  # codec
    # print(raw_data[9])  # packets amount
    # print(raw_data[10:18])  # timestamp
    # print(struct.unpack('>Q', raw_data[10:18])[0])
    # print(decode_time(*struct.unpack('>Q', raw_data[10:18])))
    # print(raw_data[18])  # priority
    # print(struct.unpack('>I', raw_data[19:23]))  # longitude
    # print(struct.unpack('>I', raw_data[23:27]))  # latitude
    # print(struct.unpack('>H', raw_data[27:29]))  # height
    # print(struct.unpack('>H', raw_data[29:31]))  # azimuth
    # print(raw_data[31])     # satellite amount
    # print(struct.unpack('>H', raw_data[32:34]))  # speed
    # io_data_decoded = decode_io_data(raw_data[34: -5])
    print(Decoder.decode_record(raw_data[8:34]).date)
