from apscheduler.schedulers.asyncio import AsyncIOScheduler
from . import crud, database, models
from datetime import date, timedelta
import logging

logging.basicConfig(filename="log.txt", level=logging.INFO)

def update_daily_report():
    db = database.SessionLocal()
    try:
        yesterday = date.today() - timedelta(days=1)
        yesterday_str = str(yesterday)
        month_year = yesterday_str[:7]
        
        revenue, cost = crud.get_daily_aggregated_data(db, yesterday)
        
        report = db.query(models.DailyReport).filter(models.DailyReport.month_year == month_year).first()
        if not report:
            report = models.DailyReport(month_year=month_year, daily_data={})
            db.add(report)
        
        data = report.daily_data or {}
        data[yesterday_str] = {
            "revenue": float(revenue),
            "cost": float(cost),
            "profit": float(revenue) - float(cost)
        }
        
        report.daily_data = data
        db.commit()
    except Exception as e:
        logging.error(f"Aggregation Error: {str(e)}")
    finally:
        db.close()

def send_daily_noti():
    db = database.SessionLocal()
    try:
        yesterday = date.today() - timedelta(days=1)
        yesterday_str = str(yesterday)
        revenue, cost = crud.get_daily_aggregated_data(db, yesterday)
        profit = revenue - cost
        
        msg = (
            f"📊 *Modern POS Report - {yesterday_str}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Revenue:* {crud.format_vnd(revenue)}\n"
            f"📉 *Cost:* {crud.format_vnd(cost)}\n"
            f"💎 *Profit:* {crud.format_vnd(profit)}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 _Automated Python POS System_"
        )
        crud.send_telegram_noti(db, msg)
    except Exception as e:
        logging.error(f"Notification Error: {str(e)}")
    finally:
        db.close()

scheduler = AsyncIOScheduler()
scheduler.add_job(update_daily_report, 'cron', hour=0, minute=30)
scheduler.add_job(send_daily_noti, 'cron', hour=8, minute=0)
