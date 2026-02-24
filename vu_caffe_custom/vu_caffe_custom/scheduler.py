import frappe
import json
from frappe.utils import today, add_days
from vu_caffe_custom.vu_caffe_custom.noti_telegram import trigger_daily_notification

@frappe.whitelist()
def update_daily_report():
    try:
        prev_day = add_days(today(), -1)
        prev_day_str = str(prev_day)
        
        # Calculate revenue from POS Invoice (grand_total or paid_amount)
        rev_result = frappe.db.sql("""
            SELECT SUM(grand_total) 
            FROM `tabPOS Invoice` 
            WHERE posting_date = %s AND docstatus = 1 AND status IN ('Paid', 'Consolidated')
        """, prev_day)
        rev = rev_result[0][0] or 0

        # Calculate cost (estimate or actual)
        # Using a default 40% margin calculation for simplicity, can be refined to use Stock Entry
        cost = float(rev) * 0.4 
        
        month_year = prev_day_str[:7] # YYYY-MM
        
        # Get or create report
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
                
        daily_data[prev_day_str] = {
            'revenue': float(rev), 
            'cost': float(cost),
            'profit': float(rev) - float(cost)
        }
        
        doc.daily_data = json.dumps(daily_data)
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        # Trigger notification
        trigger_daily_notification(prev_day_str, float(rev), float(cost))
        
    except Exception as e:
        frappe.log_error(f"Vu Caffe Daily Aggregation Error: {str(e)}", "VuCaffe Scheduler")
