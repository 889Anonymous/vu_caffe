from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import api
from .scheduler import scheduler
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Modern POS Backend")

# CORS configuration for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)

@app.on_event("startup")
async def startup_event():
    if not scheduler.running:
        scheduler.start()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Modern POS Backend is running"}
