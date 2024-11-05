import sqlite3
import json  # In case sensor_data is a JSON string

# Function to connect to the SQLite database
def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Function to create the sensor_data table if it doesn't exist
def create_sensor_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY,
        sensor_id TEXT,
        timestamp DATETIME,
        value REAL
    )
    ''')
    conn.commit()

# Function to clear old data
def clear_old_data(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sensor_data")
    conn.commit()
    print("Old data cleared from the database.")  # Debugging: Verify data is cleared

# Function to save sensor data into the database
def save_sensor_data(sensor_data, db_path):
    print(f"Saving data: {sensor_data}")  # Debugging: Check what is being passed to this function
    
    # Connect to the database
    conn = connect_db(db_path)
    cursor = conn.cursor()
    
    try:
        # Insert sensor data into the database
        cursor.execute(
            'INSERT INTO sensor_data (sensor_id, timestamp, value) VALUES (?, ?, ?)', 
            (sensor_data['id'], sensor_data['timestamp'], sensor_data['value'])
        )
        conn.commit()  # Commit changes to the database
    except sqlite3.Error as e:
        print(f"Error saving data to the database: {e}")
    finally:
        conn.close()  # Close the connection

# Function to save data to history database
def save_to_history(sensor_data, history_db_path):
    conn = connect_db(history_db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO sensor_data (sensor_id, timestamp, value) VALUES (?, ?, ?)', 
            (sensor_data['id'], sensor_data['timestamp'], sensor_data['value'])
        )
        conn.commit()  # Commit changes to the history database
    except sqlite3.Error as e:
        print(f"Error saving data to the history database: {e}")
    finally:
        conn.close()

# Function to fetch sensor data of a topic from the database
def fetch_sensor_data(db_path, topic):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()    

    # Execute the query to find rows with the specific topic
    cursor.execute("SELECT sensor_id, timestamp, value FROM sensor_data WHERE sensor_id = ?", (topic,))

    return cursor.fetchall()


if __name__ == '__main__':  
    from dt_config import CONFIG
    from pprint import pprint
    topic = 'KNX/13/0/0<Livingroom.Sensors.CO2-ppm>'
    history_sensor_data = fetch_sensor_data(CONFIG['history_db_path'],topic)
    realtime_sensor_data = fetch_sensor_data(CONFIG['realtime_db_path'],topic)
    print('History Sensor Data')
    pprint(history_sensor_data)
    print('Realtime Sensor Data')
    pprint(realtime_sensor_data)
    



