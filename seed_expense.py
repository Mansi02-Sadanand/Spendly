import random
import sys
from datetime import datetime, timedelta
from database.db import get_db

# Parse arguments
if len(sys.argv) != 4:
    print("Usage: /seed-expenses <user_id> <count> <months>")
    print("Example: /seed-expenses 1 50 6")
    sys.exit(1)

try:
    user_id = int(sys.argv[1])
    count = int(sys.argv[2])
    months = int(sys.argv[3])
except ValueError:
    print("Usage: /seed-expenses <user_id> <count> <months>")
    print("Example: /seed-expenses 1 50 6")
    sys.exit(1)

# Verify user exists
conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
user = cursor.fetchone()
if user is None:
    print(f"No user found with id {user_id}.")
    conn.close()
    sys.exit(1)

print(f"Seeding expenses for: {user['name']} (id: {user_id})")

# Category definitions with Indian context
CATEGORIES = {
    'Food': (50, 800, [
        'Lunch at office canteen', 'Street food at market', 'Family dinner',
        'Groceries from local store', 'Weekend brunch', 'Order from Swiggy',
        'Tea and snacks', 'Festival sweets', 'Tiffin service', 'Juice corner'
    ]),
    'Transport': (20, 500, [
        'Auto rickshaw fare', 'Metro card recharge', 'Bus pass',
        'Ola/Uber ride', 'Petrol fill', 'Bike maintenance',
        'Parking fee', 'Train ticket', 'Taxi to airport', 'Cycle rickshaw'
    ]),
    'Bills': (200, 3000, [
        'Electricity bill', 'Mobile recharge', 'Internet bill',
        'Water bill', 'DTH subscription', 'House maintenance',
        'Society charges', 'Gas cylinder', 'Property tax', 'Insurance premium'
    ]),
    'Health': (100, 2000, [
        'Doctor consultation', 'Medicine from pharmacy', 'Health checkup',
        'Gym membership', 'Yoga class', 'Dental visit',
        'Eye test', 'Lab tests', 'Physiotherapy', 'Ayurvedic medicine'
    ]),
    'Entertainment': (100, 1500, [
        'Movie tickets', 'OTT subscription', 'Cricket match tickets',
        'Concert entry', 'Gaming cafe', 'Amusement park',
        'Bowling night', 'Escape room', 'Karaoke bar', 'Food festival'
    ]),
    'Shopping': (200, 5000, [
        'Festival clothes', 'Jewellery purchase', 'Electronics gadget',
        'Home decor', 'Kitchen appliances', 'Footwear',
        'Bags and accessories', 'Cosmetics', 'Books', 'Gift items'
    ]),
    'Other': (50, 1000, [
        'Stationery items', 'Donation at temple', 'Pet supplies',
        'Car wash', 'Laundry service', 'Salon visit',
        'Plumber service', 'Electrician visit', 'Courier charges', 'Miscellaneous'
    ])
}

# Weighted category distribution (Food most common, Health/Entertainment least)
CATEGORY_WEIGHTS = {
    'Food': 25,
    'Transport': 15,
    'Bills': 20,
    'Health': 8,
    'Entertainment': 10,
    'Shopping': 15,
    'Other': 7
}

def generate_expense(months_back):
    """Generate a single random expense."""
    # Select category based on weights
    category = random.choices(
        list(CATEGORY_WEIGHTS.keys()),
        weights=list(CATEGORY_WEIGHTS.values())
    )[0]

    min_amt, max_amt, descriptions = CATEGORIES[category]
    amount = round(random.uniform(min_amt, max_amt), 2)
    description = random.choice(descriptions)

    # Generate random date within the past months
    days_back = random.randint(0, months_back * 30)
    date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    return (user_id, amount, category, date, description)

# Generate all expenses
expenses = [generate_expense(months) for _ in range(count)]

# Insert all expenses in a single transaction
try:
    cursor.executemany("""
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, expenses)
    conn.commit()
    print(f"\nSuccessfully inserted {count} expenses.")
except Exception as e:
    conn.rollback()
    print(f"Error inserting expenses: {e}")
    conn.close()
    sys.exit(1)

# Get date range of inserted expenses
cursor.execute("""
    SELECT MIN(date) as min_date, MAX(date) as max_date
    FROM expenses
    WHERE user_id = ?
""", (user_id,))
date_range = cursor.fetchone()
print(f"Date range: {date_range['min_date']} to {date_range['max_date']}")

# Show sample of 5 inserted records
cursor.execute("""
    SELECT id, amount, category, date, description
    FROM expenses
    WHERE user_id = ?
    ORDER BY date DESC
    LIMIT 5
""", (user_id,))
samples = cursor.fetchall()

print("\nSample expenses:")
print("-" * 70)
for s in samples:
    print(f"  ID: {s['id']}, Rs {s['amount']:.2f} ({s['category']}) - {s['date']}: {s['description']}")

conn.close()
