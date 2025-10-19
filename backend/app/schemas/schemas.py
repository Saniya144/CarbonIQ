
from pydantic import BaseModel, Field
from datetime import date

class EmissionFactorBase(BaseModel):
    category: str
    unit: str
    factor_kgco2e_per_unit: float = Field(gt=0)

class EmissionFactorCreate(EmissionFactorBase):
    pass

class EmissionFactorOut(EmissionFactorBase):
    id: int
    class Config:
        from_attributes = True

class TransactionIn(BaseModel):
    date: date
    description: str
    amount: float | None = None
    category: str
    unit: str
    quantity: float = Field(gt=0)
    emission_scope: str | None = None

class TransactionOut(TransactionIn):
    id: int
    emission_kgco2e: float | None = None
    class Config:
        from_attributes = True
