import json

CONFIG = {       
    'mqtt_topics': ['M-bus/Electricity/Active Imported Energy Total',
                    'M-bus/Electricity/Active Imported Power Total',
                    'M-bus/Heat energy/Volume',
                    'M-bus/Cold water/Flow Total',
                    'M-bus/Hot water/Flow Total',
                    'KNX/13/0/2<Livingroom.Sensors.Air-temperature-C>',
                    'KNX/13/0/3<Livingroom.Sensors.Floor-temp-C>',
                    'KNX/13/0/0<Livingroom.Sensors.CO2-ppm>',
                    'KNX/13/0/1<Livingroom.Sensors.Rh-percent>',
                    'KNX/14/0/2<Bedroom.Sensors.Air-temperature-C>',
                    'KNX/14/0/0<Bedroom.Sensors.CO2-ppm>',
                    'KNX/14/0/1<Bedroom.Sensors.Rh-percent>',
                    'KNX/15/0/2<Bathroom.Sensors.Air-temperature-C>',
                    'KNX/15/0/3<Bathroom.Sensors.Floor-temp-C>', 
                    'KNX/15/0/0<Bathroom.Sensors.CO2-ppm>',
                    'KNX/15/0/1<Bathroom.Sensors.RH|percent>'
                    ],
    'realtime_db_path': './sensor_data_realtime.db',
    'history_db_path': './sensor_data_history.db'
}

# Replace the file location with your own path
local_config = "C:/Users/yanpe/Documents/projects/cic_dt_smartlab_files/smartlab_config.json"
# Open and read the file content
with open(local_config, "r") as f:
    data = json.load(f)
    CONFIG.update(data)

if __name__ == "__main__":
    from pprint import pprint
    pprint(CONFIG)