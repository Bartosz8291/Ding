from flask import Flask, render_template, request, redirect, session, url_for
import json, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")  # keep secret in .env

PAGES_FILE = "pages.json"
ACCOUNTS_FILE = "accounts.json"

# Load pages
pages = []
if os.path.exists(PAGES_FILE):
    with open(PAGES_FILE, "r", encoding="utf-8") as f:
        pages = json.load(f)

# Load accounts
accounts = []
if os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        accounts = json.load(f)

def search_pages(query):
    results = []
    for page in pages:
        if query.lower() in page["content"].lower() or query.lower() in page["title"].lower():
            results.append({"title": page["title"], "url": page["url"]})
    return results

# -------------------
# Authentication
# -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        for user in accounts:
            if user["username"] == username and check_password_hash(user["password"], password):
                session["username"] = username
                return redirect(url_for("index"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Check for empty fields
        if not username or not password or not confirm:
            return render_template("register.html", error="All fields are required")

        # Check passwords match
        if password != confirm:
            return render_template("register.html", error="Passwords do not match")

        # Check if username exists
        for user in accounts:
            if user["username"] == username:
                return render_template("register.html", error="Username already taken")

        # Add new user
        hashed_pw = generate_password_hash(password)
        accounts.append({"username": username, "password": hashed_pw})
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=4)

        return redirect(url_for("login"))

    return render_template("register.html")

# -------------------
# Main Ding page
# -------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    results = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            results = search_pages(query)
    return render_template("index.html", results=results, username=session["username"])

# -------------------
# Add Page
# -------------------
@app.route("/add", methods=["POST"])
def add_page():
    if "username" not in session:
        return "Forbidden", 403

    title = request.form.get("title")
    url = request.form.get("url")
    content = request.form.get("content")

    if title and url and content:
        pages.append({"title": title, "url": url, "content": content})
        with open(PAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(pages, f, indent=4)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
