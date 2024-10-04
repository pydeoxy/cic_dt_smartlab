import paho.mqtt.client as mqtt
import json
from datetime import datetime  # For getting the current timestamp
from database import save_sensor_data
from dt_config import CONFIG

# The callback for when the client connects to the broker
'''def on_connect(client, userdata, flags, rc, mqtt_topic=CONFIG['mqtt_topic']):
    print(f"Connected with result code {rc}")
    # Subscribe to the topic (replace with your topic)
    client.subscribe(mqtt_topic)'''

# The callback for when a message is received from the broker
def on_message(client, userdata, msg, db_path=CONFIG['db_path']):
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
        save_sensor_data(sensor_data, db_path)

    except ValueError as e:
        print(f"Error converting payload to float: {e}")
    except Exception as e:
        print(f"Error saving data: {e}")

# MQTT Setup
def setup_mqtt(mqtt_broker, mqtt_port, mqtt_topic):
    client = mqtt.Client()
    #client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker (replace with your broker address and port)
    client.connect(mqtt_broker, mqtt_port, 60)
    client.subscribe(mqtt_topic)
    
    # Start the MQTT loop in a non-blocking way
    client.loop_start()
    return client

if __name__ == '__main__': 
    import time    
    client = setup_mqtt(CONFIG['mqtt_broker'], CONFIG['mqtt_port'])
    while True:
        time.sleep(1)
