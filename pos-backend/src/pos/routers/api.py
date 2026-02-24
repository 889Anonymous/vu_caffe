from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .. import crud, database, models
from datetime import date, timedelta
from typing import Optional

router = APIRouter()

# --- Legacy Compatibility Routes ---

@router.get("/api/method/ury.ury_pos.api.getPosProfile")
def get_pos_profile(db: Session = Depends(database.get_db)):
    # Mocking minimum required profile info for the UI
    return {
        "message": {
            "pos_profile": "Default POS Profile",
            "warehouse": "Default Warehouse",
            "company": "Modern POS Co.",
            "currency": "VND",
            "waiter": "Cashier",
            "cashier": "Cashier",
            "restaurant": 1,
            "company_address": "Vietnam",
            "tableAttention": 1
        }
    }

@router.get("/api/method/ury.ury_pos.api.getRestaurantMenu")
def get_restaurant_menu(db: Session = Depends(database.get_db)):
    items = crud.get_items(db)
    # Map our models to the legacy format
    legacy_items = []
    for item in items:
        legacy_items.append({
            "item": item.code,
            "item_name": item.name,
            "item_image": item.image,
            "rate": item.price,
            "course": item.category or "General",
            "description": item.description,
            "special_dish": 0
        })
    return {"message": {"items": legacy_items}}

@router.get("/api/method/ury.ury_pos.api.getModeOfPayment")
def get_mode_of_payment():
    return {"message": ["Cash", "Mobile Payment"]}

@router.post("/api/method/ury.ury.doctype.ury_order.ury_order.sync_order")
async def sync_order(request: Request, db: Session = Depends(database.get_db)):
    data = await request.json()
    # Frontend sends: { "items": [...], "table": "...", ... }
    items_data = data.get("items", [])
    if not items_data:
        raise HTTPException(status_code=400, detail="Order info missing")
    
    # Map legacy items to our create_order expected format
    mapped_items = []
    for item in items_data:
        # Legacy might send 'item' as code, and 'qty'
        mapped_items.append({
            "code": item.get("item"),
            "qty": item.get("qty", 1)
        })
    
    order = crud.create_order(db, mapped_items)
    return {
        "message": {
            "name": f"ORD-{order.id}",
            "status": "Success",
            "grand_total": order.total,
            "items": items_data, # Return back for confirmation
            "modified": str(order.created_at)
        }
    }

@router.get("/api/method/ury.ury.doctype.ury_order.ury_order.get_order_invoice")
def get_order_invoice(table: str, db: Session = Depends(database.get_db)):
    # Mocking an empty invoice for the table
    return {"message": None}

@router.get("/api/method/ury.ury_pos.api.get_select_field_options")
def get_select_field_options():
    return {"message": [{"name": "Dine In"}, {"name": "Take Away"}]}

@router.get("/api/method/ury.ury_pos.api.getAggregator")
def get_aggregator():
    return {"message": []}

@router.get("/api/method/ury.ury_pos.api.getAggregatorItem")
def get_aggregator_item():
    return {"message": []}

# --- Generic Resource Fallback (Mocking Frappe DB calls) ---

@router.get("/api/resource/{doctype}")
def get_resource_list(doctype: str, db: Session = Depends(database.get_db)):
    if doctype == "URY Menu Course":
        # Extract unique categories from items
        items = crud.get_items(db)
        categories = sorted(list(set(item.category for item in items if item.category)))
        return {"data": [{"name": cat} for cat in categories]}
    return {"data": []}

@router.get("/api/resource/{doctype}/{name}")
def get_resource_doc(doctype: str, name: str):
    if doctype == "Company":
        return {"data": {"default_currency": "VND"}}
    if doctype == "Currency":
        return {"data": {"symbol": "₫"}}
    return {"data": {}}

# --- Modern API Routes (Keep for future use) ---

@router.get("/api/items")
def list_items(db: Session = Depends(database.get_db)):
    return crud.get_items(db)

@router.post("/api/orders")
def place_order(order_data: dict, db: Session = Depends(database.get_db)):
    if not order_data.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    order = crud.create_order(db, order_data["items"])
    return {"order_id": order.id, "success": True}
