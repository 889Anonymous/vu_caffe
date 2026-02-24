import json

import frappe
from ury.ury_pos.api import getBranch
from frappe.utils import get_datetime


# Function to set order status in a KOT document
@frappe.whitelist()
def serve_kot(name, time):
    current_time = get_datetime()
    creation_time = frappe.db.get_value("URY KOT", name, "creation")

    production_time = current_time - creation_time
    production_time_minutes = production_time.total_seconds() / 60

    # Batch 3 writes into one round-trip using db_set
    frappe.db.set_value(
        "URY KOT",
        name,
        {
            "start_time_serv": time,
            "production_time": production_time_minutes,
            "order_status": "Served",
        },
    )


# Function to mark it as verified by a user in cancel type KOT
@frappe.whitelist()
def confirm_cancel_kot(name, user):
    frappe.db.set_value("URY KOT", name, {"verified": 1, "verified_by": user})


@frappe.whitelist(allow_guest=True)
def get_site_name():
    return {"site_name": frappe.local.site}


def _build_kot_response(order_status):
    """
    Shared logic for kot_list() and served_kot_list().
    Fetches KOTs with the given order_status for the current branch,
    returning full doc data in a single batch instead of N get_doc() calls.
    """
    today = frappe.utils.now()
    branch = getBranch()
    three_hours_ago = frappe.utils.add_to_date(today, hours=-3)

    # Single query for all POS Profile settings needed
    pos_profile_data = frappe.db.get_value(
        "POS Profile",
        {"branch": branch},
        ["custom_kot_warning_time", "custom_reset_order_number_daily", "custom_kot_alert"],
        as_dict=True,
    ) or {}

    kot_alert_time = pos_profile_data.get("custom_kot_warning_time")
    daily_order_number = pos_profile_data.get("custom_reset_order_number_daily")
    audio_alert = pos_profile_data.get("custom_kot_alert")

    # Fetch full KOT fields in one query — no N+1 loop needed
    kot_fields = [
        "name", "invoice", "restaurant_table", "customer_name", "pos_profile",
        "comments", "type", "naming_series", "production", "aggregator_id",
        "is_aggregator", "order_no", "order_status", "verified", "verified_by",
        "original_kot", "start_time_serv", "production_time", "creation",
    ]
    kot_list_raw = frappe.get_list(
        "URY KOT",
        fields=kot_fields,
        filters={
            "order_status": order_status,
            "branch": branch,
            "type": [
                "in",
                [
                    "New Order",
                    "Order Modified",
                    "Duplicate",
                    "Cancelled",
                    "Partially cancelled",
                ],
            ],
            "docstatus": 1,
            "verified": 0,
            "creation": (">=", three_hours_ago),
        },
        order_by="creation desc",
    )

    # Batch fetch all KOT Items for the fetched KOTs in one query
    kot_names = [k["name"] for k in kot_list_raw]
    all_kot_items = []
    if kot_names:
        all_kot_items = frappe.get_all(
            "URY KOT Items",
            filters={"parent": ["in", kot_names], "parenttype": "URY KOT"},
            fields=["parent", "item", "item_name", "quantity", "cancelled_qty", "comments", "course"],
            order_by="idx asc",
        )

    # Group items by parent KOT
    items_by_kot = {}
    for item in all_kot_items:
        items_by_kot.setdefault(item["parent"], []).append(item)

    # Assemble final list
    KOT = []
    for kot in kot_list_raw:
        kot_dict = dict(kot)
        kot_dict["kot_items"] = items_by_kot.get(kot["name"], [])
        KOT.append(kot_dict)

    return {
        "KOT": KOT,
        "Branch": branch,
        "kot_alert_time": kot_alert_time,
        "audio_alert": audio_alert,
        "daily_order_number": daily_order_number,
    }


@frappe.whitelist()
def kot_list():
    return _build_kot_response("Ready For Prepare")


@frappe.whitelist()
def served_kot_list():
    return _build_kot_response("Served")
