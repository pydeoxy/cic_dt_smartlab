import paho.mqtt.client as mqtt
import json
from datetime import datetime  # For getting the current timestamp

# The callback for when a message is received from the broker
def on_message(client, userdata, msg, save_callback):
    try:
        # Decode the message payload from bytes to string (in this case, it's a number)
        payload_value = float(msg.payload.decode('utf-8'))
        
        # Construct the sensor_data dictionary
        sensor_data = {
            "id": msg.topic,  # Use the topic name as the sensor ID
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),  # Current time in ISO format
            "value": payload_value  # The value received from the payload
        }
        print(f"Received sensor data: {sensor_data}")

        # Save the sensor data to the database
        save_callback(sensor_data)

    except ValueError as e:
        print(f"Error converting payload to float: {e}")
    except Exception as e:
        print(f"Error saving data: {e}")

# MQTT Setup
def setup_mqtt(mqtt_broker, mqtt_port, mqtt_topics, save_callback):
    client = mqtt.Client()
    # Attach on_message callback with access to the save_callback
    client.on_message = lambda client, userdata, msg: on_message(client, userdata, msg, save_callback)

    # Connect to the MQTT broker (replace with your broker address and port)
    client.connect(mqtt_broker, mqtt_port, 60)
    for topic in mqtt_topics:
        client.subscribe(topic)
    
    # Start the MQTT loop in a non-blocking way
    client.loop_start()
    return client

if __name__ == '__main__': 
    from dt_config import CONFIG
    import time   
    import threading
    from database import save_sensor_data, save_to_history

    # Function to save data to both databases
    def save_both_databases(sensor_data):
        save_sensor_data(sensor_data, CONFIG['realtime_db_path'])  # Save to real-time database
        save_to_history(sensor_data, CONFIG['history_db_path'])  
    # Start the MQTT client in a separate thread
    mqtt_thread = threading.Thread(target=setup_mqtt, args=(CONFIG['mqtt_broker'], CONFIG['mqtt_port'], CONFIG['mqtt_topics'], save_both_databases))
    mqtt_thread.start()
    print("MQTT client started") 
    
    while True:
        time.sleep(1)
