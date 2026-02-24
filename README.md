# Modern Hybrid POS Monorepo

This repository contains a lightweight, high-performance POS system with a Python backend and a ReactJS frontend.

## Project Structure
- `pos-backend/`: FastAPI + SQLite + APScheduler. Handles all business logic, data persistence, and automated Telegram notifications.
- `pos-frontend/`: ReactJS + Vite + Tailwind. Recovered legacy UI optimized for faster interaction.
- `legacy-vue-pos/`: Backup of the original Vue-based POS.

## Getting Started

### 1. Run the Backend
```bash
cd pos-backend
pip install -r requirements.txt
python -m uvicorn src.pos.main:app --reload
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
- **Branding**: All components follow the "Modern POS" neutral branding.
- **Reporting**: Automated EOD summaries delivered via Telegram at 08:00 AM.