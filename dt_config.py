import json
import os

CONFIG = {    
    'realtime_db_path': './sensor_data_realtime.db',
    'history_db_path': './sensor_data_history.db'
}

# Get the directory of the current running Python file
local_repository = os.path.dirname(os.path.abspath(__file__))

CONFIG["TOPIC_FILE_PATH"]= f"{local_repository}/shared_topic.json"
CONFIG["ifc_file"] = f"{local_repository}/local_files/smartLab.ifc"
CONFIG["mqtt_excel"] = f"{local_repository}/local_files/Smartlab_MQTT_Topics.xlsx"
local_config = f"{local_repository}/local_files/smartlab_config.json"

with open(local_config, "r") as f:
    data = json.load(f)
    CONFIG.update(data)

def load_link():
    local_repository = os.path.dirname(os.path.abspath(__file__))
    topic_ifc_link = f"{local_repository}/local_files/topic_ifc_link.json"

    with open(topic_ifc_link, "r") as f:
        link = json.load(f)
    return link

sensor_ifc_link = load_link()

mqtt_topics = list(sensor_ifc_link.keys())
CONFIG['mqtt_topics'] = mqtt_topics 

# Constants for thresholds
THRESHOLDS = {
    'CO2': [429.5, 1000],  # CO2 above low value implies occupied, high value for safety threshold    
    'TEMPERATURE': [18, 24],  # Low and high value for temperature    
    'HUMIDITY': [30, 60]  # Low and high value for humidity
}

if __name__ == "__main__":
    from pprint import pprint
    pprint(CONFIG)