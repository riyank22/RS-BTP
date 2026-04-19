from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy.sql import func
from sqlalchemy import event
Base = declarative_base()

class GNB(Base):
    __tablename__ = "gnbs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    gnb_id = Column(String, unique=True, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    radius = Column(Float, default=500.0)  # Coverage radius in meters
    # Use DB-side NOW so inserts done via ORM still get a timestamp value
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class UE(Base):
    __tablename__ = "ues"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ue_id = Column(String, unique=True, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    # use func.now() for DB-side timestamping
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Geofence(Base):
    __tablename__ = "geofences"
    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String, unique=True)
    zone_type = Column(String) # RED, PINK
    shape = Column(String)     # CIRCLE, POLYGON
    data = Column(JSON)        # {"radius": 500, "center": [lat, lng]}


# Ensure Python-side timestamps are populated reliably for ORM INSERTs
@event.listens_for(UE, "before_insert")
def _set_ue_timestamp(mapper, connection, target):
    if getattr(target, "timestamp", None) is None:
        target.timestamp = datetime.datetime.utcnow()


@event.listens_for(GNB, "before_insert")
def _set_gnb_timestamp(mapper, connection, target):
    if getattr(target, "timestamp", None) is None:
        target.timestamp = datetime.datetime.utcnow()
