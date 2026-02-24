import re

import frappe
from frappe import _

# Unicode-aware pattern: allows Vietnamese, other accented chars, and common punctuation
_SEARCH_TERM_PATTERN = re.compile(r"^[\w\s\-_@.'\u00C0-\u024F\u1E00-\u1EFF]+$", re.UNICODE)
_SEARCH_MAX_LENGTH = 100


def validate_search_input(search_term):
    """Validate and sanitize search input. Supports Vietnamese and Unicode characters."""
    if not search_term:
        return ""

    # Length validation
    if len(search_term) > _SEARCH_MAX_LENGTH:
        frappe.throw(_(f"Search term too long (max {_SEARCH_MAX_LENGTH} characters)"))

    # Unicode-aware character whitelist — allows tiếng Việt có dấu, Latin extended, etc.
    if not _SEARCH_TERM_PATTERN.match(search_term):
        frappe.throw(_("Invalid characters in search term"))

    return search_term


@frappe.whitelist()
def overrided_past_order_list(search_term, status, limit=20):
    user = frappe.session.user
    search_term = validate_search_input(search_term)

    branch_name = None
    room_name = None

    if user != "Administrator":
        sql_query = """
            SELECT b.branch, a.room
            FROM `tabURY User` AS a
            INNER JOIN `tabBranch` AS b ON a.parent = b.name
            WHERE a.user = %s
        """
        branch_array = frappe.db.sql(sql_query, user, as_dict=True)

        if not branch_array:
            frappe.throw("User is not Associated with any Branch.Please refresh Page")

        branch_name = branch_array[0].get("branch")
        room_name = branch_array[0].get("room")

    fields = [
        "name",
        "grand_total",
        "currency",
        "customer",
        "posting_time",
        "posting_date",
        "restaurant_table",
        "invoice_printed",
    ]

    invoice_list = []
    updated_list = []

    if search_term and status:
        invoices_by_customer = frappe.db.get_all(
            "POS Invoice",
            filters={
                "customer": ["like", "%{}%".format(frappe.db.escape(search_term))],
                "status": status,
            },
            fields=fields,
        )
        invoices_by_name = frappe.db.get_all(
            "POS Invoice",
            filters={"name": ["like", "%{}%".format(frappe.db.escape(search_term))], "status": status},
            fields=fields,
        )
        invoice_list = invoices_by_customer + invoices_by_name
        updated_list = invoice_list

    elif status:
        is_admin = user == "Administrator"

        if status == "To Bill":
            filters = {"status": "Draft"}
            if not is_admin:
                filters.update({"branch": branch_name, "custom_restaurant_room": room_name})

            invoice_list = frappe.db.get_all("POS Invoice", filters=filters, fields=fields)
            updated_list = [
                inv for inv in invoice_list
                if inv.restaurant_table and inv.invoice_printed == 0
            ]
        else:
            filters = {"status": status}
            if not is_admin:
                filters.update({"branch": branch_name, "custom_restaurant_room": room_name})

            invoice_list = frappe.db.get_all("POS Invoice", filters=filters, fields=fields)
            updated_list = [
                inv for inv in invoice_list
                if not inv.restaurant_table or inv.invoice_printed == 1
            ]

    return updated_list
