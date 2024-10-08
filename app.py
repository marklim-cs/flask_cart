import sqlite3
import os
from dotenv import load_dotenv
from flask import Flask, g, render_template, session, request, redirect
from flask_session import Session

app = Flask(__name__)

load_dotenv()
DATABASE = os.getenv('DATABASE_URL')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    db = get_db()
    books = db.execute("SELECT * FROM books")
    return render_template("books.html", books=books)

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/cart", methods=["POST", "GET"])
def cart():
    db = get_db()
    if "cart" not in session:
        session["cart"] = []

    #POST
    if request.method == "POST":
        book_id = request.form.get("id")
        if book_id:
            session["cart"].append(book_id)
            return redirect("/cart")

    #GET
    cart_ids = session.get("cart", [])
    if cart_ids:
        placeholders = ','.join(['?'] * len(cart_ids))
        books = db.execute(f"SELECT * FROM books WHERE id IN ({placeholders})", cart_ids)
    else:
        books = []

    return render_template("cart.html", books=books)

@app.route("/delete", methods=["POST"])
def delete():
    book_id = request.form.get("id")
    if book_id and "cart" in session:
        try:
            session["cart"].remove(book_id)
        except ValueError:
            pass
    return redirect("/cart") 