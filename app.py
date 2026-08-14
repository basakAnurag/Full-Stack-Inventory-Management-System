from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
os.makedirs(app.instance_path, exist_ok=True) # Instance to run DB
DB_NAME = os.path.join(app.instance_path, "A3_04_4_1_85.db")
LOW_STOCK_LIMIT = 5


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows dictionary-like access to rows
    return conn


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('customer','seller')),
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            total_price REAL,
            purchase_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Ensure DB is created before first request
with app.app_context():
    initialize_db()

# --- AUTHENTICATION ROUTES ---


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for(session["role"]))
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"].strip()
    password = request.form["password"]
    role = request.form["role"]

    hashed = hash_password(password)
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password_hash=? AND role=?",
        (username, hashed, role),
    ).fetchone()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        flash(f"Welcome back, {username}!", "success")
        return redirect(url_for(role))
    else:
        flash("Invalid username, password, or role!", "error")
        return redirect(url_for("index"))


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"].strip()
    password = request.form["password"]
    confirm = request.form["confirm"]
    role = request.form["role"]

    if not username:
        flash("Username cannot be empty!", "error")
        return redirect(url_for("index"))
    if password != confirm:
        flash("Passwords do not match!", "error")
        return redirect(url_for("index"))
    if len(password) < 5:
        flash("Password must be at least 5 characters!", "error")
        return redirect(url_for("index"))

    hashed = hash_password(password)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed, role),
        )
        conn.commit()
        session["user_id"] = cursor.lastrowid
        session["username"] = username
        session["role"] = role
        conn.close()
        flash("Account created successfully!", "success")
        return redirect(url_for(role))
    except sqlite3.IntegrityError:
        flash("Username already taken!", "error")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# --- CUSTOMER ROUTES ---


@app.route("/customer")
def customer():
    if session.get("role") != "customer":
        return redirect(url_for("index"))

    conn = get_connection()
    products = conn.execute("SELECT * FROM products WHERE stock > 0").fetchall()
    history = conn.execute(
        "SELECT * FROM purchase_history WHERE user_id=? ORDER BY purchase_date DESC",
        (session["user_id"],),
    ).fetchall()
    conn.close()

    return render_template(
        "customer.html", products=products, history=history, low_stock=LOW_STOCK_LIMIT
    )


@app.route("/buy/<int:product_id>", methods=["POST"])
def buy(product_id):
    if session.get("role") != "customer":
        return redirect(url_for("index"))

    qty = int(request.form.get("quantity", 0))
    if qty <= 0:
        flash("Quantity must be greater than 0!", "error")
        return redirect(url_for("customer"))

    conn = get_connection()
    cursor = conn.cursor()
    product = cursor.execute(
        "SELECT * FROM products WHERE id=?", (product_id,)
    ).fetchone()

    if not product or product["stock"] < qty:
        flash("Not enough stock or product not found!", "error")
        conn.close()
        return redirect(url_for("customer"))

    total = product["price"] * qty
    new_stock = product["stock"] - qty
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
    cursor.execute(
        """
        INSERT INTO purchase_history (user_id, username, product_id, product_name, quantity, total_price, purchase_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            session["user_id"],
            session["username"],
            product_id,
            product["name"],
            qty,
            total,
            date_str,
        ),
    )

    conn.commit()
    conn.close()
    flash(f"Successfully purchased {qty}x {product['name']}!", "success")
    return redirect(url_for("customer"))


# --- SELLER ROUTES ---


@app.route("/seller")
def seller():
    if session.get("role") != "seller":
        return redirect(url_for("index"))

    conn = get_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    return render_template("seller.html", products=products, low_stock=LOW_STOCK_LIMIT)


@app.route("/add_product", methods=["POST"])
def add_product():
    if session.get("role") != "seller":
        return redirect(url_for("index"))

    name = request.form["name"].strip()
    price = float(request.form["price"])
    stock = int(request.form["stock"])

    if not name or price < 0 or stock < 0:
        flash("Invalid product details!", "error")
        return redirect(url_for("seller"))

    conn = get_connection()
    conn.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        (name, price, stock),
    )
    conn.commit()
    conn.close()
    flash("Product added successfully!", "success")
    return redirect(url_for("seller"))


@app.route("/update_product/<int:product_id>", methods=["POST"])
def update_product(product_id):
    if session.get("role") != "seller":
        return redirect(url_for("index"))

    price = float(request.form["price"])
    stock = int(request.form["stock"])

    if price < 0 or stock < 0:
        flash("Price and stock cannot be negative!", "error")
        return redirect(url_for("seller"))

    conn = get_connection()
    conn.execute(
        "UPDATE products SET price=?, stock=? WHERE id=?", (price, stock, product_id)
    )
    conn.commit()
    conn.close()
    flash("Product updated!", "success")
    return redirect(url_for("seller"))


@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if session.get("role") != "seller":
        return redirect(url_for("index"))

    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    flash("Product deleted!", "success")
    return redirect(url_for("seller"))


if __name__ == "__main__":
    app.run(debug=True)
