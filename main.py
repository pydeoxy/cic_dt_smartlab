import threading
from mqtt_client import setup_mqtt
from database import connect_db, create_sensor_table, clear_old_data, save_sensor_data, save_to_history
from visualization import visualize_real_time_data

# Main function to start the MQTT client and visualization
def main(realtime_db_path, history_db_path, mqtt_broker, mqtt_port, mqtt_topic, visual_topic):
    # Connect to the database and ensure the sensor_data table exists
    conn = connect_db(realtime_db_path)
    create_sensor_table(conn)

    # Optionally, clear the old data before saving new sensor data
    clear_old_data(conn)  # Call this only if you need to clear the data
    conn.close()

    # Also connect to the history database and ensure the sensor_data table exists
    history_conn = connect_db(history_db_path)
    create_sensor_table(history_conn)
    history_conn.close()

    # Function to save data to both databases
    def save_both_databases(sensor_data):
        save_sensor_data(sensor_data, realtime_db_path)  # Save to real-time database
        save_to_history(sensor_data, history_db_path)    # Save to history database

    # Start the MQTT client in a separate thread
    mqtt_thread = threading.Thread(target=setup_mqtt, args=(mqtt_broker, mqtt_port, mqtt_topic, save_both_databases))
    mqtt_thread.start()
    print("MQTT client started")  # Debugging: Check if MQTT client thread starts

    # Start the real-time visualization in the main thread
    visualize_real_time_data(realtime_db_path, visual_topic)
    print("Visualization started")  # Debugging: Check if visualization starts

    # Wait for the MQTT thread to finish
    mqtt_thread.join()

if __name__ == "__main__":
    from dt_config import CONFIG
    topic = 'M-bus/Electricity/Active Imported Power Total'
    main(CONFIG['realtime_db_path'], CONFIG['history_db_path'], CONFIG['mqtt_broker'], CONFIG['mqtt_port'], CONFIG['mqtt_topics'], topic)
