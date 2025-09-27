from flask import Flask, render_template, request, redirect
import json, os, hashlib
from dotenv import load_dotenv

# Load .env
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")
TOKEN = hashlib.sha256(SECRET_KEY.encode()).hexdigest()

app = Flask(__name__)
PAGES_FILE = "pages.json"

# Load pages
if os.path.exists(PAGES_FILE):
    with open(PAGES_FILE, "r", encoding="utf-8") as f:
        pages = json.load(f)
else:
    pages = []

# Search function
def search_pages(query):
    results = []
    for page in pages:
        if query.lower() in page["content"].lower() or query.lower() in page["title"].lower():
            results.append({"title": page["title"], "url": page["url"]})
    return results

# Index / search
@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            results = search_pages(query)
    return render_template("index.html", results=results, token=TOKEN)

# Add page with token check and debug
@app.route("/add", methods=["POST"])
def add_page():
    submitted_token = request.form.get("token")
    print("DEBUG: Submitted token:", submitted_token)
    print("DEBUG: Expected token :", TOKEN)

    if submitted_token != TOKEN:
        print("DEBUG: Forbidden access attempt!")
        return "Forbidden", 403

    title = request.form.get("title")
    url = request.form.get("url")
    content = request.form.get("content")

    print(f"DEBUG: Adding page -> Title: {title}, URL: {url}, Content: {content}")

    if title and url and content:
        new_page = {"title": title, "url": url, "content": content}
        pages.append(new_page)
        with open(PAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(pages, f, indent=4)
        print("DEBUG: Page added successfully!")

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

# This code is Copyrighted. Copyright (c) 2025 Ding