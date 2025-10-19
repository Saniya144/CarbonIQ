from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.models import EmissionFactor, Transaction

def compute_emission_for_transaction(db: Session, tx: Transaction) -> float | None:
    # Clean inputs (remove spaces, make lowercase)
    cat = tx.category.strip().lower() if tx.category else None
    unit = tx.unit.strip().lower() if tx.unit else None

    if not cat or not unit:
        return None

    # Case-insensitive match
    factor = (
        db.query(EmissionFactor)
        .filter(
            func.lower(EmissionFactor.category) == cat,
            func.lower(EmissionFactor.unit) == unit
        )
        .first()
    )

    if not factor:
        print(f"⚠️ No emission factor found for category={cat}, unit={unit}")
        return None

    return tx.quantity * factor.factor_kgco2e_per_unit
