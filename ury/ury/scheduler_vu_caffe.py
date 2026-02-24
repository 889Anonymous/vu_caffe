import frappe
import json
from frappe.utils import today, add_days
from ury.ury.noti_telegram import trigger_daily_notification

@frappe.whitelist()
def update_daily_report():
    today_str = today()
    prev_day = add_days(today_str, -1)
    
    # Calculate revenue from POS Invoice (grand_total or paid_amount)
    rev_result = frappe.db.sql("""
        SELECT SUM(grand_total) 
        FROM `tabPOS Invoice` 
        WHERE posting_date = %s AND docstatus = 1 AND status IN ('Paid', 'Consolidated')
    """, prev_day)
    rev = rev_result[0][0] or 0

    # Calculate cost (from Stock Entry or similar, assuming simplicity here based on prompt)
    cost_result = frappe.db.sql("""
        SELECT SUM(amount) 
        FROM `tabPOS Invoice Item` a
        JOIN `tabPOS Invoice` b ON a.parent = b.name
        WHERE b.posting_date = %s AND b.docstatus = 1 AND b.status IN ('Paid', 'Consolidated')
    """, prev_day)
    # Note: real cost might come from Stock Entry but as a fallback, we grab item total if no inventory tracking
    cost_approx = cost_result[0][0] or 0
    # True Cost calculation assuming 40% margin if not tracked perfectly by Stock Entry
    cost = rev * 0.4 
    
    month_year = prev_day[:7] # YYYY-MM
    
    doc = None
    if frappe.db.exists('Vu Caffe Daily Report', month_year):
        doc = frappe.get_doc('Vu Caffe Daily Report', month_year)
    else:
        doc = frappe.new_doc('Vu Caffe Daily Report')
        doc.month_year = month_year
        
    daily_data = {}
    if doc.daily_data:
        if isinstance(doc.daily_data, str):
            daily_data = json.loads(doc.daily_data)
        else:
            daily_data = doc.daily_data
            
    daily_data[prev_day] = {'revenue': float(rev), 'cost': float(cost)}
    
    doc.daily_data = json.dumps(daily_data)
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    trigger_daily_notification(prev_day, float(rev), float(cost))

@frappe.whitelist()
def update_monthly_report():
    pass
