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
    try:
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
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")

initialize_db()

# Compost log features
class CompostLog:
    @staticmethod
    def add_entry(item, weight):
        """Add a new entry to the compost log."""
        try:
            weight = float(weight)
            date = datetime.date.today().strftime("%Y-%m-%d")
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO compost_log (item, weight, date) VALUES (?, ?, ?)", (item, weight, date))
            conn.commit()
            conn.close()
            return True  # Success flag
        except Exception as e:
            print(f"Error adding entry: {e}")
            return False  # Failure flag

    @staticmethod
    def view_log():
        """View all compost log entries."""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM compost_log ORDER BY date DESC")
            logs = c.fetchall()
            conn.close()
            return logs
        except sqlite3.Error as e:
            print(f"Error fetching log entries: {e}")
            return []

    @staticmethod
    def search_log(query):
        """Search the compost log for a specific item."""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM compost_log WHERE item LIKE ?", ('%' + query + '%',))
            results = c.fetchall()
            conn.close()
            return results
        except sqlite3.Error as e:
            print(f"Error searching log: {e}")
            return []

    @staticmethod
    def binary_search_log(query):
        """Binary search for an item in the sorted log."""
        logs = sorted(CompostLog.view_log(), key=lambda x: x[1])  # Sort by item name
        low, high = 0, len(logs) - 1
        while low <= high:
            mid = (low + high) // 2
            if logs[mid][1].lower() == query.lower():
                return logs[mid]  # Found the match
            elif logs[mid][1].lower() < query.lower():
                low = mid + 1
            else:
                high = mid - 1
        return None  # Not found

# Google Maps API for compost sites
class CompostResources:
    @staticmethod
    def get_nearby_compost_sites(location="New York"):
        """Fetch nearby compost sites from Google Maps API."""
        try:
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=compost+site+near+{location}&key={GOOGLE_MAPS_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            return [(place["name"], place["formatted_address"]) for place in data.get("results", [])]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching compost sites: {e}")
            return []

# Notifications with Linked List
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class NotificationSystem:
    def __init__(self):
        self.head = None

    def add_notification(self, message):
        """Add a new notification to the linked list."""
        new_node = Node(message)
        if not self.head:
            self.head = new_node
        else:
            last = self.head
            while last.next:
                last = last.next
            last.next = new_node

    def view_notifications(self):
        """Retrieve all notifications."""
        current = self.head
        notifications = []
        while current:
            notifications.append(current.data)
            current = current.next
        return notifications

notification_system = NotificationSystem()

def background_notifier():
    """Add periodic notifications in the background."""
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
    if CompostLog.add_entry(item, weight):
        notification_system.add_notification(f"✅ New log added: {item} ({weight} kg)")
    else:
        notification_system.add_notification(f"❌ Failed to add log: {item} ({weight} kg)")
    return redirect("/")

@app.route("/search", methods=["POST"])
def search_log():
    query = request.form["query"]
    results = CompostLog.search_log(query)
    return render_template("search.html", results=results)

@app.route("/binary_search", methods=["POST"])
def binary_search():
    query = request.form["query"]
    result = CompostLog.binary_search_log(query)
    if result:
        return render_template("binary_search.html", result=result)
    else:
        return render_template("binary_search.html", result=None)

@app.route("/resources")
def compost_sites():
    location = "New York"  # Replace with user location if needed
    sites = CompostResources.get_nearby_compost_sites(location)
    return render_template("resources.html", sites=sites)

if __name__ == "__main__":
    app.run(debug=True)
