from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, database, crud
from scheduler import scheduler
import os
from dotenv import load_dotenv

load_dotenv()

# Build DB tables on startup
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Vu Caffe Pure Python POS")

# In-memory cart for demo simulation (HTMX state)
CART = []

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inject format_vnd into all templates
templates.env.globals.update(format_vnd=crud.format_vnd)

@app.on_event("startup")
async def startup_event():
    if not scheduler.running:
        scheduler.start()

@app.get("/", response_class=HTMLResponse)
async def pos_page(request: Request, db: Session = Depends(database.get_db)):
    items = crud.get_items(db)
    return templates.TemplateResponse("pos.html", {"request": request, "items": items})

@app.post("/cart/add", response_class=HTMLResponse)
async def add_to_cart(request: Request, item_id: int = Form(...), db: Session = Depends(database.get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item:
        CART.append(item)
    
    total = sum(i.price for i in CART)
    return templates.TemplateResponse("cart_partial.html", {
        "request": request, 
        "cart": CART, 
        "total": total
    })

@app.post("/orders")
async def place_order(db: Session = Depends(database.get_db)):
    if not CART:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    items_data = [{"item_id": i.id, "qty": 1} for i in CART]
    order = crud.create_order(db, items_data)
    CART.clear()
    
    return HTMLResponse(content="<script>alert('Thanh toán thành công!'); window.location.reload();</script>")

# API Endpoints
@app.get("/api/items")
def list_items(db: Session = Depends(database.get_db)):
    return crud.get_items(db)

@app.post("/api/items")
def add_item(name: str, price: float, image_url: str = None, db: Session = Depends(database.get_db)):
    return crud.create_item(db, name, price, image_url)
