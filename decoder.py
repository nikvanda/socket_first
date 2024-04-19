import collections as clt
import datetime as dt
import typing as tp
import struct

Record = clt.namedtuple('Record', ('date', 'priority', 'longitude', 'latitude',
                                   'height', 'azimuth', 'satellite_amount', 'speed'))


class Decoder:
    @staticmethod
    def decode_record(record_raw_data: bytes) -> Record:
        timestamp = (dt.
                     datetime.
                     fromtimestamp(struct.unpack('>Q', record_raw_data[:8])[0] / 1e3))
        priority = record_raw_data[8]
        longitude = struct.unpack('>I', record_raw_data[9:13])[0]
        latitude = struct.unpack('>I', record_raw_data[13:17])[0]
        height = struct.unpack('>H', record_raw_data[17:19])[0]
        azimuth = struct.unpack('>H', record_raw_data[19:21])[0]
        satellite_amount = record_raw_data[21]
        print(f'satellite_amount {satellite_amount}')
        print(f'longitude {longitude}')
        print(f'latitude {latitude}')
        speed = struct.unpack('>H', record_raw_data[22:24])[0]

        record = Record(timestamp, priority, longitude, latitude,
                        height, azimuth, satellite_amount, speed)

        return record

    @staticmethod
    def decode_io_data(io_data: bytes) -> tp.Tuple[tp.List[int], int, tp.Dict[str, int]]:
        tracker_length = 2, 3, 5, 9
        byte_type = 'B', 'H', 'I', 'Q'
        io_data_dec = [io_data[0], io_data[1]]

        current_byte_idx = 2
        current_byte_type_idx = 0
        io_data_dict = {'Event_io': io_data[0], 'Total_amount_io': io_data[1]}
        for i in tracker_length:
            amount = io_data[current_byte_idx]
            io_data_dec.append(amount)
            current_byte_idx += 1

            print(f'{i - 1} byte trackers amount: {amount}')
            io_data_dict[f'{i - 1}_trackers_amount'] = amount

            end_tracker = current_byte_idx + amount * i
            trackers = {}

            for y in range(current_byte_idx, end_tracker, i):
                if i == 2:
                    print(y, y + 1)
                    print(f'ID: {io_data[y]},'
                          f' Value: {io_data[y + 1]}')
                    trackers[io_data[y]] = io_data[y + 1]
                    io_data_dec.extend([io_data[y], io_data[y + 1]])
                else:
                    print(y, range(y + 1, y + i))
                    print(f'ID: {io_data[y]},'
                          f' Value: {struct.unpack(f">{byte_type[current_byte_type_idx]}", io_data[y + 1: y + i])[0]}')
                    trackers[io_data[y]] = struct.unpack(f">{byte_type[current_byte_type_idx]}", io_data[y + 1: y + i])[0]
                    io_data_dec.extend([io_data[y],
                                        struct.unpack(f">{byte_type[current_byte_type_idx]}", io_data[y + 1: y + i])[
                                            0]])

            current_byte_type_idx += 1
            current_byte_idx = end_tracker
            io_data_dict[f'{i-1}_trackers'] = trackers

        return io_data_dec, current_byte_idx, io_data_dict
