from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine, Relationship

# --- TABELL 1: Bilar (Cachad bilinformation) ---
class Vehicle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reg_number: str = Field(index=True, unique=True)
    make: str
    model: str
    year: int
    engine: str
    vin: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- TABELL 2: Reservdelar ---
class Part(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    article_number: str = Field(index=True)
    brand: str
    part_type: str                  # t.ex. "Bromsbelägg fram"
    is_original: bool = False       # True = Original, False = Eftermarknad
    oem_numbers: str                # Lagras som komma-separerad sträng (t.ex. "31445796,31445797")
    
    # Koppling till prishistorik
    prices: List["PriceHistory"] = Relationship(back_populates="part")

# --- TABELL 3: Prishistorik (Sparar alla priser vi hittar över tid) ---
class PriceHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    part_id: int = Field(foreign_key="part.id")
    store_name: str                 # t.ex. "Autodoc", "Mekonomen"
    price_sek: float
    shipping_cost_sek: float
    in_stock: bool
    delivery_days: str
    url: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow) # Tidsstämpel för historik!

    part: Optional[Part] = Relationship(back_populates="prices")

# --- TABELL 4: Prisbevakning ---
class PriceAlert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str
    part_id: int = Field(foreign_key="part.id")
    target_price_sek: float
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- DATABASKOPPLING ---
sqlite_file_name = "carparts.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

def init_db():
    """Skapar databasfilen och alla tabeller om de inte redan finns."""
    SQLModel.metadata.create_all(engine)