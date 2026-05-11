import sqlite3
import os
import hashlib

DB_PATH = "energy_system.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table for live telemetry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_status (
            name TEXT PRIMARY KEY, watts REAL, status TEXT, essential INTEGER
        )
    ''')
    # Table for user commands
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_commands (
            name TEXT PRIMARY KEY, force_off INTEGER
        )
    ''')
    # Persistent system values (Billing/Usage)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_state (
            key TEXT PRIMARY KEY, value REAL
        )
    ''')
    
    # --- NEW: User Login Table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT NOT NULL
        )
    ''')
    # Create default admin user if none exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        pw_hash = hashlib.sha256("password123".encode()).hexdigest()
        cursor.execute('INSERT INTO users VALUES (?, ?)', ("admin", pw_hash))

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_history (
        date TEXT PRIMARY KEY, 
        kwh REAL, 
        cost REAL
    )
    ''')

    conn.commit()
    conn.close()

def save_system_value(key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO system_state (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_system_value(key, default=0.0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM system_state WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def update_device_live(name, watts, status, essential):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO device_status VALUES (?, ?, ?, ?)', (name, watts, status, int(essential)))
    conn.commit()
    conn.close()

def get_all_devices():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM device_status')
    rows = cursor.fetchall()
    conn.close()
    return {row['name']: {"watts": row['watts'], "status": row['status'], "essential": bool(row['essential'])} for row in rows}

def set_force_off(name, is_off):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO user_commands (name, force_off) VALUES (?, ?)', (name, int(is_off)))
    conn.commit()
    conn.close()

def get_forced_off_list():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM user_commands WHERE force_off = 1')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# --- NEW: User Verification Function ---
def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, pw_hash))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def update_user_credentials(new_username, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Hash the new password
    pw_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    # We clear the old user and insert the new one
    cursor.execute('DELETE FROM users') 
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (new_username, pw_hash))
    
    conn.commit()
    conn.close()
    print(f"✅ Credentials updated! New User: {new_username}")

def save_daily_log(date_str, kwh, cost):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO daily_history VALUES (?, ?, ?)', (date_str, kwh, cost))
    conn.commit()
    conn.close()

def get_all_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM daily_history ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]