import threading
from mqtt_client import setup_mqtt
from database import connect_db, create_sensor_table, clear_old_data
from visualization import visualize_real_time_data

# Main function to start the MQTT client and visualization
def main(db_path, mqtt_broker, mqtt_port, mqtt_topic, visual_topic):
    # Connect to the database and ensure the sensor_data table exists
    conn = connect_db(db_path)
    create_sensor_table(conn)

    # Optionally, clear the old data before saving new sensor data
    clear_old_data(conn)  # Call this only if you need to clear the data

    conn.close()

    # Start the MQTT client in a separate thread
    mqtt_thread = threading.Thread(target=setup_mqtt, args=(mqtt_broker, mqtt_port, mqtt_topic))
    mqtt_thread.start()
    print("MQTT client started")  # Debugging: Check if MQTT client thread starts

    # Start the real-time visualization in the main thread
    visualize_real_time_data(db_path, visual_topic)
    print("Visualization started")  # Debugging: Check if visualization starts

    # Wait for the MQTT thread to finish
    mqtt_thread.join()

if __name__ == "__main__":
    from dt_config import CONFIG
    topic = 'KNX/15/0/0<Bathroom.Sensors.CO2-ppm>'
    main(CONFIG['db_path'], CONFIG['mqtt_broker'], CONFIG['mqtt_port'], CONFIG['mqtt_topic'], topic)
