# **CiC Digital Twins Project of SmartLab**

# **Project Overview**

This project is a proof-of-concept for the Digital Twin of SmartLab, built as part of the CiC Digital Twins initiative. The main objectives of the project are to integrate real-time sensor data from an MQTT broker, manage data storage, and visualize the SmartLab building and sensor data in Blender. The project establishes a practical workflow for developing a Minimum Viable Product (MVP) using Git, Google Drive, and VS Code as development tools.

## **Project Objectives**

* **Real-time Integration**: Capture real-time sensor data using MQTT.  
* **Data Management**: Store sensor data in a database and support CRUD operations.  
* **3D Visualization**: Visualize the SmartLab building and sensor data using Blender.  
* **Modularity and Scalability**: Maintain a well-structured Python codebase that is scalable and easy to maintain.

  ## **Tools and Resources**

* **IFC Model**: The IFC model of the SmartLab building.  
* **MQTT Sensors**: Real-time sensor data streaming via MQTT.  
* **Development Tools**: Python, Blender, Bonsai, IfcOpenShell, paho-mqtt, etc.

  ## **File Structure**

To ensure modularity, scalability, and maintainability, the project is organized as follows:

   `cic_dt_smartlab/`  
   `│`  
   `├── main.py                    # Main entry point for running the digital twin.`  
   `├── dt_config.py               # Configuration settings for the MQTT broker, database, etc.`  
   `├── ifc_parser.py              # Parses the IFC model to extract building geometry and sensor locations.`  
   `├── mqtt_client.py             # Manages MQTT connection, subscriptions, and message handling.`  
   `├── database.py                # Handles database connections, schema definition, and CRUD operations.`  
   `├── visualization.py           # Visualizes sensor data.`  
   `├── blender_visualization.py   # Visualizes sensors and building model in Blender.`        
   `├── shared_topic.json          # Store the same topic of sensor data visualized in Blender and matplotlib.`  
   `├── sensor_data_history.db     # Store the historical sensor data received from the MQTT brocker.` 
   `├── sensor_data_realtime.db    # Store the real-time sensor data for visualization synchronously.`   
   `└── requirements.txt           # List of dependencies (e.g., ifcopenshell, paho-mqtt).`


  ## **Roadmap**

  ### **Current Work**

* **Minimal Viable Program**:  
  * Core files (main.py, config.py, mqtt\_client.py, database.py, visualization.py) are functional.  
  * Sensor data is successfully stored in `sensor_data.db` and visualized in a separate window in real-time.

  ### **Upcoming Work**

* **Coordination**:  
  * Set up a GitHub repository to manage the project and implement a Git workflow.  
  * Define a strategy for sharing large files (IFC models, databases) via Google Drive or other storage solutions.  
* **IFC Model**:  
  * Update and maintain the IFC model with shared access through Google Drive.  
  * Ensure sensor data from MQTT aligns with sensor data in the IFC model.  
* **Visualization**:  
  * Add Blender operators for interactive controls and display sensor data in a pop-up window.  
* **Database**:  
  * Implement two separate databases: one for historical data storage and one for real-time data visualization.

  
