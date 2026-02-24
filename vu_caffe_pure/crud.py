from sqlalchemy.orm import Session
import models
from datetime import date

def format_vnd(amount):
    """Formats a float as Vietnamese currency: 1.234.567 ₫"""
    return "{:,.0f} ₫".format(amount).replace(",", ".")

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_item(db: Session, name: str, price: float, image_url: str = None):
    db_item = models.Item(name=name, price=price, image_url=image_url)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_order(db: Session, items_data: list):
    """
    items_data: list of dicts [{'item_id': 1, 'qty': 2}, ...]
    """
    grand_total = 0
    order_items = []
    
    for item in items_data:
        db_item = db.query(models.Item).filter(models.Item.id == item['item_id']).first()
        if db_item:
            item_total = db_item.price * item['qty']
            grand_total += item_total
            order_items.append(models.OrderItem(
                item_id=db_item.id,
                item_name=db_item.name,
                qty=item['qty'],
                price=db_item.price
            ))
            
    db_order = models.Order(grand_total=grand_total)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for oi in order_items:
        oi.order_id = db_order.id
        db.add(oi)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_daily_aggregated_data(db: Session, target_date: date):
    # Sum grand_total from Orders
    rev_result = db.query(models.Order).filter(
        models.Order.posting_date == target_date,
        models.Order.docstatus == 1
    ).all()
    revenue = sum(o.grand_total for o in rev_result)
    
    # Sum total_amount from StockEntries (Material Issue)
    cost_result = db.query(models.StockEntry).filter(
        models.StockEntry.posting_date == target_date,
        models.StockEntry.purpose == "Material Issue"
    ).all()
    cost = sum(s.total_amount for s in cost_result)
    
    return revenue, cost

def create_stock_entry(db: Session, amount: float, posting_date: date = None):
    if not posting_date:
        posting_date = date.today()
    db_entry = models.StockEntry(total_amount=amount, posting_date=posting_date)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

import requests
import os

def send_telegram_noti(db: Session, message: str):
    # Try getting from DB Config first
    config = db.query(models.Config).first()
    token = config.tele_bot_token if config else os.getenv("TELEGRAM_TOKEN")
    chat_id = config.tele_chat_id if config else os.getenv("CHAT_ID")
    
    if not token or not chat_id:
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except Exception:
        return False
