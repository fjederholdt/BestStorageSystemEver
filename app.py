from dbm import sqlite3

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    products = get_products()
    return render_template("index.html", products=products)

def get_products():

    conn = sqlite3.connect("LetMilk.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    conn.close()

    return products

@app.route("/add_product_to_cart", methods=["POST"])
def add_product_to_cart():

    data = request.json
    product = data["product"]

    print("Product purchased:", product)

    return jsonify({
        "status": "success",
        "message": f"You bought {product}"
    })


if __name__ == "__main__":
    app.run()