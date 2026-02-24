# Modern Hybrid POS Monorepo (Original UI)

This repository contains a high-performance POS system with a **Pure Python Backend** and the **Original Vue.js Frontend**.

## Project Structure
- `pos-backend/`: FastAPI + SQLite + APScheduler. Handles business logic, persistence, and automated Telegram notifications. Implements a compatibility layer for the original UI.
- `pos-frontend/`: Original Vue.js + Vite + Tailwind. The premium, feature-rich interface recovered and optimized for the new backend.
- `pos/`: (Deprecated) Backup folder.

## Getting Started

### 1. Run the Backend
```bash
cd pos-backend
pip install -r requirements.txt
python -m uvicorn src.pos.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Run the Frontend
```bash
cd pos-frontend
npm install
npm run dev
```

### 3. Docker Deployment (Combined)
```bash
cd pos-backend
docker-compose up --build -d
```
Access at `http://localhost:5173` (Frontend) and `http://localhost:8000/api` (Backend).

## Maintenance
- **Legacy Compatibility**: Backend mapping in `src/pos/routers/api.py`.
- **Reporting**: Automated EOD summaries delivered via Telegram.