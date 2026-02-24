import frappe
import requests

def send_tele_noti(message, chat_id, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code != 200:
            frappe.log_error(f"Telegram API response error: {response.text}", "Telegram Notification Error")
    except Exception as e:
        frappe.log_error(f"Telegram noti connection fail: {str(e)}", "Telegram Notification Error")

def get_config_value(key):
    # Try getting from Vu Caffe Config Doctype first
    val = frappe.db.get_single_value('Vu Caffe Config', key)
    if val: return val
    
    # Fallback to site_config.json
    val = frappe.conf.get(key)
    if val: return val
    return None

def trigger_daily_notification(prev_day, rev, cost):
    token = get_config_value("tele_bot_token")
    chat_id = get_config_value("tele_chat_id")
    
    if not token or not chat_id:
        frappe.log_error("Missing tele_bot_token or tele_chat_id in configuration", "Telegram Notification Error")
        return
        
    profit = rev - cost
    message = (
        f"☕ *Vu Caffe - Báo Cáo Ngày {prev_day}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 *Doanh thu:* {rev:,.0f} ₫\n"
        f"📉 *Chi phí (ước tính):* {cost:,.0f} ₫\n"
        f"💎 *Lợi nhuận gộp:* {profit:,.0f} ₫\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📅 _Báo cáo tự động từ hệ thống URY ERP_"
    )
    
    send_tele_noti(message, chat_id, token)
