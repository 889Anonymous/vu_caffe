from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from datetime import date
import requests
import os

def format_vnd(amount):
    return "{:,.0f} ₫".format(amount).replace(",", ".")

def get_items(db: Session):
    return db.query(models.Item).all()

def create_order(db: Session, items_data: list):
    grand_total = 0
    order_items = []
    
    for item in items_data:
        db_item = db.query(models.Item).filter(models.Item.id == item['id']).first()
        if db_item:
            item_total = db_item.price * item['qty']
            grand_total += item_total
            order_items.append(models.OrderItem(
                item_id=db_item.id,
                item_name=db_item.name,
                qty=item['qty'],
                price=db_item.price,
                modifiers=item.get('modifiers')
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
    revenue = db.query(func.sum(models.Order.grand_total)).filter(
        models.Order.posting_date == target_date,
        models.Order.docstatus == 1
    ).scalar() or 0
    
    cost = db.query(func.sum(models.StockEntry.total_amount)).filter(
        models.StockEntry.posting_date == target_date,
        models.StockEntry.purpose == "Material Issue"
    ).scalar() or 0
    
    return revenue, cost

def send_telegram_noti(db: Session, message: str):
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
