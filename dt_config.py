CONFIG = {
    #'ifc_file': 'path/to/building.ifc',
    'mqtt_broker': 'xrdevmqtt.edu.metropolia.fi',
    'mqtt_port': 1883,
    'mqtt_topics': [# 'M-bus/Electricity/Current L2'
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
    'db_path': 'C:/Users/yanpe/OneDrive - Metropolia Ammattikorkeakoulu Oy/Courses/DTIC/cic_dt_smartlab/sensor_data.db'
}
