import frappe
import requests

def send_tele_noti(message, chat_id, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        frappe.log_error(f"Telegram noti fail: {str(e)}", "Telegram Notification Error")

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
        frappe.log_error("Missing tele_bot_token or tele_chat_id in site_config.json", "Telegram Notification Error")
        return
        
    profit = rev - cost
    message = f"Cà phê Vu Caffe - Báo Cáo Ngày {prev_day}\n- Doanh thu: {rev:,.0f} ₫\n- Chi phí (ước tính): {cost:,.0f} ₫\n- Lợi nhuận gộp: {profit:,.0f} ₫"
    
    send_tele_noti(message, chat_id, token)
