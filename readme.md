# **CiC Digital Twins Project of SmartLab**

## **Project Overview**

The **CiC Digital Twins Project of SmartLab** is a proof-of-concept initiative designed to create a **Digital Twin** for the SmartLab environment. This project integrates real-time sensor data, efficient data management, and 3D visualization to provide a seamless representation of the building and its sensor network. It is part of the **Digital Twins in Construction** course of **Computing in Construction** program at **Metropolia**.

The project demonstrates a practical workflow for building a Minimum Viable Product (MVP) of a small digital twin project, leveraging modern tools like Git, Google Drive, and VS Code for efficient development.

## **Project Objectives**

* **Real-time Integration**: Capture real-time sensor data using MQTT.  
* **Data Management**: Store sensor data in a database with support for Create, Read, Update, Delete (CRUD) operations. 
* **3D Visualization**: Visualize the sensor data and visualize SmartLab building with parts related to corresponding sensor data using Blender.  
* **Modularity and Scalability**: Maintain a well-structured Python codebase that is scalable and easy to maintain.

## **Features**
* Building Information Modeling (BIM) integration using the IFC model.
* Real-time data streaming with MQTT.
* Robust database handling for real-time and historical sensor data.
* Intuitive 3D visualization in Blender with sensor overlays.

## **Tools and Resources**

* **Languages & Frameworks**: Python
* **3D & BIM Tools**: Blender, IfcOpenShell
* **IoT & Messaging**: MQTT, paho-mqtt
* **Database**: SQLite3
* **Version Control**: Git

## **File Structure**

To ensure modularity, scalability, and maintainability, the project is organized as follows:
```
   cic_dt_smartlab/  
   │ 
   ├── main.py                    # Main entry point for running the digital twin.  
   ├── dt_config.py               # Configuration settings for the MQTT broker, database, etc.  
   ├── file_downloader.py         # Download and update the IFC model and excel file of topics/model connections.  
   ├── mqtt_client.py             # Manages MQTT connection, subscriptions, and message handling.  
   ├── database.py                # Handles database connections, schema definition, and CRUD operations.  
   ├── visualization.py           # Visualizes sensor data with pop-up charts.  
   ├── blender_visualization      # Files related to visualization in Blender.    
       │ 
       ├── __init__.py            # List of python files in this folder to be imported in blender_run.py
       ├── actuators.py           # Actuator sensors to be controlled by pushing messages.
       ├── highlight_tools.py     # Highlight display of selected sensors or spaces related to sensor data.
       ├── lights.py              # Facade lights. 
       └── topics.py              # Select MQTT topics to be visualized. 
   │
   ├── sensor_data_history.db     # Store the historical sensor data received from the MQTT brocker.   
   ├── sensor_data_realtime.db    # Store the real-time sensor data for visualization synchronously.   
   ├── requirements.txt           # List of dependencies (e.g., ifcopenshell, paho-mqtt).
   ├── local_files                # Private files to store configuration locally.  
       │ 
       ├── blender_console_import.txt # Command lines running in Blender Console before running blender_run.py.
       ├── smartlab_config.json       # Configuration settings of MQTT broker and shared IFC file.
       ├── shared_topic.json          # The same topic of sensor data visualized in Blender and matplotlib.
       ├── topic_ifc_link.json        # Selected KNX topics and their corrensponding GUIDs in the IFC model.  
       ├── Topic_Ifc_Mapping.csv      # Full MQTT topics and their corrensponding GUIDs in the IFC model.  
       └── smartLab.ifc               # IFC file of the project. 
   
  ```


## **How to Get Started**

### **Prerequisites**

  * Install **Python 3.10+**.  
  * Ensure **Blender 4.2** is installed.

### **Installation**

1. Clone the repository:
  ```
  git clone https://github.com/yourusername/cic-digital-twins.git  
  cd cic-digital-twins
  ```
2. Install dependencies:
  ```
  pip install -r requirements.txt  
  ```
3. Configure `smartlab_config.json` with your MQTT broker, and file id of shared IFC on Goolge Drive.
   Configure `topic_ifc_link.json` with your selected MQTT topics and their corresponding GUIDs in the IFC file.
   Configure `Topic_Ifc_Mapping.csv` with your MQTT topics including actuators and their corresponding GUIDs in the IFC file.

### **Running the Project**

1. Start Blender, open the IFC model, and hide the objects which are not needed to be shown.

2. Start Blender, run the following lines in the Console:
  ```
  import sys
  sys.path.append('<you_path_to_python>\\Scripts')
  sys.path.append('<you_path_to_python>\\site-packages')
  sys.path.append('<you_path_to_local_repository>')  
  ```
  These lines could be saved in blender_console_import.txt.

  Run blender_run.py in Scripting.

3. Switch to BIM view, check Siderbar in the View menu. 
  The following panels are added in the siderbar:
    - MQTT Visualizaiton
    - Visualization tools
    - Lights
    - Actuator Control

4. Choose the MQTT topic to be visualized from the drop-down menu in the MQTT Visualizaiton panel.
    - Click the button to start visualization.
    - Press 'Esc' key to stop the visualization.

4. Choose the MQTT topic of actuators from the drop-down menu in the Actuator Control panel.
    - Check the latest value by click the Show Current Value button.
    - Input the new value in the Payload part and click the Publish Payload to send the value to the actuator sensor to control the related element.

5. Other functions:

* Download and update files:
  ```
  python file_downloader.py  
  ```
  Press 'Yes' in the pop up window to download and update the IFC file and csv file.

## **Details**

### **Real-time Integration**
* Subscribes to topics using **MQTT** to retrieve sensor data in real-time.
* Uses `paho-mqtt` for message handling and updates.

### **Data Management**
* **SQLite3** is used to store:
  * Real-time sensor data (`sensor_data_realtime.db`) for visualization.
  * Historical data (`sensor_data_history.db`) for analytics and audits.

### **Visualization**
1. **2D Visualization**: Displays history or real-time sensor data trends using `visualization.py`.
2. **3D Visualization**:
  * Renders building geometry and overlays sensor data in **Blender**.
  * Supports dynamic updates for real-time exploration.
  * Highlight model elements by changing colors and transparency.
  * Showing colored light of the facade lighting.
  * Control actuator sensors by push message to MQTT client.

## **Extensibility**
This program is designed for flexibility and future development.
* **Customizable MQTT Configuration**: The MQTT broker setup and the mapping between MQTT topics and IFC entities can be tailored to suit your specific requirements.
* **Private Database Support**: You can use your own private database files to ensure data privacy and compatibility.
* **Scalable for Digital Twins**: The program's design allows it to be adapted for other digital twin projects, making it a versatile tool for various applications.
* **Future Development**: Easily extend and enhance the program to meet evolving needs and requirements.