import sqlite3

def get_connection():
    return sqlite3.connect('data.db')

def insert_travel_plan(place, duration, purpose):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO travel_plans (place, duration, purpose) VALUES (?, ?, ?)", (place, duration, purpose))
    conn.commit()
    conn.close()
