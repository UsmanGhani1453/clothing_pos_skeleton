from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    category: Optional[str] = ""
    size: Optional[str] = ""
    color: Optional[str] = ""
    barcode: Optional[str] = None
    cost_price: float = 0.0
    sale_price: float
    stock_qty: int = 0


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True


class SaleItemIn(BaseModel):
    product_id: int
    quantity: int


class SaleCreate(BaseModel):
    items: List[SaleItemIn]
    discount: float = 0.0
    payment_method: str = "cash"
    cashier: Optional[str] = ""


class SaleItemOut(BaseModel):
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: int
    invoice_no: str
    total_amount: float
    discount: float
    payment_method: str
    cashier: Optional[str] = ""
    created_at: datetime
    items: List[SaleItemOut] = []

    class Config:
        from_attributes = True
