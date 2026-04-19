from typing import List

from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import db_models, schemas
from utils.seeder import seed_db

# Import your existing services
# from services import nrf_manager

# Create tables
db_models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed Data & Register to NRF
    seed_db()
    # await nrf_manager.register_af() # Logic from your QoS AF
    yield
    # Shutdown: Deregister
    # await nrf_manager.deregister_af()


app = FastAPI(title="Location_AF_Module", lifespan=lifespan)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/location/get-ues", response_model=List[schemas.UEResponse])
def get_all_ues(db: Session = Depends(get_db)):
    # Sort by timestamp descending to ensure freshest data is prioritized
    return db.query(db_models.UE).order_by(db_models.UE.timestamp.desc()).all()


@app.get("/location/get-gnbs")
def get_all_gnbs(db: Session = Depends(get_db)):
    # gNodeBs are static but keeping order for consistency
    return db.query(db_models.GNB).order_by(db_models.GNB.timestamp.desc()).all()


@app.get("/location/{device_id}")
def get_location(device_id: str, db: Session = Depends(get_db)):
    # Check UE table first, sorted by latest
    res = db.query(db_models.UE).filter(db_models.UE.ue_id == device_id) \
        .order_by(db_models.UE.timestamp.desc()).first()

    if not res:
        # Check GNB table
        res = db.query(db_models.GNB).filter(db_models.GNB.gnb_id == device_id).first()

    if res:
        # We manually return a dict here to include the timestamp in a clean format
        return {
            "id": device_id,
            "lat": res.lat,
            "lng": res.lng,
            "timestamp": res.timestamp.isoformat() if res.timestamp else None
        }
    raise HTTPException(status_code=404, detail="Device not found")


@app.post("/location/update")
def update_location(data: schemas.LocationUpdate, db: Session = Depends(get_db)):
    ue = db.query(db_models.UE).filter(db_models.UE.ue_id == data.id).first()
    if ue:
        ue.lat = data.lat
        ue.lng = data.lng
        db.commit()
        return {"status": "success"}

    # If UE doesn't exist (new drone), create it
    new_ue = db_models.UE(ue_id=data.id, lat=data.lat, lng=data.lng)
    db.add(new_ue)
    db.commit()
    return {"status": "created"}


@app.get("/zones")
def get_zones(db: Session = Depends(get_db)):
    return db.query(db_models.Geofence).all()