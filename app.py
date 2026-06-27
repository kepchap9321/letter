
from flask import Flask, request
import datetime
import uuid
import sqlite3
import os

app = Flask(__name__)

# ---------------- DB PATH (FIXED) ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


# ---------------- INIT DB ----------------
def initdb():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            message TEXT,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()


# ---------------- INSERT ----------------
def insert_message(message_id, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO messages (id, message, timestamp) VALUES (?, ?, ?)",
        (message_id, message, timestamp)
    )

    conn.commit()
    conn.close()


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        message_id = str(uuid.uuid4())
        message = request.form["message"]

        insert_message(message_id, message)

        return f"Link: http://127.0.0.1:5000/message/{message_id}"

    return '''
    <form method="post">
        <textarea name="message"></textarea><br>
        <button type="submit">Submit</button>
    </form>
    '''


# ---------------- GET MESSAGE ----------------
@app.route("/message/<message_id>")
def get_message(message_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT message, timestamp FROM messages WHERE id = ?",
        (message_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Message not found", 404

    message, timestamp = row

    created_time = datetime.datetime.strptime(
        timestamp, "%Y-%m-%d %H:%M:%S"
    )

    now = datetime.datetime.now()

    # ---------------- EXPIRY LOGIC ----------------
    if now - created_time > datetime.timedelta(minutes=30):
        return "Message expired", 410

    return f"""
    Message: {message}<br>
    Created: {timestamp}
    """


# ---------------- START ----------------
if __name__ == "__main__":
    initdb()
    app.run(debug=True)
