import socket
import struct
import datetime
import typing


def crc16_teltonika(pData):
    crc16_result = 0x0000
    for i in range(len(pData)):
        val = pData[i]
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

    if rest_data == b'866897050116377' and len(rest_data) == length:
        response = 1
        conn.send(response.to_bytes(1, byteorder='big'))
        data_full = conn.recv(1024)
        crc_sum_raw = raw_data[-4:]
        avl_data_len = raw_data[4:8]
        # raw_data = b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'
        items = [int(item) for item in data_full]
        avl_data_raw = data_full[8:-4]
        if ((sum(items[:4]) != 0) or (
                crc16_teltonika(avl_data_raw) != int(str(crc_sum_raw.hex()), base=16)) or
                (len(avl_data_raw) != int(str(avl_data_len.hex()), base=16))):
            pass
        print(data_full)

    conn.close()


def decode_time(raw_date: int):
    date = datetime.datetime.fromtimestamp(raw_date/1e3)
    return date
#     b'\x00\x0f866897050116377'
# b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'


def decode_io_data(io_data: bytes):
    print(io_data)
    print(len(io_data))
    print(f'Event Id {io_data[0]}')
    print(f'Trackers Amount {io_data[1]}')

    one_byte_tracker_amount = io_data[2]
    print(f'One byte amount: {one_byte_tracker_amount}')
    end_one_byte = 3 + one_byte_tracker_amount * 2
    print(f'One byte end: {end_one_byte}')
    print('One byte trackers:')
    for i in range(3, end_one_byte, 2):
        print(i, i + 1)
        print(f'ID: {io_data[i]}, Value: {io_data[i + 1]}')

    two_bytes_count = io_data[end_one_byte]
    print(f'Two bytes count: {two_bytes_count}')
    two_byte_end = end_one_byte + io_data[end_one_byte] * 3 + 1
    print(f'Two bytes end: {two_byte_end}')
    print('Two byte trackers:')
    for i in range(end_one_byte + 1, two_byte_end, 3):
        print(i, range(i + 1, i + 3))
        print(f'ID: {io_data[i]}, Value: {struct.unpack(">H", io_data[i + 1: i + 3])[0]}')

    four_bytes_count = io_data[two_byte_end]
    print(f'Four byte count: {four_bytes_count}')
    end_four_bytes = two_byte_end + io_data[two_byte_end] * 5 + 1
    print(f'Four byte end: {end_four_bytes}')
    for i in range(two_byte_end + 1, end_four_bytes, 5):
        print(i, range(i + 1, i + 5))
        print(f'ID: {io_data[i]}, Value: {struct.unpack(">I", io_data[i + 1: i + 5])[0]}')

    eight_bytes_count = io_data[end_four_bytes]
    print(f'Eight bytes count: {eight_bytes_count}')
    end_eight_bytes = end_four_bytes + io_data[end_four_bytes] * 9 + 1
    print(f'Eight bytes end: {end_eight_bytes}')
    for i in range(end_four_bytes + 1, end_eight_bytes, 9):
        print(i, range(i + 1, i + 9))
        print(f'ID: {io_data[i]}, Value: {struct.unpack(">Q", io_data[i + 1: i + 9])[0]}')


if __name__ == '__main__':
    # main()
    raw_data = b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'
    items = [int(item) for item in raw_data]
    # print(f'Preamble: {raw_data[:4]}')
    # print(f'Preamble: {struct.unpack(">I", raw_data[:4])[0]}')
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
    decode_io_data(raw_data[34: -5])
    # two_byte_tracker_amount = raw_data[end_one_byte]
    # print(two_byte_tracker_amount)
    # end_two_bytes = (end_one_byte + 1) + two_byte_tracker_amount * 3
    # print(end_two_bytes)
    # for i in range(end_one_byte + 1, end_two_bytes, 3):
    #     print(f'ID: {raw_data[i]}, Value: {struct.unpack(">H", raw_data[i + 1: i + 3])[0]}')
    # four_byte_tracker_count = raw_data[45]
    # print(four_byte_tracker_count)
    # end_four_bytes = (end_two_bytes + 1) + four_byte_tracker_count * 5
    # print(end_four_bytes)
    # for i in range(end_two_bytes + 1, end_four_bytes, 5):
    #     print(f'ID: {raw_data[i]}, Value: {struct.unpack(">I", raw_data[i + 1: i + 5])[0]}')
    # eight_byte_amount = raw_data[51]
    # print(eight_byte_amount)


