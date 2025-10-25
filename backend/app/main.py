from fastapi import FastAPI
from .core.config import settings
from .db.database import Base, engine, SessionLocal
from .api.routes import router
from .models.models import EmissionFactor
import json, os
from fastapi.middleware.cors import CORSMiddleware

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.api_title, version=settings.api_version, description="CarbonIQ — A Carbon Accounting & Emission Forecasting API")

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your actual Streamlit URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def load_default_factors():
    db = SessionLocal()
    count = db.query(EmissionFactor).count()
    print(f"Startup check: emission_factors count = {count}")

    if count == 0:
        json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/emission_factors.json"))
        print(f"Attempting to load factors from absolute path: {json_path}")

        if not os.path.exists(json_path):
            print("⚠️ File not found at that path!")
        else:
            try:
                with open(json_path, "r") as f:
                    factors = json.load(f)
                for item in factors:
                    db.add(EmissionFactor(**item))
                db.commit()
                print(f"✅ Loaded {len(factors)} emission factors from {json_path}")
            except Exception as e:
                print(f"⚠️ Could not load emission factors: {e}")

    db.close()
