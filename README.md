# Learn2Earn Equipment Lending System

A command-line Python program that tracks equipment Learn2Earn lends to its fellows. It stores inventory, issues items, accepts returns, searches and filters resources, and produces accurate reports.

Python standard library only. No frameworks, databases, or third-party packages.

## Requirements

- Python 3.8 or newer

## Run it

```bash
python learn2earn.py
```

On some systems use `python3` instead of `python`.

## Menu options

| Option | What it does |
|--------|--------------|
| 1 | Add a resource (duplicate IDs are rejected) |
| 2 | List all resources |
| 3 | Borrow: a fellow takes units of a resource |
| 4 | Return: a fellow gives units back |
| 5 | Search resources by name (case-insensitive) |
| 6 | Filter resources by category |
| 7 | Show the report |
| 8 | Run the required 7-step demonstration |
| 0 | Exit |

The menu loops until you choose `0`.

## Starting data

- Resources: R001 Laptop (10), R002 Keyboard (5), R003 Headset (3)
- Fellows: F001 Ada, F002 John, F003 Grace

## How it works

**Inventory** is a list of dictionaries with `id`, `name`, `category`, `total` and `available`.

**Loans** are a list of `borrow_records`. Each record stores `fellow_id`, `resource_id`, `quantity` and `returned`. Units a fellow currently holds = `quantity - returned`, summed over their records.

**Validate first, change later.** `borrow()` and `return_item()` run every check before touching any data, so a rejected request never changes stock or records. Each returns `(ok, message)`.

### Main functions

- `add_resource` adds a resource and rejects duplicates and invalid totals
- `borrow` checks fellow ID, resource ID, quantity and stock, then logs the loan
- `return_item` only accepts quantities the fellow currently has on loan
- `search_by_name` and `filter_by_category` are case-insensitive
- `generate_report` shows total, available and borrowed units, low stock (fewer than 3 available) and the most-borrowed resource, listing all resources in a tie
- `run_demo` runs the seven required demonstration steps plus invalid-input tests

## Report contents

- Total units
- Available units
- Units currently borrowed
- Resources with fewer than 3 available units
- Resource with the most units currently borrowed (all leaders if tied)

## Expected demonstration results

| Step | Action | Result |
|------|--------|--------|
| 1 | F001 borrows 2 laptops | Laptop available = 8 |
| 2 | F002 borrows 3 keyboards | Keyboard available = 2 |
| 3 | F001 returns 1 laptop | Laptop available = 9 |
| 4 | F003 requests 4 headsets | Rejected, stock unchanged |
| 5 | F002 returns 4 keyboards | Rejected, stock unchanged |
| 6 | Search `LAPtop` | Finds Laptop |
| 7 | Report | Total 18, available 14, borrowed 4, Keyboard low stock (2), Keyboard most borrowed (3) |

## Known limitations

- Data is held in memory only, so it is lost when the program exits.
- Fellows cannot be added from the menu.
- Returns are applied to a fellow's oldest loans first, with no due dates or overdue tracking.

## Possible improvement

Save `resources` and `borrow_records` to a JSON file on exit with `json.dump`, and reload them at startup with `json.load`.
