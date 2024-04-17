import socket
import selectors

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from decoder import Decoder
import models
import functions as func

engine = sa.create_engine('sqlite:///example.db')

models.Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

selector = selectors.DefaultSelector()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 1050
s.bind(('', port))

s.listen()
s.setblocking(False)

connections = []


def main():
    try:
        while True:
            try:
                conn, addr = s.accept()
                conn.setblocking(False)
                connections.append(conn)
            except BlockingIOError:
                pass

            for connection in connections:
                try:
                    data = connection.recv(1024)
                    enc_1, length = data[:2]
                    rest_data = data[2:]

                    response = 1 if len(rest_data) == length else 0
                    connection.send(response.to_bytes(1, byteorder='big'))
                except BlockingIOError:
                    pass

                if response:
                    try:
                        data_full = connection.recv(1024)
                        print(data_full)
                    except BlockingIOError:
                        pass

                    try:
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

                            _, idx, io_dict = Decoder.decode_io_data(data_full[current_byte:])
                            current_byte += idx
                            full_record = (record, io_dict)
                            records.append(full_record)

                        connection.send(len(records).to_bytes(1, byteorder='big'))
                    except BlockingIOError:
                        pass

                    imei = rest_data.decode('ascii')
                    func.put_data_to_storage(records, imei)
    finally:
        s.close()


if __name__ == '__main__':
    main()
