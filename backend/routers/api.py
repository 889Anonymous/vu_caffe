from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, database, models
from datetime import date, timedelta

router = APIRouter(prefix="/api")

@router.get("/items")
def list_items(db: Session = Depends(database.get_db)):
    return crud.get_items(db)

@router.post("/orders")
def place_order(order_data: dict, db: Session = Depends(database.get_db)):
    # Expected format: {"items": [{"id": 1, "qty": 2}], "total": 1000}
    if not order_data.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    order = crud.create_order(db, order_data["items"])
    return {"order_id": order.id, "success": True}

@router.get("/report/daily")
def get_daily_report(db: Session = Depends(database.get_db)):
    yesterday = date.today() - timedelta(days=1)
    revenue, cost = crud.get_daily_aggregated_data(db, yesterday)
    return {
        "date": str(yesterday),
        "revenue": revenue,
        "cost": cost,
        "profit": revenue - cost
    }

@router.get("/config/telegram")
def get_telegram_config(db: Session = Depends(database.get_db)):
    config = db.query(models.Config).first()
    if not config:
        return {"token": None, "chat_id": None}
    return {"token": config.tele_bot_token[:5] + "..." if config.tele_bot_token else None, "chat_id": config.tele_chat_id}
