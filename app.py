
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
import json
import os
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-dev-secret-key")

DATABASE = Path(__file__).resolve().with_name("store.db")


# CONNECT TO DATABASE
def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# CREATE DATABASE TABLES
def initialize_database():
    connection = get_db()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            total INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS runway_products (
            product_key TEXT PRIMARY KEY,
            catalog_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            vendor TEXT NOT NULL,
            price REAL NOT NULL,
            image_url TEXT NOT NULL,
            product_url TEXT NOT NULL,
            option_legend TEXT NOT NULL,
            sizes_json TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            colors_json TEXT NOT NULL DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS runway_variants (
            variant_id INTEGER PRIMARY KEY,
            product_key TEXT NOT NULL,
            size TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1,
            position INTEGER NOT NULL,
            FOREIGN KEY (product_key) REFERENCES runway_products(product_key)
        );

        CREATE TABLE IF NOT EXISTS runway_looks (
            id INTEGER PRIMARY KEY,
            position INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            model_image TEXT NOT NULL,
            original_image TEXT NOT NULL,
            description TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS runway_look_products (
            look_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            product_key TEXT NOT NULL,
            pin_left REAL NOT NULL,
            pin_top REAL NOT NULL,
            is_new INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (look_id, position),
            FOREIGN KEY (look_id) REFERENCES runway_looks(id) ON DELETE CASCADE,
            FOREIGN KEY (product_key) REFERENCES runway_products(product_key)
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    product_columns = {
        column["name"] for column in connection.execute("PRAGMA table_info(runway_products)")
    }
    if "description" not in product_columns:
        connection.execute("ALTER TABLE runway_products ADD COLUMN description TEXT NOT NULL DEFAULT ''")
    if "colors_json" not in product_columns:
        connection.execute("ALTER TABLE runway_products ADD COLUMN colors_json TEXT NOT NULL DEFAULT '[]'")

    seed_runway_catalog(connection)

    # Add sample products if the store is empty
    count = connection.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    if count == 0:
        products = [
            ("Luxury Shirt", 5000, 20),
            ("Classic Shoes", 15000, 10),
            ("School Bag", 8000, 15),
            ("Wrist Watch", 12000, 8)
        ]

        connection.executemany(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            products
        )

    connection.commit()
    connection.close()


def seed_runway_catalog(connection):
    products = [
        ("air-jordan", "tatum-5-orbit-copy", "Air Jordan 12 Retro", "Nikey | Password: 1", 149, "source-tatum-5-orbit-copy.webp", "tatum-5-orbit-copy", "Shoe size", ["40", "41", "42", "43", "44", "45", "46"], [57015167025457, 57015167058225, 57015167090993, 57015167123761, 57015167156529, 57015167189297, 57015167222065], "A low-top sneaker with a light grey and cream finish, dark brown detailing, and small pink accents.", [{"name":"Light grey","hex":"#b9b9b2"},{"name":"Cream","hex":"#e7dfcf"},{"name":"Dark brown","hex":"#49382f"},{"name":"Pink","hex":"#e7a6a8"}]),
        ("tshirt", "tshirt", "Tshirt", "Nike", 199, "source-tshirt.webp", "tshirt", "Size", ["S", "L", "M", "XL"], [56835911582001, 56835911614769, 56835911647537, 56835911680305], "A black jersey tee with a pink rib collar and a bold white graphic print.", [{"name":"Black","hex":"#171717"},{"name":"Pink","hex":"#db7c91"},{"name":"White","hex":"#f2f0eb"}]),
        ("sweatshirt", "sweatshirt", "Sweatshirt", "Nike", 199, "source-sweatshirt.webp", "sweatshirt", "Size", ["S", "L", "M", "XL"], [56835806396721, 56835806429489, 56835806462257, 56835806495025], "A relaxed beige crew-neck sweatshirt with a soft neutral finish and a small chest print.", [{"name":"Beige","hex":"#d7cbbb"},{"name":"Cream","hex":"#eee9df"}]),
        ("tatum", "tatum-5-orbit", "Tatum 5 Orbit", "Nikey | Password: 1", 149, "source-tatum-5-orbit.webp", "tatum-5-orbit", "Shoe size", ["40", "41", "42", "43", "44", "45", "46"], [57015166730545, 57015166763313, 57015166796081, 57015166828849, 57015166861617, 57015166894385, 57015166927153], "A court-inspired white leather sneaker with a black collar, grey patterned panels, and red accents.", [{"name":"White","hex":"#f0eee8"},{"name":"Black","hex":"#191919"},{"name":"Grey","hex":"#92918d"},{"name":"Red","hex":"#b3282f"}]),
        ("hoodie-black", "hoodie-black", "Hoodie Black", "Nike", 199, "source-hoodie-black.webp", "hoodie-black", "Size", ["S", "L", "M", "XL"], [56836251681073, 56836251713841, 56836251746609, 56836251779377], "A black hoodie with a relaxed fit and a subtle grey starburst graphic.", [{"name":"Black","hex":"#171717"},{"name":"Charcoal","hex":"#454545"}]),
        ("sweatshirt-plus", "sweatshirt-plus", "Sweatshirt Plus", "Nike", 199, "source-sweatshirt-plus.webp", "sweatshirt-plus", "Size", ["S", "L", "M", "XL"], [56836143743281, 56836143776049, 56836143808817, 56836143841585], "A bottle-green hooded sweatshirt with varsity lettering in a warm cream tone.", [{"name":"Bottle green","hex":"#315642"},{"name":"Cream","hex":"#eee6d6"}]),
        ("hoodie", "hoodie", "Hoodie", "Nike", 199, "source-hoodie.webp", "hoodie", "Size", ["S", "L", "M", "XL"], [56836002185521, 56836002218289, 56836002251057, 56836002283825], "A heather-grey hoodie with a high-contrast black chest graphic.", [{"name":"Heather grey","hex":"#aeb1b3"},{"name":"Black","hex":"#1b1b1b"}]),
        ("luka", "air-jordan-12-retro-copy", "Luka 5", "Nikey | Password: 1", 149, "source-air-jordan-12-retro-copy.webp", "air-jordan-12-retro-copy", "Shoe size", ["40", "41", "42", "43", "44", "45", "46"], [57015176364337, 57015176397105, 57015176429873, 57015176462641, 57015176495409, 57015176528177, 57015176560945], "A black leather low-top with a clean white midsole.", [{"name":"Black","hex":"#181818"},{"name":"White","hex":"#f4f3ef"}]),
    ]
    for key, catalog_id, name, vendor, price, image, slug, legend, sizes, variant_ids, description, colors in products:
        connection.execute(
            """INSERT OR IGNORE INTO runway_products
            (product_key, catalog_id, name, vendor, price, image_url, product_url, option_legend, sizes_json, description, colors_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (key, catalog_id, name, vendor, price,
             f"https://reel-ref-try-the-look.vercel.app/assets/{image}",
             f"https://nike-makknzjs.myshopify.com/products/{slug}", legend,
             json.dumps(sizes), description, json.dumps(colors)),
        )
        connection.execute(
            "UPDATE runway_products SET description = ?, colors_json = ? WHERE product_key = ? AND (description = '' OR colors_json = '[]')",
            (description, json.dumps(colors), key),
        )
        for position, (size, variant_id) in enumerate(zip(sizes, variant_ids)):
            connection.execute(
                "INSERT OR IGNORE INTO runway_variants (variant_id, product_key, size, position) VALUES (?, ?, ?, ?)",
                (variant_id, key, size, position),
            )

    looks = [
        (1, "The City Edit", "model-1-640.webp", "original-look-1.webp", "A charcoal knit and easy denim.", ["air-jordan", "tshirt", "sweatshirt"], [(47, 27), (48, 58), (45, 96)], []),
        (2, "Gallery Opening", "model-5-640.webp", "original-look-5.webp", "A clean white tee and relaxed denim.", ["tatum", "hoodie-black", "tshirt"], [(50, 28), (48, 58), (45, 88)], ["hoodie-black"]),
        (3, "Gallery Opening", "model-4-640.webp", "original-look-4.webp", "Olive knitwear. A grounded palette.", ["sweatshirt-plus", "tatum", "tshirt"], [(50, 28), (48, 58), (45, 88)], ["tatum"]),
        (4, "Studio Day", "model-6-640.webp", "original-look-6.webp", "Black, white and laid-back denim.", ["hoodie-black", "air-jordan", "tshirt"], [(50, 28), (48, 58), (45, 88)], []),
        (5, "Studio Day", "model-3-640.webp", "original-look-3.webp", "Burgundy layers. A tailored perspective.", ["sweatshirt", "tatum", "tshirt"], [(50, 28), (48, 58), (45, 88)], []),
        (6, "Studio Day", "model-2-640.webp", "original-look-2.webp", "A grey crew and your favourite denim.", ["hoodie", "luka", "tshirt"], [(50, 28), (48, 58), (45, 88)], []),
    ]
    for position, name, model_image, original_image, description, product_keys, pins, new_products in looks:
        connection.execute(
            """INSERT OR IGNORE INTO runway_looks
            (id, position, name, model_image, original_image, description)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (position, position, name,
             f"https://reel-ref-try-the-look.vercel.app/assets/{model_image}",
             f"https://reel-ref-try-the-look.vercel.app/assets/{original_image}", description),
        )
        for item_position, (product_key, (pin_left, pin_top)) in enumerate(zip(product_keys, pins)):
            connection.execute(
                """INSERT OR IGNORE INTO runway_look_products
                (look_id, position, product_key, pin_left, pin_top, is_new)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (position, item_position, product_key, pin_left, pin_top,
                 int(product_key in new_products)),
            )


def get_runway_catalog():
    connection = get_db()
    product_rows = connection.execute("SELECT * FROM runway_products ORDER BY rowid").fetchall()
    products = {}
    for row in product_rows:
        variants = connection.execute(
            "SELECT variant_id, size, available FROM runway_variants WHERE product_key = ? ORDER BY position",
            (row["product_key"],),
        ).fetchall()
        products[row["product_key"]] = {
            "id": row["catalog_id"], "name": row["name"], "vendor": row["vendor"],
            "price": row["price"], "image": row["image_url"], "url": row["product_url"],
            "legend": row["option_legend"], "sizes": json.loads(row["sizes_json"]),
            "description": row["description"], "colors": json.loads(row["colors_json"]),
            "variants": [variant["variant_id"] for variant in variants],
        }

    looks = []
    for row in connection.execute("SELECT * FROM runway_looks ORDER BY position"):
        associations = connection.execute(
            """SELECT product_key, pin_left, pin_top, is_new FROM runway_look_products
            WHERE look_id = ? ORDER BY position""",
            (row["id"],),
        ).fetchall()
        looks.append({
            "name": row["name"], "image": row["model_image"],
            "original": row["original_image"], "description": row["description"],
            "items": [item["product_key"] for item in associations],
            "pins": [[item["pin_left"], item["pin_top"]] for item in associations],
            "new": [item["product_key"] for item in associations if item["is_new"]],
        })
    connection.close()
    return {"products": products, "looks": looks}


initialize_database()


# HOME PAGE - DISPLAY PRODUCTS
@app.route("/")
def home():
    return render_template("index.html", runway_catalog=get_runway_catalog())


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password with at least 8 characters.", "error")
            return render_template("signup.html", name=name, email=email)

        connection = get_db()
        try:
            cursor = connection.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            connection.commit()
            session.clear()
            session["user_id"] = cursor.lastrowid
            session["user_name"] = name
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("An account with this email already exists. Sign in instead.", "error")
        finally:
            connection.close()
    return render_template("signup.html", name="", email="")


@app.route("/login", methods=["GET", "POST"])
@app.route("/signin", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        connection = get_db()
        user = connection.execute(
            "SELECT id, name, password_hash FROM users WHERE email = ? COLLATE NOCASE",
            (email,),
        ).fetchone()
        connection.close()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            next_page = request.args.get("next", "")
            if next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)
            return redirect(url_for("dashboard"))
        flash("That email and password combination was not recognized.", "error")
    return render_template("login.html")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    connection = get_db()
    product_count = connection.execute("SELECT COUNT(*) FROM runway_products").fetchone()[0]
    look_count = connection.execute("SELECT COUNT(*) FROM runway_looks").fetchone()[0]
    variant_count = connection.execute("SELECT COUNT(*) FROM runway_variants").fetchone()[0]
    order_count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    products = connection.execute(
        "SELECT product_key, name, vendor, price, image_url, product_url FROM runway_products ORDER BY rowid"
    ).fetchall()
    looks = connection.execute(
        "SELECT id, position, name, model_image FROM runway_looks ORDER BY position"
    ).fetchall()
    connection.close()
    return render_template(
        "dashboard.html", name=session.get("user_name", "there"),
        product_count=product_count, look_count=look_count,
        variant_count=variant_count, order_count=order_count,
        products=products, looks=looks,
        runway_catalog=get_runway_catalog(),
    )


# ADD PRODUCT TO CART
@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    connection = get_db()

    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    connection.close()

    if product is None:
        flash("Product not found.")
        return redirect(url_for("home"))

    cart = session.get("cart", {})
    product_key = str(product_id)

    current_quantity = int(cart.get(product_key, 0))

    if current_quantity >= product["stock"]:
        flash("Not enough stock available.")
    else:
        cart[product_key] = current_quantity + 1
        session["cart"] = cart
        flash("Product added to cart!")

    return redirect(url_for("home"))


# DISPLAY SHOPPING CART
@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    connection = get_db()

    for product_id, quantity in cart.items():
        product = connection.execute(
            "SELECT * FROM products WHERE id = ?",
            (int(product_id),)
        ).fetchone()

        if product:
            subtotal = product["price"] * quantity
            total += subtotal

            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "subtotal": subtotal,
                "stock": product["stock"]
            })

    connection.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


# UPDATE CART QUANTITY
@app.route("/update-cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    quantity = request.form.get("quantity", type=int)

    cart = session.get("cart", {})
    product_key = str(product_id)

    connection = get_db()
    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()
    connection.close()

    if product is None:
        cart.pop(product_key, None)
    elif quantity is None or quantity < 1:
        cart.pop(product_key, None)
    elif quantity > product["stock"]:
        flash("Quantity is greater than available stock.")
    else:
        cart[product_key] = quantity

    session["cart"] = cart

    return redirect(url_for("view_cart"))


# REMOVE PRODUCT FROM CART
@app.route("/remove-from-cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)

    session["cart"] = cart

    return redirect(url_for("view_cart"))


# CHECKOUT AND SAVE ORDER
@app.route("/checkout", methods=["POST"])
def checkout():
    customer_name = request.form.get("customer_name", "").strip()
    cart = session.get("cart", {})

    if not customer_name:
        flash("Please enter your name.")
        return redirect(url_for("view_cart"))

    if not cart:
        flash("Your shopping cart is empty.")
        return redirect(url_for("view_cart"))

    connection = get_db()

    try:
        connection.execute("BEGIN IMMEDIATE")

        order_products = []
        total = 0

        # Check every product before creating an order
        for product_id, quantity in cart.items():
            product = connection.execute(
                "SELECT * FROM products WHERE id = ?",
                (int(product_id),)
            ).fetchone()

            if product is None:
                raise ValueError("A product no longer exists.")

            if quantity < 1 or product["stock"] < quantity:
                raise ValueError(
                    f"Not enough stock for {product['name']}."
                )

            subtotal = product["price"] * quantity
            total += subtotal

            order_products.append((product, quantity))

        # Save the order
        cursor = connection.execute(
            "INSERT INTO orders (customer_name, total) VALUES (?, ?)",
            (customer_name, total)
        )

        order_id = cursor.lastrowid

        # Save order items and update stock
        for product, quantity in order_products:
            connection.execute(
                """
                INSERT INTO order_items
                (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, product["id"], quantity, product["price"])
            )

            connection.execute(
                """
                UPDATE products
                SET stock = stock - ?
                WHERE id = ?
                """,
                (quantity, product["id"])
            )

        connection.commit()

        session["cart"] = {}

        return render_template(
            "success.html",
            order_id=order_id,
            customer_name=customer_name,
            total=total
        )

    except (ValueError, sqlite3.Error) as error:
        connection.rollback()
        flash(str(error) if isinstance(error, ValueError)
              else "Order could not be saved. Please try again.")
        return redirect(url_for("view_cart"))

    finally:
        connection.close()


# START APPLICATION
if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
