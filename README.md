# Modern Pure Python POS System

A high-performance, lightweight Point of Sale system built with **FastAPI**, **SQLite**, and **HTMX**. Optimized for minimal resource usage (<400MB RAM) on edge devices and free-tier cloud VMs.

## Key Features
- **Fast & Responsive**: HTMX driven UI for instant interactive experience.
- **Persistent Storage**: Robust SQLite database with optimized indexing and aggregation.
- **Automated Reporting**: Integrated EOD aggregation and Telegram notification system.
- **Standard Layout**: Clean `src/` package structure for easy maintenance.
- **Docker-Ready**: Optimized deployment with Docker Compose.

## Project Structure
- `src/pos`: Core application logic (API, Models, DB).
- `src/templates`: Neutral Jinja2 templates.
- `src/static`: Static assets.
- `deploy/`: Dockerization files.

## Getting Started
1. **Clone**: `git clone <repo-url>`
2. **Setup Env**: Copy `.env.example` to `.env` and add your Telegram keys.
3. **Deploy**: `docker-compose -f deploy/docker-compose.yml up --build -d`
4. **Access**: Open `http://localhost:8000`

## Maintainer
Designed for speed and simplicity.