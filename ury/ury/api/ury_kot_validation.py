import frappe
import json

from frappe.utils import get_datetime, datetime


def kotValidationThread():
    current_datetime = get_datetime()
    one_minute_ago = current_datetime - datetime.timedelta(minutes=1)
    five_minutes_ago = current_datetime - datetime.timedelta(minutes=5)

    # Get a list of unprocessed invoices within the last 5 minutes
    invoice_list = get_unprocessed_invoices(five_minutes_ago, one_minute_ago)

    if not invoice_list:
        return

    # Batch load all POS Invoices in one query
    invoice_names = [inv["name"] for inv in invoice_list]

    # Batch fetch all needed POS Invoice fields
    pos_invoices = {
        doc["name"]: doc
        for doc in frappe.get_all(
            "POS Invoice",
            filters={"name": ["in", invoice_names]},
            fields=["name", "pos_profile", "waiter", "branch", "restaurant_table", "creation", "custom_ury_order_number"],
        )
    }

    # Batch fetch unique POS Profiles
    pos_profile_names = list({inv["pos_profile"] for inv in pos_invoices.values() if inv.get("pos_profile")})
    pos_profiles = {
        doc["name"]: doc
        for doc in frappe.get_all(
            "POS Profile",
            filters={"name": ["in", pos_profile_names]},
            fields=["name", "kot_naming_series", "branch"],
        )
    }

    # Batch fetch all KOTs for these invoices in one query
    existing_kots = frappe.get_all(
        "URY KOT",
        filters={"invoice": ["in", invoice_names]},
        fields=["name", "invoice"],
    )
    invoices_with_kots = {kot["invoice"] for kot in existing_kots}

    # Process each invoice using pre-fetched data
    for invoice_data in pos_invoices.values():
        if invoice_data["name"] in invoices_with_kots:
            continue  # KOT already exists, skip

        pos_profile_data = pos_profiles.get(invoice_data.get("pos_profile"))
        if not pos_profile_data:
            continue

        process_invoice_batch(invoice_data, pos_profile_data)


# Function to fetch unprocessed invoices within a time range
def get_unprocessed_invoices(start_time, end_time):
    return frappe.db.sql(
        """
        SELECT name, creation
        FROM `tabPOS Invoice`
        WHERE docstatus = 0
            AND creation BETWEEN %s AND %s
        """,
        (start_time, end_time),
        as_dict=True,
    )


# Refactored: accepts pre-fetched dicts to avoid repeated DB calls
def process_invoice_batch(invoice_data, pos_profile_data):
    branch = invoice_data.get("branch") or pos_profile_data.get("branch")
    if not branch:
        return

    kot_naming_series = pos_profile_data.get("kot_naming_series")
    waiter = invoice_data.get("waiter")

    # Batch fetch productions for branch
    productions = get_productions_for_branch(branch)
    if not productions:
        return

    production_names = [p["name"] for p in productions]

    # Batch fetch all production item groups in one query
    production_item_groups_rows = frappe.get_all(
        "URY Production Item Groups",
        filters={"parent": ["in", production_names], "parenttype": "URY Production Unit"},
        fields=["parent", "item_group"],
    )
    # Map: production_name -> set of item_groups
    production_to_groups = {}
    for row in production_item_groups_rows:
        production_to_groups.setdefault(row["parent"], set()).add(row["item_group"])

    # Fetch invoice items
    invoice_items = frappe.get_all(
        "POS Invoice Item",
        filters={"parent": invoice_data["name"]},
        fields=["item_code", "item_name", "qty"],
    )
    if not invoice_items:
        return

    # Batch fetch item groups for all items
    item_codes = [i["item_code"] for i in invoice_items]
    item_group_map = {
        row["name"]: row["item_group"]
        for row in frappe.get_all(
            "Item",
            filters={"name": ["in", item_codes]},
            fields=["name", "item_group"],
        )
    }

    for production in productions:
        prod_groups = production_to_groups.get(production["name"], set())
        production_items = [
            i for i in invoice_items
            if item_group_map.get(i["item_code"]) in prod_groups
        ]
        if production_items:
            create_kot(
                invoice_data,
                pos_profile_data,
                kot_naming_series,
                production_items,
                waiter,
                production["name"],
            )


# Function to fetch production units for a branch
def get_productions_for_branch(branch):
    return frappe.get_all(
        "URY Production Unit", filters={"branch": branch}, fields=["name"]
    )


# Function to create a KOT — accepts pre-fetched invoice_data dict
def create_kot(
    invoice_data, pos_profile_data, kot_naming_series, production_items, owner, production_name
):
    kotdoc = frappe.new_doc("URY KOT")
    kotdoc.update(
        {
            "invoice": invoice_data["name"],
            "restaurant_table": invoice_data.get("restaurant_table"),
            "naming_series": kot_naming_series,
            "type": "Duplicate",
            "pos_profile": pos_profile_data["name"],
            "customer_name": invoice_data.get("waiter"),
            "production": production_name,
            "order_no": invoice_data.get("custom_ury_order_number"),
        }
    )

    for pr in production_items:
        kotdoc.append(
            "kot_items",
            {"item": pr["item_code"], "item_name": pr["item_name"], "quantity": pr["qty"]},
        )

    kotdoc.insert()
    kotdoc.submit()
    kotdoc.db_set("owner", owner)

    # Create a KOT Log entry
    create_kot_log(kotdoc, invoice_data["name"])


# Function to create a KOT Log entry
def create_kot_log(kotdoc, invoice_name):
    # Use cached value instead of re-fetching the full POS Invoice doc
    invoice_creation = frappe.db.get_value("POS Invoice", invoice_name, "creation")
    KOTLog = frappe.new_doc("URY KOT Error Log")
    KOTLog.update(
        {
            "kot": kotdoc.name,
            "invoice": invoice_name,
            "invoice_creation_time": invoice_creation,
        }
    )
    KOTLog.insert()
