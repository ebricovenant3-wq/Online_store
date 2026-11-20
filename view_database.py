
import sqlite3
from pathlib import Path

database = Path(__file__).resolve().with_name("store.db")
connection = sqlite3.connect(database)

print("\n--- PRODUCTS ---")

products = connection.execute(
    "SELECT * FROM products"
).fetchall()

for product in products:
    print(product)

print("\n--- ORDERS ---")

orders = connection.execute(
    "SELECT * FROM orders"
).fetchall()

for order in orders:
    print(order)

print("\n--- ORDER ITEMS ---")

items = connection.execute(
    "SELECT * FROM order_items"
).fetchall()

for item in items:
    print(item)

print("\n--- RUNWAY PRODUCTS ---")
runway_products = connection.execute(
    "SELECT product_key, name, vendor, price, product_url FROM runway_products ORDER BY rowid"
).fetchall()
for product in runway_products:
    print(product)

print("\n--- RUNWAY LOOKS AND PIECES ---")
look_items = connection.execute(
    """SELECT looks.position, looks.name, runway_look_products.position,
              runway_products.name, runway_look_products.pin_left,
              runway_look_products.pin_top
       FROM runway_looks AS looks
       JOIN runway_look_products ON runway_look_products.look_id = looks.id
       JOIN runway_products ON runway_products.product_key = runway_look_products.product_key
       ORDER BY looks.position, runway_look_products.position"""
).fetchall()
for item in look_items:
    print(item)

print("\n--- RUNWAY SIZE VARIANTS ---")
variants = connection.execute(
    """SELECT runway_products.name, runway_variants.size,
              runway_variants.variant_id, runway_variants.available
       FROM runway_variants
       JOIN runway_products ON runway_products.product_key = runway_variants.product_key
       ORDER BY runway_products.rowid, runway_variants.position"""
).fetchall()
for variant in variants:
    print(variant)

connection.close()
