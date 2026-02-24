import json

import frappe
from ury.ury_pos.api import getBranch


# Load JSON data or return as is if it's already a Python dictionary
def load_json(data):
    if isinstance(data, str):
        return json.loads(data)
    return data


# Create a list of order items from a list of input items
def create_order_items(items):
    order_items = []
    for item in items:
        order_item = {
            "item_code": item.get("item", item.get("item_code")),
            "qty": item["qty"],
            "item_name": item["item_name"],
            "comments": item.get("comment", item.get("comments", "")),
        }
        order_items.append(order_item)
    return order_items


# Create a KOT (Kitchen Order Ticket) document
def create_kot_doc(
    invoice_id,
    customer,
    restaurant_table,
    items,
    kot_type,
    comments,
    pos_profile_id,
    kot_naming_series,
    production,
):
    pos_invoice = frappe.get_doc("POS Invoice", invoice_id)
    order_number = pos_invoice.custom_ury_order_number
    is_aggregator = 1 if pos_invoice.order_type == "Aggregators" else 0

    kot_doc = frappe.get_doc(
        {
            "doctype": "URY KOT",
            "invoice": invoice_id,
            "restaurant_table": restaurant_table,
            "customer_name": customer,
            "pos_profile": pos_profile_id,
            "comments": comments,
            "type": kot_type,
            "naming_series": kot_naming_series,
            "production": production,
            "aggregator_id": pos_invoice.custom_aggregator_id,
            "is_aggregator": is_aggregator,
            "order_no": order_number,
        }
    )

    branch = getBranch()

    # Batch fetch menu info: room + restaurant in one go if table exists
    if restaurant_table:
        table_data = frappe.db.get_value(
            "URY Table",
            restaurant_table,
            ["restaurant_room", "restaurant"],
            as_dict=True,
        )
        room = table_data.get("restaurant_room") if table_data else None
        restaurant = table_data.get("restaurant") if table_data else None
        menu = frappe.db.get_value(
            "Menu for Room", {"room": room, "parent": restaurant}, "menu"
        )
    else:
        menu = frappe.db.get_value("URY Restaurant", {"branch": branch}, "active_menu")

    # Batch fetch all item courses in one query
    item_codes = [item["item_code"] for item in items]
    if menu and item_codes:
        course_rows = frappe.get_all(
            "URY Menu Item",
            filters={"item": ["in", item_codes], "parent": menu},
            fields=["item", "course"],
        )
        course_map = {row["item"]: row["course"] for row in course_rows}
    else:
        course_map = {}

    for item in items:
        kot_doc.append(
            "kot_items",
            {
                "item": item["item_code"],
                "item_name": item["item_name"],
                "quantity": item["qty"],
                "comments": item["comments"],
                "course": course_map.get(item["item_code"]),
            },
        )

    kot_doc.insert()
    kot_doc.submit()


# Function to get all production item groups for a given branch (batched)
def get_all_production_item_groups(branch):
    productions = frappe.db.get_all(
        "URY Production Unit", filters={"branch": branch}, fields=["name"]
    )
    if not productions:
        return set()

    production_names = [p["name"] for p in productions]

    # Single batch query instead of N queries in a loop
    all_groups = frappe.get_all(
        "URY Production Item Groups",
        filters={"parent": ["in", production_names], "parenttype": "URY Production Unit"},
        fields=["item_group"],
        order_by="idx",
    )
    return {row["item_group"] for row in all_groups}


# Build a map: production_name -> [item_groups] — batched
def get_production_item_group_map(production_names):
    rows = frappe.get_all(
        "URY Production Item Groups",
        filters={"parent": ["in", production_names], "parenttype": "URY Production Unit"},
        fields=["parent", "item_group"],
        order_by="idx",
    )
    result = {}
    for row in rows:
        result.setdefault(row["parent"], []).append(row["item_group"])
    return result


# Process items to create KOT documents
def process_items_for_kot(
    invoice_id,
    customer,
    restaurant_table,
    items,
    comments,
    pos_profile_id,
    kot_naming_series,
    kot_type,
):
    kot_items = create_order_items(items)
    pos_profile = frappe.get_doc("POS Profile", pos_profile_id)
    productions = frappe.db.get_all(
        "URY Production Unit", filters={"branch": pos_profile.branch}, fields=["name"]
    )

    if not productions:
        frappe.throw(
            "Create URY Production unit against POS Profile: %s " % pos_profile.name
        )

    production_names = [p["name"] for p in productions]

    # Batch fetch all item groups for all items in one query
    item_codes = [item["item_code"] for item in kot_items]
    item_group_map = {
        row["name"]: row["item_group"]
        for row in frappe.get_all(
            "Item",
            filters={"name": ["in", item_codes]},
            fields=["name", "item_group"],
        )
    }

    # Batch fetch production → item_group mapping
    prod_group_map = get_production_item_group_map(production_names)

    # Validate: warn about items not in any production
    all_production_item_groups = get_all_production_item_groups(pos_profile.branch)
    for item in kot_items:
        item_group = item_group_map.get(item["item_code"])
        if item_group and item_group not in all_production_item_groups:
            frappe.msgprint(
                f"Item group '{item_group}' for item '{item['item_code']}' is not in any production."
            )

    # Batch check existing KOTs for this invoice per production
    existing_kots = frappe.get_all(
        "URY KOT",
        filters={"invoice": invoice_id, "docstatus": 1},
        fields=["production"],
    )
    productions_with_kot = {kot["production"] for kot in existing_kots}

    for production in productions:
        prod_groups = set(prod_group_map.get(production["name"], []))
        production_items = [
            item for item in kot_items
            if item_group_map.get(item["item_code"]) in prod_groups
        ]

        if production_items:
            effective_kot_type = (
                "Order Modified"
                if production["name"] in productions_with_kot
                else kot_type
            )
            create_kot_doc(
                invoice_id,
                customer,
                restaurant_table,
                production_items,
                effective_kot_type,
                comments,
                pos_profile_id,
                kot_naming_series,
                production["name"],
            )


# Process items to create a cancel KOT document
def process_items_for_cancel_kot(
    invoice_id,
    customer,
    restaurant_table,
    items,
    comments,
    pos_profile_id,
    cancel_kot_naming_series,
    kot_type,
    invoiceItems,
):
    kot_items = create_order_items(items)
    pos_profile = frappe.get_doc("POS Profile", pos_profile_id)
    productions = frappe.db.get_all(
        "URY Production Unit", filters={"branch": pos_profile.branch}, fields=["name"]
    )

    production_names = [p["name"] for p in productions]

    # Batch fetch item groups for cancel items
    item_codes = [item["item_code"] for item in kot_items]
    item_group_map = {
        row["name"]: row["item_group"]
        for row in frappe.get_all(
            "Item",
            filters={"name": ["in", item_codes]},
            fields=["name", "item_group"],
        )
    }

    # Batch fetch production → item_group mapping
    prod_group_map = get_production_item_group_map(production_names)

    for production in productions:
        prod_groups = set(prod_group_map.get(production["name"], []))
        production_items = [
            item for item in kot_items
            if item_group_map.get(item["item_code"]) in prod_groups
        ]

        if production_items:
            create_cancel_kot_doc(
                invoice_id,
                restaurant_table,
                production_items,
                kot_type,
                customer,
                comments,
                pos_profile_id,
                cancel_kot_naming_series,
                invoiceItems,
                production["name"],
            )


# Create a cancel KOT document
def create_cancel_kot_doc(
    invoice_id,
    restaurant_table,
    cancel_items,
    kot_type,
    customer,
    comments,
    pos_profile_id,
    cancel_kot_naming_series,
    invoiceItems,
    production,
):
    # Single load of POS Invoice (not duplicated like before)
    pos_invoice = frappe.db.get_value(
        "POS Invoice",
        invoice_id,
        ["custom_ury_order_number", "order_type", "custom_aggregator_id"],
        as_dict=True,
    )
    order_number = pos_invoice.get("custom_ury_order_number")
    is_aggregator = 1 if pos_invoice.get("order_type") == "Aggregators" else 0

    # Batch fetch all original KOTs and their items in one go
    kot_list = frappe.db.get_list(
        "URY KOT",
        filters={
            "invoice": invoice_id,
            "type": ("in", ("New Order", "Order Modified")),
        },
        fields=["name"],
    )
    kot_names = [k["name"] for k in kot_list]

    # Batch fetch all KOT items for all KOTs
    all_kot_items = frappe.get_all(
        "URY KOT Items",
        filters={"parent": ["in", kot_names]},
        fields=["parent", "item"],
    )
    # Map: item_code -> first KOT name that contains it
    item_to_kot_map = {}
    for ki in all_kot_items:
        if ki["item"] not in item_to_kot_map:
            item_to_kot_map[ki["item"]] = ki["parent"]

    # Find original KOTs related to the cancel items
    original_kots = set()
    for cancel_item in cancel_items:
        kot_name = item_to_kot_map.get(cancel_item["item_code"])
        if kot_name:
            original_kots.add(kot_name)

    set_kots = ",".join(original_kots)

    kot_cancel_doc = frappe.get_doc(
        {
            "doctype": "URY KOT",
            "naming_series": cancel_kot_naming_series,
            "original_kot": set_kots,
            "restaurant_table": restaurant_table,
            "customer_name": customer,
            "type": kot_type,
            "invoice": invoice_id,
            "pos_profile": pos_profile_id,
            "comments": comments,
            "production": production,
            "is_aggregator": is_aggregator,
            "order_no": order_number,
        }
    )

    branch = getBranch()

    # Batch fetch table → room + restaurant
    if restaurant_table:
        table_data = frappe.db.get_value(
            "URY Table",
            restaurant_table,
            ["restaurant_room", "restaurant"],
            as_dict=True,
        )
        room = table_data.get("restaurant_room") if table_data else None
        restaurant = table_data.get("restaurant") if table_data else None
        menu = frappe.db.get_value(
            "Menu for Room", {"room": room, "parent": restaurant}, "menu"
        )
    else:
        menu = frappe.db.get_value("URY Restaurant", {"branch": branch}, "active_menu")

    # Batch fetch courses for all cancel items
    cancel_item_codes = [ci["item_code"] for ci in cancel_items]
    if menu and cancel_item_codes:
        course_rows = frappe.get_all(
            "URY Menu Item",
            filters={"item": ["in", cancel_item_codes], "parent": menu},
            fields=["item", "course"],
        )
        course_map = {row["item"]: row["course"] for row in course_rows}
    else:
        course_map = {}

    # Build invoiceItems lookup map for O(1) access
    invoice_item_map = {i["item_code"]: i for i in invoiceItems}

    for cancel_item in cancel_items:
        course = course_map.get(cancel_item["item_code"])
        original_item = invoice_item_map.get(cancel_item["item_code"])
        if original_item:
            kot_cancel_doc.append(
                "kot_items",
                {
                    "item": cancel_item["item_code"],
                    "item_name": cancel_item["item_name"],
                    "cancelled_qty": abs(int(cancel_item["qty"])),
                    "quantity": original_item["qty"],
                    "comments": cancel_item["comments"],
                    "course": course,
                },
            )

    kot_cancel_doc.insert()
    kot_cancel_doc.submit()


# Whitelisted function to handle KOT entry
@frappe.whitelist()
def kot_execute(
    invoice_id,
    customer,
    restaurant_table=None,
    current_items=[],
    previous_items=[],
    comments=None,
):
    current_items = load_json(current_items)
    previous_items = load_json(previous_items)
    new_invoice_items_array = create_order_items(previous_items)
    new_Order_items_array = create_order_items(current_items)

    final_array = compare_two_array(new_Order_items_array, new_invoice_items_array)
    removed_item = get_removed_items(new_invoice_items_array, new_Order_items_array)

    pos_invoice = frappe.get_doc("POS Invoice", invoice_id)
    pos_profile_id = pos_invoice.pos_profile
    pos_profile = frappe.get_doc("POS Profile", pos_profile_id)
    kot_naming_series = pos_profile.custom_kot_naming_series
    if kot_naming_series:
        cancel_kot_naming_series = "CNCL-" + kot_naming_series
    else:
        frappe.throw(
            "KOT Naming Series is mandatory for the auto creation of KOT.Ensure it is configured in the POS Profile: %s"
            % pos_profile.name
        )

    positive_qty_items = [item for item in final_array if int(item["qty"]) > 0]
    negative_qty_items = [item for item in final_array if int(item["qty"]) <= 0]
    total_cancel_items = negative_qty_items + removed_item
    if positive_qty_items:
        process_items_for_kot(
            invoice_id,
            customer,
            restaurant_table,
            positive_qty_items,
            comments,
            pos_profile_id,
            kot_naming_series,
            "New Order",
        )
    if total_cancel_items:
        process_items_for_cancel_kot(
            invoice_id,
            customer,
            restaurant_table,
            total_cancel_items,
            comments,
            pos_profile_id,
            cancel_kot_naming_series,
            "Partially cancelled",
            new_invoice_items_array,
        )


# Compare two arrays and return the items that are different
# Refactored from O(n²) to O(n) using a dict lookup
def compare_two_array(array_1, array_2):
    # Build a lookup map from array_2: item_code -> qty
    prev_qty_map = {}
    for y in array_2:
        prev_qty_map[y["item_code"]] = int(y["qty"])

    finalarray = []
    for x in array_1:
        code = x["item_code"]
        curr_qty = int(x["qty"])
        prev_qty = prev_qty_map.get(code)

        if prev_qty is None:
            # Item is new (not in previous)
            finalarray.append(x)
        elif curr_qty != prev_qty:
            # Quantity changed
            diff_item = dict(x)
            diff_item["qty"] = curr_qty - prev_qty
            finalarray.append(diff_item)
        # else: same qty → no change, skip

    return finalarray


# Get the items that have been removed from the second array compared to the first array
def get_removed_items(array_1, array_2):
    # O(n) using set lookup instead of O(n²) list comprehension
    current_codes = {x["item_code"] for x in array_2}
    return [obj for obj in array_1 if obj["item_code"] not in current_codes]
