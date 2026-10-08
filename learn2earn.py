"""Learn2Earn equipment lending system (standard library only)."""

LOW_STOCK_LIMIT = 3

# ---------------------------------------------------------------- data
resources = [
    {"id": "R001", "name": "Laptop", "category": "Electronics", "total": 10, "available": 10},
    {"id": "R002", "name": "Keyboard", "category": "Accessories", "total": 5, "available": 5},
    {"id": "R003", "name": "Headset", "category": "Accessories", "total": 3, "available": 3},
]
fellows = {"F001": "Ada", "F002": "John", "F003": "Grace"}
# Each record: {"fellow_id", "resource_id", "quantity", "returned"}
borrow_records = []


# ------------------------------------------------------------- helpers
def find_resource(resource_id):
    """Return the resource dict with this ID, or None."""
    for r in resources:
        if r["id"] == resource_id:
            return r
    return None


def is_positive_int(value):
    """True only for real ints > 0 (bool is rejected on purpose)."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def parse_positive_int(text):
    """Turn user text into a positive int, or return None."""
    text = text.strip()
    if text.isdigit() and int(text) > 0:
        return int(text)
    return None


def on_loan(fellow_id, resource_id):
    """Units this fellow currently holds of this resource."""
    return sum(
        rec["quantity"] - rec["returned"]
        for rec in borrow_records
        if rec["fellow_id"] == fellow_id and rec["resource_id"] == resource_id
    )


# ----------------------------------------------------------- inventory
def add_resource(resource_id, name, category, total):
    """Add a resource. Returns (ok, message)."""
    resource_id = resource_id.strip().upper()
    name, category = name.strip(), category.strip()
    if not resource_id or not name or not category:
        return False, "ID, name and category cannot be empty."
    if find_resource(resource_id):
        return False, f"Resource ID {resource_id} already exists."
    if not is_positive_int(total):
        return False, "Total units must be a positive whole number."
    resources.append({"id": resource_id, "name": name, "category": category,
                      "total": total, "available": total})
    return True, f"Added {name} ({resource_id}) with {total} units."


def list_resources(items=None):
    items = resources if items is None else items
    if not items:
        print("  (no resources)")
        return
    print(f"  {'ID':<6}{'Name':<12}{'Category':<13}{'Total':>6}{'Avail':>7}")
    for r in items:
        print(f"  {r['id']:<6}{r['name']:<12}{r['category']:<13}"
              f"{r['total']:>6}{r['available']:>7}")


# ----------------------------------------------------------- borrowing
def borrow(fellow_id, resource_id, quantity):
    """Validate EVERYTHING first, change state only at the very end."""
    fellow_id, resource_id = fellow_id.strip().upper(), resource_id.strip().upper()
    if fellow_id not in fellows:
        return False, f"Unknown fellow ID: {fellow_id}."
    res = find_resource(resource_id)
    if res is None:
        return False, f"Unknown resource ID: {resource_id}."
    if not is_positive_int(quantity):
        return False, "Quantity must be a positive whole number."
    if quantity > res["available"]:
        return False, (f"Only {res['available']} {res['name']} unit(s) available; "
                       f"cannot lend {quantity}.")
    # --- all checks passed: now mutate ---
    res["available"] -= quantity
    borrow_records.append({"fellow_id": fellow_id, "resource_id": resource_id,
                           "quantity": quantity, "returned": 0})
    return True, f"{fellows[fellow_id]} borrowed {quantity} x {res['name']}."


# ------------------------------------------------------------- returns
def return_item(fellow_id, resource_id, quantity):
    fellow_id, resource_id = fellow_id.strip().upper(), resource_id.strip().upper()
    if fellow_id not in fellows:
        return False, f"Unknown fellow ID: {fellow_id}."
    res = find_resource(resource_id)
    if res is None:
        return False, f"Unknown resource ID: {resource_id}."
    if not is_positive_int(quantity):
        return False, "Quantity must be a positive whole number."
    held = on_loan(fellow_id, resource_id)
    if quantity > held:
        return False, (f"{fellows[fellow_id]} only has {held} {res['name']} "
                       f"on loan; cannot return {quantity}.")
    # --- mutate: settle against the oldest loans first ---
    remaining = quantity
    for rec in borrow_records:
        if remaining == 0:
            break
        if rec["fellow_id"] == fellow_id and rec["resource_id"] == resource_id:
            take = min(remaining, rec["quantity"] - rec["returned"])
            rec["returned"] += take
            remaining -= take
    res["available"] += quantity
    return True, f"{fellows[fellow_id]} returned {quantity} x {res['name']}."


# -------------------------------------------------------------- search
def search_by_name(term):
    term = term.strip().lower()
    return [r for r in resources if term in r["name"].lower()]


def filter_by_category(category):
    category = category.strip().lower()
    return [r for r in resources if r["category"].lower() == category]


# ------------------------------------------------------------- reports
def units_borrowed(resource_id):
    return sum(rec["quantity"] - rec["returned"]
               for rec in borrow_records if rec["resource_id"] == resource_id)


def generate_report():
    total = sum(r["total"] for r in resources)
    available = sum(r["available"] for r in resources)
    borrowed = sum(units_borrowed(r["id"]) for r in resources)
    low = [r for r in resources if r["available"] < LOW_STOCK_LIMIT]
    per_resource = {r["id"]: units_borrowed(r["id"]) for r in resources}
    top = max(per_resource.values(), default=0)

    print("  ===== REPORT =====")
    print(f"  Total units:      {total}")
    print(f"  Available units:  {available}")
    print(f"  Borrowed units:   {borrowed}")
    print(f"  Low stock (<{LOW_STOCK_LIMIT} available):")
    if low:
        for r in low:
            print(f"    - {r['name']} ({r['available']})")
    else:
        print("    none")
    if top == 0:
        print("  Most borrowed:    nothing is currently on loan")
    else:
        leaders = [find_resource(rid) for rid, n in per_resource.items() if n == top]
        label = "Most borrowed:   " if len(leaders) == 1 else "Most borrowed (tie):"
        names = ", ".join(r["name"] for r in leaders)
        print(f"  {label} {names} ({top} units)")


# ---------------------------------------------------------------- demo
def run_demo():
    steps = [
        ("1. F001 borrows 2 laptops", lambda: borrow("F001", "R001", 2)),
        ("2. F002 borrows 3 keyboards", lambda: borrow("F002", "R002", 3)),
        ("3. F001 returns 1 laptop", lambda: return_item("F001", "R001", 1)),
        ("4. F003 requests 4 headsets", lambda: borrow("F003", "R003", 4)),
        ("5. F002 tries to return 4 keyboards", lambda: return_item("F002", "R002", 4)),
    ]
    for title, action in steps:
        ok, msg = action()
        print(f"{title}\n  {'OK' if ok else 'REJECTED'}: {msg}")
        list_resources()
    print("6. Search for 'LAPtop'")
    list_resources(search_by_name("LAPtop"))
    print("7. Report")
    generate_report()
    print("Extra invalid-input test: F999 borrows -2 of R001")
    ok, msg = borrow("F999", "R001", -2)
    print(f"  {'OK' if ok else 'REJECTED'}: {msg}")
    ok, msg = borrow("F001", "R001", -2)
    print(f"  {'OK' if ok else 'REJECTED'}: {msg}")
    list_resources()


# ---------------------------------------------------------------- menu
def ask_quantity(prompt="Quantity: "):
    qty = parse_positive_int(input(prompt))
    if qty is None:
        print("  Error: quantity must be a positive whole number.")
    return qty


def show(result):
    ok, msg = result
    print(f"  {'OK' if ok else 'ERROR'}: {msg}")


def main():
    menu = """
=== Learn2Earn Lending ===
1. Add resource      2. List resources   3. Borrow
4. Return            5. Search by name   6. Filter by category
7. Report            8. Run demonstration  0. Exit"""
    while True:
        print(menu)
        choice = input("Choose: ").strip()
        if choice == "1":
            rid, name, cat = input("ID: "), input("Name: "), input("Category: ")
            total = parse_positive_int(input("Total units: "))
            if total is None:
                print("  Error: total must be a positive whole number.")
            else:
                show(add_resource(rid, name, cat, total))
        elif choice == "2":
            list_resources()
        elif choice in ("3", "4"):
            fid, rid = input("Fellow ID: "), input("Resource ID: ")
            qty = ask_quantity()
            if qty is not None:
                show((borrow if choice == "3" else return_item)(fid, rid, qty))
        elif choice == "5":
            list_resources(search_by_name(input("Name contains: ")))
        elif choice == "6":
            list_resources(filter_by_category(input("Category: ")))
        elif choice == "7":
            generate_report()
        elif choice == "8":
            run_demo()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice. Enter a number from the menu.")


if __name__ == "__main__":
    main()