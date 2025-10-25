from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from ..db.database import get_db
from ..models.models import EmissionFactor, Transaction
from ..schemas.schemas import EmissionFactorCreate, EmissionFactorOut, TransactionOut
from ..utils.csv_loader import read_transactions_csv
from ..services.emissions import compute_emission_for_transaction
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression

router = APIRouter()

# -------------------- Root & Health --------------------

@router.get("/")
def root():
    return {"message": "Welcome to CarbonIQ API", "version": "0.1.0"}

@router.get("/health")
def healthcheck():
    return {"status": "ok"}

# -------------------- Emission Factors --------------------

@router.get("/factors", response_model=list[EmissionFactorOut])
def list_factors(db: Session = Depends(get_db)):
    """List all stored emission factors."""
    return db.query(EmissionFactor).all()

@router.post("/factors", response_model=EmissionFactorOut)
def upsert_factor(payload: EmissionFactorCreate, db: Session = Depends(get_db)):
    """Insert or update an emission factor."""
    existing = (
        db.query(EmissionFactor)
        .filter(EmissionFactor.category == payload.category, EmissionFactor.unit == payload.unit)
        .first()
    )
    if existing:
        existing.factor_kgco2e_per_unit = payload.factor_kgco2e_per_unit
        db.commit()
        db.refresh(existing)
        return existing

    factor = EmissionFactor(**payload.model_dump())
    db.add(factor)
    db.commit()
    db.refresh(factor)
    return factor

# -------------------- Upload Transactions --------------------

@router.post("/upload")
def upload_transactions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload transactions from a CSV and compute emissions."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    try:
        df = read_transactions_csv(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    created = 0
    for _, row in df.iterrows():
        # Parse date safely
        dt = row["date"]
        if isinstance(dt, str):
            dt_parsed = None
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
                try:
                    dt_parsed = datetime.strptime(dt, fmt).date()
                    break
                except Exception:
                    continue
            if dt_parsed is None:
                raise HTTPException(status_code=400, detail=f"Bad date format: {dt}")
        else:
            dt_parsed = dt

        print(f"Row debug → category='{row['category']}', unit='{row['unit']}'")

        tx = Transaction(
            date=dt_parsed,
            description=str(row["description"]),
            amount=float(row["amount"]) if "amount" in row and not pd.isna(row["amount"]) else None,
            category=str(row["category"]),
            unit=str(row["unit"]),
            quantity=float(row["quantity"]),
            emission_scope=str(row["emission_scope"]) if "emission_scope" in row and not pd.isna(row["emission_scope"]) else None,
        )

        emission = compute_emission_for_transaction(db, tx)
        tx.emission_kgco2e = emission
        db.add(tx)
        created += 1

    db.commit()
    return {"inserted": created}

# -------------------- List Transactions --------------------

@router.get("/transactions", response_model=list[TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    """Return all stored transactions with computed emissions."""
    return db.query(Transaction).all()

# -------------------- Emissions Summary --------------------

@router.get("/emissions/summary")
def emissions_summary(db: Session = Depends(get_db)):
    """Return total emissions grouped by scope and category."""
    rows = (
        db.query(Transaction.emission_scope, Transaction.category, func.sum(Transaction.emission_kgco2e))
        .group_by(Transaction.emission_scope, Transaction.category)
        .all()
    )

    summary = {}
    for scope, category, total in rows:
        if not scope:
            scope = "unspecified"
        summary.setdefault(scope, {})[category] = round(total, 2)
    return summary

# -------------------- Analytics: Trends --------------------

@router.get("/analytics/trends")
def emission_trends(db: Session = Depends(get_db)):
    """Show emissions trends aggregated monthly."""
    rows = db.query(Transaction).all()
    if not rows:
        return []

    data = {}
    for tx in rows:
        if not tx.date or not tx.emission_kgco2e:
            continue
        month = tx.date.strftime("%Y-%m")
        data.setdefault(month, 0)
        data[month] += tx.emission_kgco2e

    sorted_data = sorted(data.items())
    return [{"month": m, "emissions": v} for m, v in sorted_data]

# -------------------- Analytics: Scope Breakdown --------------------

@router.get("/analytics/scope_breakdown")
def scope_breakdown(db: Session = Depends(get_db)):
    """Return total emissions grouped by Scope (1,2,3)."""
    rows = db.query(Transaction).all()
    result = {}
    for tx in rows:
        if tx.emission_scope and tx.emission_kgco2e:
            result.setdefault(tx.emission_scope, 0)
            result[tx.emission_scope] += tx.emission_kgco2e
    return result

# -------------------- Analytics: Forecast --------------------

@router.get("/analytics/forecast")
def emission_forecast(db: Session = Depends(get_db)):
    """Predict emissions for next 3 months using a simple linear model."""
    rows = db.query(Transaction).all()
    data = [{"date": tx.date, "emission": tx.emission_kgco2e}
            for tx in rows if tx.date and tx.emission_kgco2e]

    if not data:
        return []

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    df_grouped = df.groupby("month")["emission"].sum().reset_index()
    df_grouped["month_num"] = np.arange(len(df_grouped))

    X = df_grouped["month_num"].values.reshape(-1, 1)
    y = df_grouped["emission"].values
    model = LinearRegression().fit(X, y)

    future = np.arange(len(df_grouped), len(df_grouped) + 3).reshape(-1, 1)
    preds = model.predict(future)
    last_month = df_grouped["month"].iloc[-1]
    forecast_months = pd.period_range(start=last_month + 1, periods=3, freq="M")

    return [{"month": str(m), "predicted_emissions": float(e)}
            for m, e in zip(forecast_months, preds)]

# -------------------- Admin: Reset --------------------

@router.delete("/admin/reset")
def reset_db(db: Session = Depends(get_db)):
    """Delete all transactions from database."""
    db.query(Transaction).delete()
    db.commit()
    return {"message": "All transactions deleted"}

# -------------------- Analytics: Insights --------------------

@router.get("/analytics/insights")
def generate_insights(db: Session = Depends(get_db)):
    """Generate high-level insights from emission data."""
    transactions = db.query(Transaction).all()
    if not transactions:
        return {"message": "No data available"}

    df = pd.DataFrame([{
        "date": tx.date,
        "scope": tx.emission_scope,
        "category": tx.category,
        "emission": tx.emission_kgco2e
    } for tx in transactions if tx.emission_kgco2e])

    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
    insights = []

    # Top emission source
    top_source = df.groupby("category")["emission"].sum().idxmax()
    top_val = df.groupby("category")["emission"].sum().max()
    insights.append(f"🔥 Your largest emission source is **{top_source}** ({top_val:.0f} kg CO₂e).")

    # Scope comparison
    scope_totals = df.groupby("scope")["emission"].sum()
    if len(scope_totals) > 1:
        dominant_scope = scope_totals.idxmax()
        insights.append(f"♻️ **{dominant_scope.capitalize()}** accounts for the highest share of total emissions.")

    # Trend check
    monthly = df.groupby("month")["emission"].sum().sort_index()
    if len(monthly) >= 2:
        pct_change = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]) * 100
        direction = "increased 📈" if pct_change > 0 else "decreased 📉"
        insights.append(f"📅 Emissions {direction} by **{abs(pct_change):.1f}%** last month.")

    return {"insights": insights}
