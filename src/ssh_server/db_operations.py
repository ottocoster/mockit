import sqlite3
import os

# Static database path
DB_PATH = 'example.db'

def get_connection():
    """Establishes a connection to the SQLite database and creates the file if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        open(DB_PATH, 'w').close()  # Create the file if it doesn't exist
    return sqlite3.connect(DB_PATH)

def create_table(device_type):
    """Creates a new table named after the device_type."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {device_type} (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_record(device_type, key, value):
    """Inserts a new record with string value into the specified device_type table using a unique key."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {device_type} (key, value) VALUES (?, ?)
    ''', (key, value))
    conn.commit()
    conn.close()

def read_record(device_type, key):
    """Retrieves a record by key from the specified device_type table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT value FROM {device_type} WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def update_record(device_type, key, new_value):
    """Updates the string value of a record identified by key in the specified device_type table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE {device_type} SET value = ? WHERE key = ?
    ''', (new_value, key))
    conn.commit()
    conn.close()

def delete_record(device_type, key):
    """Deletes a record from the specified device_type table by key."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        DELETE FROM {device_type} WHERE key = ?
    ''', (key,))
    conn.commit()
    conn.close()

# Example usage:
# create_table('example_device')
# create_record('example_device', 'device_key_1', 'some value')
# value = read_record('example_device', 'device_key_1')
# update_record('example_device', 'device_key_1', 'new value')
# delete_record('example_device', 'device_key_1')

# if command == "create":
#     create_record("a10", "version", "v7")
#     return f"created version value"
# if command == "read":
#     value = read_record("a10", "version")
#     logger.debug(f"read from db: {value}")
#     if value:
#         return value
#     else:
#         return "No record founded!"
# if command == "update":
#     data = update_record("a10", "version", "v8")
#     return "Record updated"
# if command == "delete":
#     data = delete_record("a10", "version")
#     return "Record deleted"