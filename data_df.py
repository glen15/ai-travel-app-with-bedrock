import sqlite3
import pandas as pd

def get_travel_plans():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT place, duration, purpose FROM travel_plans")
    plans = c.fetchall()
    conn.close()
    return plans

def create_dataframe():
    plans = get_travel_plans()
    df = pd.DataFrame(plans, columns=['Place', 'Duration', 'Purpose'])
    return df
