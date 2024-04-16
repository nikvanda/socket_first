import collections as clt
import datetime as dt
import struct

Record = clt.namedtuple('Record', ('codec', 'packets_amount', 'date',
                                   'priority', 'longitude', 'latitude',
                                   'height', 'azimuth', 'satellite_amount', 'speed'))


class Decoder:
    @staticmethod
    def decode_record(record_raw_data: bytes) -> Record:
        codec = record_raw_data[0]
        packets_amount = record_raw_data[1]
        timestamp = (dt.
                     datetime.
                     fromtimestamp(struct.unpack('>Q', record_raw_data[2:10])[0] / 1e3))
        priority = record_raw_data[10]
        longitude = struct.unpack('>I', record_raw_data[11:15])[0]
        latitude = struct.unpack('>I', record_raw_data[15:19])[0]
        height = struct.unpack('>H', record_raw_data[19:21])[0]
        azimuth = struct.unpack('>H', record_raw_data[21:23])[0]
        satellite_amount = record_raw_data[23]
        speed = struct.unpack('>H', record_raw_data[24:26])[0]

        record = Record(codec, packets_amount, timestamp,
                        priority, longitude, latitude,
                        height, azimuth, satellite_amount, speed)

        return record
