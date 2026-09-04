
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Demo database configuration
DATABASE = "freshmart.db"

# Demo secret — intentionally included for CodeSentinel to detect
JWT_SECRET = "freshmart-demo-secret-123"


def get_db():
    return sqlite3.connect(DATABASE)


@app.route("/")
def home():
    return jsonify({
        "application": "FreshMart",
        "message": "Fresh Food Store API"
    })


@app.route("/products")
def get_products():
    search = request.args.get("search", "")

    db = get_db()

    # Intentionally vulnerable SQL construction
    query = f"""
        SELECT id, name, price, stock
        FROM products
        WHERE name LIKE '%{search}%'
    """

    products = db.execute(query).fetchall()

    return jsonify([
        {
            "id": p[0],
            "name": p[1],
            "price": p[2],
            "stock": p[3]
        }
        for p in products
    ])


@app.route("/products/<int:product_id>")
def get_product(product_id):
    db = get_db()

    product = db.execute(
        "SELECT id, name, price, stock FROM products "
        "WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({
        "id": product[0],
        "name": product[1],
        "price": product[2],
        "stock": product[3]
    })


@app.route("/orders")
def get_orders():
    db = get_db()

    orders = db.execute(
        "SELECT id, customer_id, total FROM orders"
    ).fetchall()

    result = []

    # Intentional N+1 query problem
    for order in orders:
        customer = db.execute(
            "SELECT name FROM customers WHERE id = ?",
            (order[1],)
        ).fetchone()

        result.append({
            "order_id": order[0],
            "customer": customer[0] if customer else "Unknown",
            "total": order[2]
        })

    return jsonify(result)


@app.route("/upload", methods=["POST"])
def upload_image():
    image = request.files["image"]

    # Intentionally unsafe filename handling
    filename = image.filename

    image.save(
        os.path.join("/tmp/uploads", filename)
    )

    return jsonify({
        "message": "Image uploaded",
        "filename": filename
    })


@app.route("/discount")
def calculate_discount():
    price = float(request.args.get("price", 0))
    discount = float(request.args.get("discount", 0))

    # Missing validation
    final_price = price - (price * discount)

    return jsonify({
        "original_price": price,
        "discount": discount,
        "final_price": final_price
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
