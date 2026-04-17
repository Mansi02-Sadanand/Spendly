import random
from datetime import datetime
from werkzeug.security import generate_password_hash
from database.db import get_db

# Common Indian first names across regions
FIRST_NAMES = [
    # North Indian
    "Rahul", "Amit", "Rajesh", "Priya", "Neha", "Anjali", "Vikram", "Deepak",
    "Sunita", "Manoj", "Kavita", "Suresh", "Pooja", "Rakesh", "Meena",
    # South Indian
    "Arjun", "Karthik", "Lakshmi", "Divya", "Venkat", "Meera", "Prasad", "Kavya",
    "Ramesh", "Anita", "Murthy", "Shanti", "Gopal", "Radha", "Krishnan",
    # East/West Indian
    "Sneha", "Rohan", "Isha", "Aditya", "Pallavi", "Siddharth", "Ritika",
    "Ananya", "Vivek", "Tarun", "Megha", "Harsh", "Prachi", "Nikhil"
]

# Common Indian surnames
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Agarwal", "Singh", "Kumar", "Patel", "Desai",
    "Reddy", "Nair", "Iyer", "Rao", "Menon", "Pillai", "Chatterjee", "Banerjee",
    "Mukherjee", "Das", "Ghosh", "Joshi", "Deshmukh", "Patil", "Kulkarni",
    "Hegde", "Bhat", "Kamath", "Naik", "Prabhu", "Fernandes", "D Souza"
]

def generate_unique_email():
    """Generate a unique email that doesn't exist in the database."""
    conn = get_db()
    cursor = conn.cursor()

    max_attempts = 100
    for _ in range(max_attempts):
        first_name = random.choice(FIRST_NAMES).lower()
        last_name = random.choice(LAST_NAMES).lower()
        number = random.randint(10, 99)

        email = f"{first_name}.{last_name}{number}@gmail.com"

        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone() is None:
            conn.close()
            return email

    conn.close()
    raise Exception("Could not generate unique email after multiple attempts")

def create_user():
    """Create a new user with random Indian name and insert into database."""
    # Generate random name
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"

    # Generate unique email
    email = generate_unique_email()

    # Hash password
    password_hash = generate_password_hash("password123")

    # Get current datetime
    created_at = datetime.now().isoformat()

    # Insert into database
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    """, (name, email, password_hash, created_at))

    conn.commit()

    # Get the inserted user's ID
    user_id = cursor.lastrowid

    conn.close()

    # Print confirmation
    print(f"User created successfully!")
    print(f"id: {user_id}")
    print(f"name: {name}")
    print(f"email: {email}")

if __name__ == "__main__":
    create_user()
