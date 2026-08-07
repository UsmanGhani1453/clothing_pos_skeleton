from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/customers", tags=["customers"])

@router.get("/", response_model=List[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Customer).order_by(models.Customer.name).all()

@router.get("/dues", response_model=List[schemas.CustomerOut])
def list_dues(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    """Fetch all customers with a positive balance (Udhar)."""
    return db.query(models.Customer).filter(
        models.Customer.balance > 0
    ).order_by(models.Customer.balance.desc()).all()

@router.post("/", response_model=schemas.CustomerOut)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A customer with this phone number already exists.")
    db.refresh(db_customer)
    return db_customer

@router.get("/{customer_id}/ledger", response_model=List[schemas.LedgerEntryOut])
def get_ledger(customer_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.LedgerEntry).filter(models.LedgerEntry.customer_id == customer_id).order_by(models.LedgerEntry.created_at.desc()).all()

@router.post("/{customer_id}/pay")
def record_payment(
    customer_id: int,
    amount: float = Query(..., gt=0, description="Payment amount, must be greater than 0"),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if amount > customer.balance:
        raise HTTPException(
            status_code=400,
            detail=f"Payment (Rs. {amount:.0f}) exceeds the outstanding balance (Rs. {customer.balance:.0f})."
        )

    # Decrease balance
    customer.balance -= amount
    
    # Log payment in ledger
    entry = models.LedgerEntry(
        customer_id=customer.id, 
        amount=amount, 
        entry_type="payment", 
        description="Received payment for Khata"
    )
    db.add(entry)
    db.commit()

    return {"ok": True, "new_balance": customer.balance}