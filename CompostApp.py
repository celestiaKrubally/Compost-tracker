import sqlite3
import datetime
import threading
import requests
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

DB_FILE = 'compost_log.db'
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your actual key

# Initialize database
def initialize_db():
    """Creates the SQLite database and compost_log table if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS compost_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            weight REAL,
            date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

initialize_db()

# Compost log features
class CompostLog:
    @staticmethod
    def add_entry(item, weight):
        weight = float(weight)
        date = datetime.date.today().strftime("%Y-%m-%d")
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO compost_log (item, weight, date) VALUES (?, ?, ?)", (item, weight, date))
        conn.commit()
        conn.close()

    @staticmethod
    def view_log():
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM compost_log ORDER BY date DESC")
        logs = c.fetchall()
        conn.close()
        return logs

    @staticmethod
    def search_log(item):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM compost_log WHERE item LIKE ?", ('%' + item + '%',))
        results = c.fetchall()
        conn.close()
        return results

# Google Maps API for compost sites
class CompostResources:
    @staticmethod
    def get_nearby_compost_sites(location="New York"):
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=compost+site+near+{location}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [(place["name"], place["formatted_address"]) for place in data.get("results", [])]

# Notifications
class NotificationSystem:
    def __init__(self):
        self.notifications = []

    def add_notification(self, message):
        self.notifications.append(message)

    def view_notifications(self):
        return self.notifications

notification_system = NotificationSystem()

def background_notifier():
    while True:
        notification_system.add_notification("⏳ Reminder: Check your compost log!")
        threading.Event().wait(60 * 60)  # Notify every hour

notifier_thread = threading.Thread(target=background_notifier, daemon=True)
notifier_thread.start()

# Routes
@app.route("/")
def home():
    logs = CompostLog.view_log()
    notifications = notification_system.view_notifications()
    return render_template("index.html", logs=logs, notifications=notifications)

@app.route("/add", methods=["POST"])
def add_entry():
    item = request.form["item"]
    weight = request.form["weight"]
    CompostLog.add_entry(item, weight)
    notification_system.add_notification(f"New log added: {item} ({weight} kg)")
    return redirect("/")

@app.route("/search", methods=["POST"])
def search_log():
    query = request.form["query"]
    results = CompostLog.search_log(query)
    return render_template("search.html", results=results)

@app.route("/resources")
def compost_sites():
    location = "New York"  # Replace with user location if needed
    sites = CompostResources.get_nearby_compost_sites(location)
    return render_template("resources.html", sites=sites)

if __name__ == "__main__":
    app.run(debug=True)


