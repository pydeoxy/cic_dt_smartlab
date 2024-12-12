import pandas as pd
import time
from dt_config import CONFIG 
import paho.mqtt.client as mqtt

current_payload = ''

def link_data_from_xlsx(xlsx_file):    
    xlsx = pd.ExcelFile(xlsx_file)
    # read the first sheet, skip first row and use second row as header
    df = xlsx.parse(xlsx.sheet_names[0],skiprows=[0], header=0)
    #drop empty rows (no value in column 'IFC Entity')
    df.dropna(subset=['IFC Target GUID'], inplace=True)
    #drop unamed columns
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
    topic_guid = df[['FullTopic', 'IFC Target GUID']]
    link_dict = topic_guid.to_dict('records')
    return link_dict

def link_data_from_csv(csv_file):    
    try:
        # Attempt to read the CSV file, skipping bad lines
        df = pd.read_csv(csv_file, sep=';',header=0, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        # Fall back to a different encoding if utf-8 fails
        df = pd.read_csv(csv_file, sep=';',header=0, encoding='ISO-8859-1', on_bad_lines='skip')    
    # Drop empty rows (no value in column 'IFC Target GUID')
    df.dropna(subset=['IFC Device GUID'], inplace=True)     
    # Drop unnamed columns
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]    
    # Select relevant columns and convert to a dictionary
    topic_guid = df[['FullTopic', 'IFC Device GUID']]
    link_dict = topic_guid.set_index('FullTopic')['IFC Device GUID'].to_dict()    
    return link_dict

def actuator_control(topic, payload):
    # Create an MQTT client instance
    client = mqtt.Client()
    # Connect to the broker
    client.connect(CONFIG['mqtt_broker'], CONFIG['mqtt_port'], 60)  
    # Publish the value to the topic
    client.publish(topic, payload)
    # Disconnect the client
    client.disconnect()
    print(f"Value '{payload}' published to topic '{topic}'.")

def actuator_payload(topic):   
    # Callback for when a message is received
    def on_message(client, userdata, msg):
        #global message_received
        global current_payload
        current_payload = msg.payload.decode()
        print(f"Received message: {current_payload} on topic: {msg.topic}")        
        # Stop the MQTT client loop after receiving one message
        client.disconnect()        

    # Initialize the MQTT client
    client = mqtt.Client()
    # Set up the callback for message handling
    client.on_message = on_message
    # Connect to the MQTT broker
    client.connect(CONFIG['mqtt_broker'], CONFIG['mqtt_port'], 60)
    # Subscribe to the specific topic
    client.subscribe(topic)
    # Start the loop in a separate thread
    print(f"Waiting for a message on topic: {topic}")
    client.loop_start()
    # Wait 1s to receive a message  
    time.sleep(1)
    client.loop_stop()
    print("MQTT loop stopped. Exiting.")        
    return current_payload

actuator_ifc_link = link_data_from_csv(CONFIG["mqtt_csv"])

if __name__ == '__main__':    
    from pprint import pprint      
    #pprint(actuator_ifc_link)
    topic = 'KNX/0/4/41<Actuators.DimLight.Bedroom-Light-M1-Dim>' #'KNX/0/5/0<Actuators.Curtain.Bedroom-Up|Down>'
    print(actuator_payload(topic))
    