
#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and calculates the money collected.
Run: python3 reconcile.py
"""

import json
from datetime import datetime

latest_transactions = {}

# Read and clean the transaction data
with open("payments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)

            # Ignore records that are not JSON objects
            if not isinstance(event, dict):
                continue

            # Ignore events without a transaction ID
            txn_id = event.get("txn_id")
            if not txn_id:
                continue

            # Parse the UTC timestamp
            timestamp = datetime.fromisoformat(
                event["ts"].replace("Z", "+00:00")
            )

            # Keep only the latest attempt for each transaction
            previous = latest_transactions.get(txn_id)

            if previous is None or timestamp >= previous[0]:
                latest_transactions[txn_id] = (timestamp, event)

        except (json.JSONDecodeError, ValueError, TypeError, KeyError):
            # Ignore unreadable or malformed records
            continue

# Count successful transactions and calculate collected money
total = 0.0
count = 0

for timestamp, event in latest_transactions.values():
    if event.get("status") == "success":
        try:
            amount = float(
                str(event["amount"]).replace(",", "")
            )
        except (ValueError, TypeError, KeyError):
            continue

        total += amount
        count += 1

# Compare against the finance team's expected count
with open("expected.txt", "r", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(
        f"Check failed: counted {count} successful payments, "
        f"expected {expected}."
    )
    print(
        "Something in the data isn't being handled "
        "the way the README describes."
    )
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
