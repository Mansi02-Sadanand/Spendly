import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

DATABASE_PATH = Path(__file__).parent.parent / "spendly.db"


def get_db():
    """Return a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def create_user(name: str, email: str, password: str) -> int:
    """Create a new user with hashed password.

    Returns the new user's id.
    Raises sqlite3.IntegrityError if email already exists.
    """
    conn = get_db()
    cursor = conn.cursor()

    try:
        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """, (name, email, password_hash))

        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    finally:
        conn.close()


def get_user_by_email(email: str):
    """Fetch a user by email address.

    Returns a dict-like row if found, None otherwise.
    """
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, name, email, password_hash, created_at
            FROM users
            WHERE email = ?
        """, (email,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    """Fetch a user by ID.

    Returns a dict-like row if found, None otherwise.
    """
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, name, email, password_hash, created_at
            FROM users
            WHERE id = ?
        """, (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def seed_db():
    """Insert sample data for development."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Demo user with hashed password
    password_hash = generate_password_hash("demo123")
    cursor.execute("""
        INSERT INTO users (name, email, password_hash) VALUES
        ('Demo User', 'demo@spendly.com', ?)
    """, (password_hash,))

    # Get the demo user's ID
    cursor.execute("SELECT id FROM users WHERE email = 'demo@spendly.com'")
    user_id = cursor.fetchone()[0]

    # 8 sample expenses across all categories
    expenses = [
        (user_id, 45.50, 'Food', '2026-04-01', 'Lunch at restaurant'),
        (user_id, 25.00, 'Transport', '2026-04-02', 'Uber ride'),
        (user_id, 120.00, 'Bills', '2026-04-03', 'Electric bill'),
        (user_id, 35.00, 'Health', '2026-04-05', 'Pharmacy'),
        (user_id, 60.00, 'Entertainment', '2026-04-07', 'Movie tickets'),
        (user_id, 150.00, 'Shopping', '2026-04-10', 'Clothing'),
        (user_id, 80.00, 'Other', '2026-04-12', 'Miscellaneous'),
        (user_id, 55.00, 'Food', '2026-04-15', 'Grocery shopping'),
    ]

    cursor.executemany("""
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, expenses)

    conn.commit()
    conn.close()
