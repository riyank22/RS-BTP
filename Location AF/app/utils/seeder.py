import json
from database import SessionLocal
from models.db_models import GNB, UE, Geofence


def seed_db():
    db = SessionLocal()
    # Only seed if GNB table is empty
    if db.query(GNB).count() == 0:
        try:
            with open("app/data/seed_data.json", "r") as f:
                data = json.load(f)

                for g in data['gnbs']:
                    db.add(GNB(gnb_id=g['id'], lat=g['lat'], lng=g['lng'],radius=g.get('radius', 500.0)))

                for u in data['static_ues']:
                    db.add(UE(ue_id=u['id'], lat=u['lat'], lng=u['lng']))

                for z in data['zones']:
                    db.add(Geofence(zone_id=z['id'], zone_type=z['type'], shape=z['shape'], data=z['data']))

                db.commit()
                print("Database Seeded Successfully.")
            db.close()
        except Exception as e:
            print(f"Something went wrong: {e}")

