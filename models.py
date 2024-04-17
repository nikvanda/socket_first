import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Record(Base):
    __tablename__ = 'record'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    date = sa.Column(sa.DateTime)
    priority = sa.Column(sa.Boolean)
    longitude = sa.Column(sa.Float)
    latitude = sa.Column(sa.Float)
    height = sa.Column(sa.Float)
    azimuth = sa.Column(sa.Float)
    satellite_amount = sa.Column(sa.Integer)
    speed = sa.Column(sa.Float)

    machine_id = sa.Column(sa.Integer, sa.ForeignKey('machine.imei'))
    machine = relationship('Machine', back_populates='record')

    def __init__(self, date, priority, longitude, latitude,
                 height, azimuth, satellite_amount, speed, machine_id):
        super().__init__()
        self.date = date
        self.priority = priority
        self.longitude = longitude
        self.latitude = latitude
        self.height = height
        self.azimuth = azimuth
        self.satellite_amount = satellite_amount
        self.speed = speed
        self.machine_id = machine_id


class Machine(Base):
    __tablename__ = 'machine'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    imei = sa.Column(sa.Integer, unique=True)
    record = relationship('Record', back_populates='machine')

    def __init__(self, imei):
        super().__init__()
        self.imei = imei
