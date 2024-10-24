CONFIG = {
    #'ifc_file': 'path/to/building.ifc',
    'mqtt_broker': 'xrdevmqtt.edu.metropolia.fi',
    'mqtt_port': 1883,
    'mqtt_topics': [# 'M-bus/Electricity/Current L2'
                    'KNX/15/0/3<Bathroom.Sensors.Floor-temp-C>', 
                    'KNX/15/0/0<Bathroom.Sensors.CO2-ppm>' 
                    ],
    'db_path': 'C:/Users/yanpe/OneDrive - Metropolia Ammattikorkeakoulu Oy/Courses/DTIC/cic_dt_smartlab/sensor_data.db'
}
