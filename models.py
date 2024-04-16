import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Record(Base):
    __tablename__ = 'record'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    # tracker_imei = sa.Column(sa.Integer)
    date = sa.Column(sa.DateTime)
    priority = sa.Column(sa.Boolean)
    longitude = sa.Column(sa.Float)
    latitude = sa.Column(sa.Float)
    height = sa.Column(sa.Float)
    azimuth = sa.Column(sa.Float)
    satellite_amount = sa.Column(sa.Integer)
    speed = sa.Column(sa.Float)

    def __init__(self, date, priority, longitude, latitude,
                 height, azimuth, satellite_amount, speed):
        super().__init__()
        self.date = date
        self.priority = priority
        self.longitude = longitude
        self.latitude = latitude
        self.height = height
        self.azimuth = azimuth
        self.satellite_amount = satellite_amount
        self.speed = speed


class Machine(Base):
    __tablename__ = 'machine'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    imei = sa.Column(sa.Integer)
