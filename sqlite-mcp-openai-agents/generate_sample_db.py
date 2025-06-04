#!/usr/bin/env python3
import sqlite3
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

# Define the database path
DB_PATH = Path("sample.db")

# Create parent directory if it doesn't exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Remove existing database if it exists
if DB_PATH.exists():
    print(f"Removing existing database at {DB_PATH}")
    os.remove(DB_PATH)

# Connect to database
print(f"Creating database at {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create metrics table
print("Creating metrics table")
cursor.execute('''
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Create users table
print("Creating users table")
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE
)
''')

# Create products table
print("Creating products table")
cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Create orders table
print("Creating orders table")
cursor.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Create order_items table
print("Creating order_items table")
cursor.execute('''
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
)
''')

# Sample metrics data
print("Inserting sample metrics data")
metrics_data = []
current_time = datetime.now()

# Generate 50 metrics entries with timestamps over the last 24 hours
for i in range(50):
    metrics_data.append((
        random.choice(['cpu_usage', 'memory_usage', 'disk_usage', 'network_in', 'network_out']),
        random.uniform(1, 100),
        (current_time - timedelta(hours=i % 24)).strftime('%Y-%m-%d %H:%M:%S')
    ))

cursor.executemany(
    "INSERT INTO metrics (name, value, timestamp) VALUES (?, ?, ?)",
    metrics_data
)

# Sample users data
print("Inserting sample users data")
users_data = [
    ('john_doe', 'john.doe@example.com', '2023-01-15 12:30:45', '2023-06-20 08:15:30', True),
    ('jane_smith', 'jane.smith@example.com', '2023-02-20 10:15:20', '2023-06-19 14:20:10', True),
    ('bob_johnson', 'bob.johnson@example.com', '2023-03-10 09:45:12', '2023-06-15 11:30:45', True),
    ('alice_williams', 'alice.williams@example.com', '2023-04-05 15:20:30', '2023-06-18 09:10:25', True),
    ('charlie_brown', 'charlie.brown@example.com', '2023-05-12 14:10:35', '2023-06-10 16:45:15', False)
]

cursor.executemany(
    "INSERT INTO users (username, email, created_at, last_login, is_active) VALUES (?, ?, ?, ?, ?)",
    users_data
)

# Sample products data
print("Inserting sample products data")
products_data = [
    ('Laptop', 'Electronics', 1299.99, 10, '2023-01-10 09:00:00', '2023-06-01 10:15:30'),
    ('Smartphone', 'Electronics', 699.99, 15, '2023-02-15 10:30:00', '2023-06-05 11:20:45'),
    ('Headphones', 'Electronics', 149.99, 30, '2023-03-20 11:45:00', '2023-06-10 14:30:20'),
    ('T-shirt', 'Clothing', 19.99, 100, '2023-04-25 13:00:00', '2023-06-15 09:45:10'),
    ('Jeans', 'Clothing', 49.99, 50, '2023-05-30 14:15:00', '2023-06-20 15:10:35'),
    ('Coffee Maker', 'Appliances', 89.99, 20, '2023-06-05 15:30:00', '2023-06-25 12:25:40'),
    ('Blender', 'Appliances', 49.99, 25, '2023-06-10 16:45:00', '2023-06-30 16:40:15'),
    ('Monitor', 'Electronics', 249.99, 12, '2023-06-15 09:00:00', '2023-07-01 10:15:30')
]

cursor.executemany(
    "INSERT INTO products (name, category, price, stock, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
    products_data
)

# Sample orders data
print("Inserting sample orders data")
orders_data = [
    (1, 1299.99, 'Completed', '2023-06-01 10:30:45'),
    (1, 149.99, 'Completed', '2023-06-10 14:15:20'),
    (2, 749.98, 'Processing', '2023-06-15 09:45:30'),
    (3, 89.99, 'Shipped', '2023-06-18 11:20:15'),
    (4, 269.98, 'Pending', '2023-06-20 16:10:25'),
    (2, 1349.97, 'Completed', '2023-06-22 12:30:40'),
    (5, 49.99, 'Cancelled', '2023-06-25 10:05:15')
]

cursor.executemany(
    "INSERT INTO orders (user_id, total_amount, status, created_at) VALUES (?, ?, ?, ?)",
    orders_data
)

# Sample order items data
print("Inserting sample order items data")
order_items_data = [
    (1, 1, 1, 1299.99),  # Order 1: 1 Laptop
    (2, 3, 1, 149.99),   # Order 2: 1 Headphones
    (3, 2, 1, 699.99),   # Order 3: 1 Smartphone
    (3, 5, 1, 49.99),    # Order 3: 1 Jeans
    (4, 6, 1, 89.99),    # Order 4: 1 Coffee Maker
    (5, 8, 1, 249.99),   # Order 5: 1 Monitor
    (5, 4, 1, 19.99),    # Order 5: 1 T-shirt
    (6, 1, 1, 1299.99),  # Order 6: 1 Laptop
    (6, 7, 1, 49.99),    # Order 6: 1 Blender
    (7, 7, 1, 49.99)     # Order 7: 1 Blender
]

cursor.executemany(
    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
    order_items_data
)

# Create a view for order analytics
print("Creating order_analytics view")
cursor.execute('''
CREATE VIEW order_analytics AS
SELECT 
    o.id as order_id,
    u.username,
    p.name as product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) as item_total,
    o.status,
    o.created_at
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
''')

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Sample database created at {DB_PATH}")
print("Tables created: metrics, users, products, orders, order_items")
print("Views created: order_analytics")
print(f"Total metrics records: {len(metrics_data)}")
print(f"Total users records: {len(users_data)}")
print(f"Total products records: {len(products_data)}")
print(f"Total orders records: {len(orders_data)}")
print(f"Total order items records: {len(order_items_data)}") 