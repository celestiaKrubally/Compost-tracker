
from flask import Flask
import sqlite3  # <-- This is the missing import

app = Flask(__name__)

DB_FILE = 'compost_log.db'

# Your other functions, routes, and logic
def view_log():
    conn = sqlite3.connect(DB_FILE)
    # other logic to handle the database


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

if __name__ == "__main__":
    initialize_db()

# compost log features

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
        return f"✅ Added {item} ({weight} kg) to the compost log."

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

    @staticmethod
    def sort_logs(by="date"):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        order_by = "date DESC" if by == "date" else "weight DESC"
        c.execute(f"SELECT * FROM compost_log ORDER BY {order_by}")
        logs = c.fetchall()
        conn.close()
        return logs


# google api maps

import requests

GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

class CompostResources:
    @staticmethod
    def get_nearby_compost_sites(location="New York"):
        """Fetches compost sites using Google Maps API"""
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=compost+site+near+{location}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [(place["name"], place["formatted_address"]) for place in data.get("results", [])]


#  multi threading for background notifs

import threading

class NotificationSystem:
    def __init__(self):
        self.notifications = []

    def add_notification(self, message):
        self.notifications.append(message)

    def view_notifications(self):
        return self.notifications

notification_system = NotificationSystem()

def background_notifier():
    """Sends notifications in the background"""
    while True:
        notification_system.add_notification("⏳ Reminder: Check your compost log!")
        threading.Event().wait(60 * 60)  # Notify every hour

notifier_thread = threading.Thread(target=background_notifier, daemon=True)
notifier_thread.start()




# gui

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/")
def home():
    logs = CompostLog.view_log()
    notifications = notification_system.view_notifications()
    return render_template("index.html", logs=logs, notifications=notifications)

@app.route("/add", methods=["POST"])
def add_entry():
    item = request.form["item"]
    weight = request.form["weight"]
    message = CompostLog.add_entry(item, weight)
    notification_system.add_notification(f"New log added: {item} ({weight} kg)")
    return redirect("/")

@app.route("/search", methods=["POST"])
def search_log():
    query = request.form["query"]
    results = CompostLog.search_log(query)
    return render_template("search.html", results=results)

@app.route("/graph")
def graph():
    CompostGraph.plot_waste_trends()
    return redirect("/")

@app.route("/resources")
def compost_sites():
    location = "New York"  # Replace with user location
    sites = CompostResources.get_nearby_compost_sites(location)
    return render_template("resources.html", sites=sites)

if __name__ == "__main__":
    app.run(debug=True)


# data vis


class CompostGraph:
    @staticmethod
    def plot_waste_trends():
        logs = CompostLog.view_log()
        if not logs:
            return "No data available to plot."

        dates = [entry[3] for entry in logs]
        weights = [entry[2] for entry in logs]

        plt.figure(figsize=(8, 5))
        plt.plot(dates, weights, marker="o", linestyle="-", color="green")
        plt.xlabel("Date")
        plt.ylabel("Weight (kg)")
        plt.title("Compost Weight Trends")
        plt.xticks(rotation=45)
        plt.grid()
        plt.show()

