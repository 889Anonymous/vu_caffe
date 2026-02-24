from sqlalchemy import Column, Integer, String, Float, Date, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    image_url = Column(String, nullable=True) # Supported external links like vn1.co

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    posting_date = Column(Date, default=datetime.date.today)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    grand_total = Column(Float)
    docstatus = Column(Integer, default=1) # 1 = submitted/paid
    
    items = relationship("OrderItem", back_populates="parent")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_id = Column(Integer)
    item_name = Column(String)
    qty = Column(Float)
    price = Column(Float)
    
    parent = relationship("Order", back_populates="items")

class StockEntry(Base):
    __tablename__ = "stock_entries"
    id = Column(Integer, primary_key=True, index=True)
    posting_date = Column(Date, default=datetime.date.today)
    total_amount = Column(Float)
    purpose = Column(String, default="Material Issue")

class DailyReport(Base):
    __tablename__ = "daily_reports"
    month_year = Column(String, primary_key=True) # YYYY-MM
    daily_data = Column(JSON) # {"YYYY-MM-DD": {"revenue": 0, "cost": 0, "profit": 0}}

class Config(Base):
    __tablename__ = "config"
    id = Column(Integer, primary_key=True, index=True)
    tele_bot_token = Column(String)
    tele_chat_id = Column(String)
