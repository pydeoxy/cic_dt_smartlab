import sqlite3
import csv

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

# Function to fetch data from all topics and save as a CSV file
def save_data_csv(db_path, csv_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get all unique sensor IDs (topics)
    cursor.execute("SELECT DISTINCT sensor_id FROM sensor_data")
    topics = cursor.fetchall()

    # Prepare to write to CSV
    with open(csv_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the header
        csv_writer.writerow(["sensor_id", "timestamp", "value"])

        # Fetch data for each topic and write to CSV
        for topic in topics:
            topic_id = topic[0]  # Extract the sensor ID
            data = fetch_sensor_data(db_path, topic_id)
            csv_writer.writerows(data)  # Append the data for the topic

    conn.close()
    print(f"Data from all topics has been saved to {csv_path}")

if __name__ == '__main__':  
    from dt_config import CONFIG    
    csv_history_path = './sensor_data_history.csv'
    history_data_path =  CONFIG['history_db_path']
    save_data_csv(history_data_path, csv_history_path)
    #csv_realtime_path = './sensor_data_realtime.csv'
    #realtime_data_path =  CONFIG['realtime_db_path']
    #save_data_csv(realtime_data_path, csv_realtime_path)
    



