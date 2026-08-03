from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, default="")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="cashier")  # owner / cashier


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, default="")
    size = Column(String, default="")
    color = Column(String, default="")
    barcode = Column(String, unique=True, nullable=True, index=True)
    cost_price = Column(Float, default=0.0)
    sale_price = Column(Float, nullable=False)
    stock_qty = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String, unique=True, index=True)
    total_amount = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    payment_method = Column(String, default="cash")
    cashier = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String)  # snapshot, in case product edited later
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)

    sale = relationship("Sale", back_populates="items")
