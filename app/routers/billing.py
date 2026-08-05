from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/sales", tags=["billing"])


def generate_invoice_no():
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@router.post("/", response_model=schemas.SaleOut)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if not sale.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0.0
    sale_items = []

    for item in sale.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_qty < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name} (available: {product.stock_qty})"
            )
        subtotal = product.sale_price * item.quantity
        total += subtotal

        sale_items.append(models.SaleItem(
            product_id=product.id,
            product_name=product.name,
            quantity=item.quantity,
            unit_price=product.sale_price,
            subtotal=subtotal,
        ))

        product.stock_qty -= item.quantity

    total_after_discount = max(total - sale.discount, 0)
    invoice_no = generate_invoice_no()

    # --- Udhar / Khata Logic ---
    if sale.payment_method == "udhar":
        if not sale.customer_id:
            raise HTTPException(status_code=400, detail="Customer must be selected for Udhar.")

        customer = db.query(models.Customer).filter(models.Customer.id == sale.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found.")

        # Increase debt balance
        customer.balance += total_after_discount

        # Create ledger entry
        db.add(models.LedgerEntry(
            customer_id=customer.id,
            amount=total_after_discount,
            entry_type="udhar",
            description=f"Bill: {invoice_no}",
        ))

    db_sale = models.Sale(
        invoice_no=invoice_no,
        total_amount=total_after_discount,
        discount=sale.discount,
        payment_method=sale.payment_method,
        cashier=user.username,
        customer_id=sale.customer_id,
        items=sale_items,
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=list[schemas.SaleOut])
def list_sales(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Sale).order_by(models.Sale.created_at.desc()).limit(200).all()


@router.get("/{sale_id}", response_model=schemas.SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale