import socket
import struct

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from decoder import Decoder
import models
import functions as func

engine = sa.create_engine('sqlite:///example.db')

models.Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 1050
    s.bind(('', port))

    s.listen(1)
    conn, addr = s.accept()

    data = conn.recv(1024)
    enc_1, length = data[:2]
    rest_data = data[2:]

    response = 1 if len(rest_data) == length else 0
    conn.send(response.to_bytes(1, byteorder='big'))
    imei = rest_data.decode('ascii')
    while response:
        data_full = conn.recv(1024)
        print(data_full)

        crc_sum_raw = data_full[-4:]
        avl_data_len = data_full[4:8]
        items = [int(item) for item in data_full]
        avl_data_raw = data_full[8:-4]
        if ((sum(items[:4]) != 0) or (
                func.crc16_teltonika(avl_data_raw) != int(str(crc_sum_raw.hex()), base=16)) or
                (len(avl_data_raw) != int(str(avl_data_len.hex()), base=16))):
            break
        codec = data_full[8]
        records_count = data_full[9]
        current_byte = 10
        records = []
        for packet in range(0, records_count):
            record = Decoder.decode_record(data_full[current_byte: current_byte + 24])
            current_byte += 24

            _, idx, io_dict = data_full[current_byte:]
            current_byte += idx
            full_record = (record, io_dict)
            records.append(full_record)

        for record in records:
            gps_data, io_data = record
            print(session.query(models.Machine).all())

            response = session.query(models.Machine.imei).filter(models.Machine.imei == imei)
            if response is False:
                imei_test = models.Machine(imei=imei)
                session.add(imei_test)

            rec_base = models.Record(*gps_data, machine_id=imei)
            session.add(rec_base)

            session.commit()
            func.put_data_to_json(io_data, rec_base.id)

    conn.close()

#     b'\x00\x0f866897050116377'


if __name__ == '__main__':
    # main()
    # raw_data_1 = b'\x00\x00\x00\x00\x00\x00\x006\x08\x01\x00\x00\x01k@\xd8\xea0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x02\x15\x03\x01\x01\x01B^\x0f\x01\xf1\x00\x00`\x1a\x01N\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\xc7\xcf'
    # raw_data_2 = b'\x00\x00\x00\x00\x00\x00\x00E\x08\x01\x00\x00\x01\x8e\xe5\xc4X\x90\x00\x14\x95j.\x1d\x89\xf1[\x00\x8e\x00\x00\x0c\x00\x00\x00\x0f\t\x05\x00\x06\x00\x01\x00\x15\x05\xcf\x00E\x07f\xb3\xd0\x0c\xd1\x00\x06B\rWC\r.p\x00\x00d\x00\x00q\x00\x00e\x00\x00\x00\x00\x01\x00\x00K\xbb'
    # io_data_1, idx, test_d = Decoder.decode_io_data(raw_data_2[34:])
    # io_data_2, idx = Decoder.decode_io_data(raw_data_2[34:])
    # print(idx)
    # record_1 = Decoder.decode_record(raw_data_2[10:34])
    # print(record_1)
    # func.put_data_to_json(test_d, 3)
    # models.Base.metadata.create_all(bind=engine)
    #
    # Session = sessionmaker(bind=engine)
    # session = Session()
    #
    # record_test = models.Record(*record_1)
    # session.add(record_test)
    # session.commit()
    pass