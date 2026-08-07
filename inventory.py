from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user, require_owner

router = APIRouter(prefix="/api/products", tags=["inventory"])

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(search: str = "", db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    # Any logged-in user (owner or cashier) can view/search products - needed for billing.
    q = db.query(models.Product)
    if search:
        # Match on name OR barcode so barcode scanner input (which sends the raw
        # barcode string, not a product name) actually finds the product.
        q = q.filter(
            or_(
                models.Product.name.ilike(f"%{search}%"),
                models.Product.barcode.ilike(f"%{search}%"),
            )
        )
    return q.order_by(models.Product.name).all()

@router.post("/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), _: models.User = Depends(require_owner)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A product with this barcode already exists.")
    db.refresh(db_product)
    return db_product

@router.get("/low-stock", response_model=List[schemas.ProductOut])
def get_low_stock_products(
    threshold: int = 5, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_user)
):
    """Fetch all products with stock quantity less than or equal to the threshold."""
    return db.query(models.Product).filter(
        models.Product.stock_qty <= threshold
    ).order_by(models.Product.stock_qty).all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), _: models.User = Depends(require_owner)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A product with this barcode already exists.")
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_owner)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"ok": True}