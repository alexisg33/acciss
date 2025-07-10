from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Reemplaza con tus credenciales reales
DATABASE_URL = "postgresql://usuario:contraseña@localhost:5432/acciss"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class StockMaterial(Base):
    __tablename__ = 'stock_materials'
    id = Column(Integer, primary_key=True)
    material_description = Column(String)
    part_number = Column(String)
    hazards_identified = Column(String)
    quantity = Column(Integer)
    after_open = Column(String)
    expiration_date = Column(String)
    due_date_match = Column(String)
    batch_number = Column(String)
    comments = Column(String)
    entry_date = Column(String)
    output_date = Column(String)

Base.metadata.create_all(engine)
