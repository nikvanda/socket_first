import asyncio
import socket

import functions as func
from decoder import Decoder


async def listen_for_connection(server_socket: socket.socket, loop: asyncio.AbstractEventLoop) -> None:
    while True:
        print('Wait fo connection!')
        connection, address = await loop.sock_accept(server_socket)
        print('Got one')
        connection.setblocking(False)
        asyncio.create_task(decode_data(connection, loop))


async def decode_data(connection: socket.socket, loop: asyncio.AbstractEventLoop) -> None:
    while data := await loop.sock_recv(connection, 1024):
        enc_1, length = data[:2]
        rest_data = data[2:]
        response = 1 if len(rest_data) == length else 0
        await loop.sock_sendall(connection, response.to_bytes(1, byteorder='big'))

        while data_encoded := await loop.sock_recv(connection, 1024):
            crc_sum_raw = data_encoded[-4:]
            avl_data_len = data_encoded[4:8]
            items = [int(item) for item in data_encoded]
            avl_data_raw = data_encoded[8:-4]
            if ((sum(items[:4]) != 0) or (
                    func.crc16_teltonika(avl_data_raw) != int(str(crc_sum_raw.hex()), base=16)) or
                    (len(avl_data_raw) != int(str(avl_data_len.hex()), base=16))):
                break
            codec = data_encoded[8]
            records_count = data_encoded[9]
            current_byte = 10
            records = []
            for packet in range(0, records_count):
                record = Decoder.decode_record(data_encoded[current_byte: current_byte + 24])
                current_byte += 24

                _, idx, io_dict = Decoder.decode_io_data(data_encoded[current_byte:])
                current_byte += idx
                full_record = (record, io_dict)
                records.append(full_record)

            await loop.sock_sendall(connection, len(records).to_bytes(1, byteorder='big'))
            imei = rest_data.decode('ascii')
            func.put_data_to_storage(records, imei)


async def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 1051
    s.bind(('', port))
    s.setblocking(False)
    s.listen()

    await listen_for_connection(s, asyncio.get_event_loop())

if __name__ == '__main__':
    asyncio.run(main())
