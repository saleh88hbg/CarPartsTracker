import warnings
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning)

sqlite_file_name = "car_parts.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

class Vehicle(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    reg_number: str = Field(default=None, primary_key=True)
    make: str
    model: str
    year: int
    engine: str
    color: Optional[str] = "Okänd"
    fuel_type: Optional[str] = "Okänd"
    gearbox: Optional[str] = "Okänd"
    inspected_mileage: Optional[str] = "Ej angivet"  # <--- Senaste besiktningsmiltal
    vin: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    SQLModel.metadata.create_all(engine)