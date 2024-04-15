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
        # raw_data = b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'
        items = [int(item) for item in data_full]
        avl_data_raw = data_full[8:-4]
        if ((all(items[:4]) is not False) or (
                crc16_teltonika(avl_data_raw) != int(str(crc_sum_raw.hex()), base=16)) or
                (len(avl_data_raw) != int(str(avl_data_len.hex()), base=16))):
            pass
        print(data_full)

    conn.close()


def decode_time(raw_date: typing.Tuple[int]):
    date = datetime.datetime.fromtimestamp(raw_date)
    print(date)

#     b'\x00\x0f866897050116377'
# b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'


if __name__ == '__main__':
    # main()
    raw_data = b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'
    items = [int(item) for item in raw_data]
    crc_sum = items[-4:]
    crc_sum_raw = raw_data[-4:]
    avl_data = items[10:-5]
    avl_data_raw = raw_data[8:-4]
    avl_data_len = raw_data[4:8]
    print(avl_data_len)
    records_count = items[9]

    print(all(items[:4]) is False)
    print(items)

    print(crc16_teltonika(avl_data_raw))
    print(int(str(crc_sum_raw.hex()), base=16))
    print(int(str(avl_data_len.hex()), base=16))

    date_raw = avl_data_raw[2:8]
    date = struct.unpack('>HHH', date_raw)
    print(type(date))
    decode_time(date)
