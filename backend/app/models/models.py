
from sqlalchemy import Column, Integer, Float, String, Date, UniqueConstraint
from ..db.database import Base

class EmissionFactor(Base):
    __tablename__ = "emission_factors"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, nullable=False)
    unit = Column(String, nullable=False)  # e.g., kWh, m3, hour
    factor_kgco2e_per_unit = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("category", "unit", name="uq_category_unit"),)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=True)  # currency amount (optional for Week 1 logic)
    category = Column(String, nullable=False)  # should match an emission factor category
    unit = Column(String, nullable=False)  # unit corresponding to emission factor
    quantity = Column(Float, nullable=False)  # activity quantity, e.g., kWh consumed
    emission_scope = Column(String, nullable=True)  # e.g., scope1, scope2, scope3
    emission_kgco2e = Column(Float, nullable=True)
