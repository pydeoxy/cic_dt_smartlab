import threading
import os
import time
import json
from mqtt_client import setup_mqtt
from database import connect_db, create_sensor_table, clear_old_data, save_sensor_data, save_to_history, fetch_sensor_data
from visualization import visualize_real_time_data
from dt_config import CONFIG  

# Path for the shared file (you might set a specific directory here)
TOPIC_FILE_PATH = ".\shared_topic.json" # Update to a specific path accessible by both programs
last_mod_time = None # Track the last modification time of the file
visual_topic = None
visualization_running = True
stop_monitoring = False
visual_topic_lock = threading.Lock()  # Lock for thread safety
visual_topic_updated_event = threading.Event()  # Event to signal topic updates

def read_visual_topic():
    """Reads the selected topic from the shared file, if it has changed."""
    global last_mod_time, visual_topic

    try:
        # Get the current modification time of the file
        current_mod_time = os.path.getmtime(TOPIC_FILE_PATH)

        with visual_topic_lock:
            # Check if the file has been modified since the last read
            if last_mod_time is None or current_mod_time != last_mod_time:
                last_mod_time = current_mod_time  # Update the last modification time

                # Open and read the file content
                with open(TOPIC_FILE_PATH, "r") as f:
                    data = json.load(f)
                    visual_topic = data.get("visual_topic")  # Update global visual_topic
                    print(f"Topic updated to: {visual_topic}")  # Logging
            # Return the updated visual_topic
            return visual_topic

    except FileNotFoundError:
        print("Error: Topic file not found.")
        return None  # Return None if the file doesn't exist
    except json.JSONDecodeError:
        print("Error: JSON decoding issue in the topic file.")
        return None  # Return None if JSON format is invalid

# Function to monitor the visual_topic update
def monitor_visual_topic_update():
    global visual_topic
    while not stop_monitoring:
        new_visual_topic = read_visual_topic()  # Function that gets the latest visual_topic value
        with visual_topic_lock:
            if new_visual_topic != visual_topic:
                visual_topic = new_visual_topic
                print(f"visual_topic updated: {visual_topic}")
                visual_topic_updated_event.set()  # Signal topic change
        time.sleep(1)

# Main function to start the MQTT client and visualization
def main(realtime_db_path, history_db_path, mqtt_broker, mqtt_port, mqtt_topic):
    global visualization_running, stop_monitoring

    # Connect to the database and ensure the sensor_data table exists
    conn = connect_db(realtime_db_path)
    create_sensor_table(conn)
    # Clear the old data before saving new sensor data
    clear_old_data(conn)  
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
    visualize_real_time_data(realtime_db_path, read_visual_topic())        
       
    # Wait for the MQTT thread to finish
    mqtt_thread.join()    

if __name__ == "__main__":    
    main(CONFIG['realtime_db_path'], CONFIG['history_db_path'], 
        CONFIG['mqtt_broker'], CONFIG['mqtt_port'], 
        CONFIG['mqtt_topics'])
    #monitor_visual_topic_update()