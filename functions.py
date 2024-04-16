import os
import json


def crc16_teltonika(p_data: bytes) -> int:
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


def put_data_to_json(io_data_d,  idx):
    filename = 'io_data.json'
    filedata = {}
    if filename in os.listdir():
        with open(filename, encoding='utf-8') as file:
            filedata = json.load(file)

    filedata[idx] = io_data_d

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(filedata, file)