import sqlite3

conn = sqlite3.connect("farmers.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS farmers (
    phone TEXT PRIMARY KEY,
    name TEXT,
    state TEXT,
    crop TEXT,
    stage TEXT
)
""")

conn.commit()


def get_farmer(phone):
    cursor.execute("SELECT * FROM farmers WHERE phone=?", (phone,))
    return cursor.fetchone()


def create_farmer(phone):
    cursor.execute("INSERT INTO farmers (phone, stage) VALUES (?, ?)", (phone, "ASK_NAME"))
    conn.commit()


def update_name(phone, name):
    cursor.execute("UPDATE farmers SET name=?, stage=? WHERE phone=?", (name, "ASK_STATE", phone))
    conn.commit()


def update_state(phone, state):
    cursor.execute("UPDATE farmers SET state=?, stage=? WHERE phone=?", (state, "ASK_CROP", phone))
    conn.commit()


def update_crop(phone, crop):
    cursor.execute("UPDATE farmers SET crop=?, stage=? WHERE phone=?", (crop, "READY", phone))
    conn.commit()