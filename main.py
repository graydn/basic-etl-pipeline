import os
import requests
import sqlite3
import pandas as pd
import threading
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CF_URL = "https://api.currencyfreaks.com/v2.0"
API_KEY = os.getenv("API_KEY")
DB_NAME = "forex_data.db"
CURRENCIES_CSV = "currencies.csv"

def fetch_latest_rates():
    """Fetch latest currency exchange rates."""
    url = f"{CF_URL}/rates/latest"
    params = {"apikey": API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rates: {e}")
        return None

def create_database():
    """Create SQLite database and forex table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forex (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            territory TEXT,
            currency TEXT,
            symbol TEXT,
            iso_code TEXT UNIQUE,
            date TEXT,
            rate REAL
        )
    ''')
    conn.commit()
    return conn

def load_currencies():
    """Load currencies from CSV into a DataFrame."""
    return pd.read_csv(CURRENCIES_CSV)

def update_or_insert_rates(latest_rates, currencies_df, conn):
    """Update or insert records in the forex table."""
    rates = latest_rates['rates']
    date = latest_rates['date'][:10]
    cursor = conn.cursor()
    
    for _, row in currencies_df.iterrows():
        iso_code = row['ISO code']
        if iso_code in rates:
            cursor.execute('SELECT * FROM forex WHERE iso_code = ?', (iso_code,))
            if cursor.fetchone():
                print(f"Updating record for {iso_code}...")
                cursor.execute('''
                    UPDATE forex SET rate = ?, date = ? WHERE iso_code = ?
                ''', (float(rates[iso_code]), date, iso_code))
            else:
                print(f"Inserting new record for {iso_code}...")
                cursor.execute('''
                    INSERT INTO forex (territory, currency, symbol, iso_code, date, rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (row['Territory'], row['Currency'], row['SymbolAbbrev'], iso_code, date, float(rates[iso_code])))
    
    conn.commit()

def select_all_records(conn):
    """Select and print all records from the forex table."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM forex')
    for record in cursor.fetchall():
        print(record)

def update_rates_at_midnight(conn, currencies_df):
    """Update rates daily at midnight."""
    while True:
        now = datetime.now()
        wait_time = (datetime.combine(now.date() + timedelta(days=1), datetime.min.time()) - now).total_seconds()
        print(f"Waiting for {wait_time:.0f} seconds until the next update...")
        time.sleep(wait_time + 1)

        latest_rates = fetch_latest_rates()
        if latest_rates:
            print("Updating rates...")
            update_or_insert_rates(latest_rates, currencies_df, conn)

def main():
    conn = create_database()
    currencies_df = load_currencies()

    print("Fetching latest rates for initial database population...")
    latest_rates = fetch_latest_rates()
    if latest_rates:
        update_or_insert_rates(latest_rates, currencies_df, conn)
    
    threading.Thread(target=update_rates_at_midnight, args=(conn, currencies_df), daemon=True).start()

    while True:
        command = input("Enter 'show' to view all records, 'update' to manually update rates, or 'exit' to quit: ")
        if command.lower() == 'show':
            print("All Records in Forex Table:")
            select_all_records(conn)
        elif command.lower() == 'update':
            print("Fetching latest rates for manual update...")
            latest_rates = fetch_latest_rates()
            if latest_rates:
                update_or_insert_rates(latest_rates, currencies_df, conn)
        elif command.lower() == 'exit':
            print("Exiting...")
            break
        else:
            print("Unknown command. Please enter 'show', 'update', or 'exit'.")

    conn.close()

if __name__ == "__main__":
    main()
