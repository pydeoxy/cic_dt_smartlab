import matplotlib.pyplot as plt
from database import fetch_sensor_data
import datetime, time
import json
import numpy as np
from dt_config import CONFIG, THRESHOLDS
from matplotlib.lines import Line2D

# Function to fetch selected topic from JSON file
def get_selected_topics(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data.get('visual_topics')

# Function to handle plot closure
def on_close(event):
    global visualization_running
    visualization_running = False

# Function to handle key press events
def on_key(event):
    global running,visualization_running
    if event.key == 'escape':  # Check if the ESC key is pressed
        print("Stopping visualization...")
        running = False
        visualization_running = False

# Function to determine status for CO2, temperature and humidity
def determine_status(topic, value):   
    
    # Function to calculate the status and color
    def status_color(value, thresholds, statuses, colors):
        patches = []
        for i in range(len(statuses)):
            patches.append(Line2D([0], [0], marker='o', color='w', markerfacecolor= colors[i], markersize=8, label= statuses[i]))
        if value < thresholds[0]:
            status = statuses[0]
            color = colors[0]           
        elif thresholds[0] <= value < thresholds[1]:
            status = statuses[1]
            color = colors[1]             
        else:
            status = statuses[2]
            color = colors[2]            
        return status, color, patches
    
    if 'CO2-ppm' in topic:
        thresholds = THRESHOLDS['CO2']
        statuses = ['Unoccupied','Occupied','Crowded']
        colors = ['lightgreen','lightyellow','lightcoral']
        return status_color(value, thresholds, statuses, colors)        
        
    elif 'temp' in topic:
        thresholds = THRESHOLDS['TEMPERATURE']
        statuses = ['Cold','Normal','Hot']
        colors = ['lightblue','lightgreen','lightsalmon']
        return status_color(value, thresholds, statuses, colors)       
        
    elif '.rh' in topic.lower():
        thresholds = THRESHOLDS['HUMIDITY']
        statuses = ['Dry','Normal','Moist']
        colors = ['lightblue','lightgreen','lightsalmon']
        return status_color(value, thresholds, statuses, colors)    
            
    else:
        return 'On', 'white', []

# Function to update the plot with real-time data from the database
def visualize_real_time_data(db_path, json_path):
    global visualization_running, running
    visualization_running = True
    running = True

    # Continuously check for updates to the topic or closed plot
    while running:
        # Get the current topic from the JSON file
        topics = get_selected_topics(json_path)

        # Initialize plot
        plt.ion()  # Enable interactive mode
        fig, axs = plt.subplots(len(topics), 1,figsize=(6, 2.5*len(topics)))
        fig.canvas.manager.set_window_title("Real-Time Sensor Data")
        # Position window at (0, 0) in the top-left corner
        plt.tight_layout()
        fig.canvas.manager.window.geometry("+0+0") 
        
        # Normalize axs to a list
        if len(topics) == 1:
            axs = [axs]  # Wrap a single Axes object in a list
        else:
            axs = np.atleast_1d(axs)  # Ensure axs is a 1D array-like object

        # Connect the close event and key press event
        fig.canvas.mpl_connect('close_event', on_close)
        fig.canvas.mpl_connect('key_press_event', on_key)

        visualization_running = True  # Reset to True for the new loop

        while visualization_running: 
            for i, topic in enumerate(topics):
                ax = axs[i]  # Select the corresponding subplot for the sensor
                # Clear the axis to refresh the plot
                ax.clear()

                # Fetch the latest data from the database
                sensor_data = fetch_sensor_data(db_path, topic)

                # Process data for plotting (adjust this if you are visualizing multiple sensors)
                if sensor_data:
                    timestamps = [datetime.datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%S') for row in sensor_data]  # Adjusted format with 'T'
                    values = [row[2] for row in sensor_data]
                    sensor_id = [row[0] for row in sensor_data][0]

                    # Plot data
                    ax.plot(timestamps, values, marker='o', linestyle='-', color='b')

                    # Determine status based on sensor type
                    latest_value = values[-1] if values else None
                    status, color = determine_status(topic, latest_value)[:2]

                    ax.set_facecolor(color)  # Set background color based on status

                    ax.set_title(f"Sensor: {sensor_id}",fontsize=11, fontweight='bold')

                    # Add status annotation
                    ax.annotate(f"Status: {status}",
                                xy=(0.02, 0.93), xycoords='axes fraction',
                                ha='left', va='top', fontsize=9,
                                color='black', bbox=dict(facecolor='white', alpha=0.7))
                
                    # Set x-axis label only for the bottom graph
                    if i == len(topics) - 1:
                        ax.set_xlabel('Timestamp',fontsize=10, fontweight='bold')
                    else:
                        ax.set_xlabel('')
                    ax.set_ylabel('Sensor Value',fontsize=10, fontweight='bold')
                    ax.tick_params(axis='x', labelsize=10)  # Font size for x-axis
                    ax.tick_params(axis='y', labelsize=10)  # Font size for y-axis

                    # Add legend                
                    ax.legend(handles=determine_status(topic, latest_value)[2], loc='upper right', fontsize=8)

            # Add more space between subplots
            plt.subplots_adjust(hspace=0.4)             
            # Pause for a short period to allow for updates
            plt.draw()
            plt.pause(1)  # Pause to allow interactive updates

            # Check if the topic has changed; if so, break to reinitialize
            if topics != get_selected_topics(json_path):
                visualization_running = False  # Stop the current plot to restart
                break

        # Close the plot window when the loop ends
        plt.ioff()  
        plt.close(fig)

        # Small delay to prevent excessive checking
        time.sleep(1)        

# Function to visualize historical data from the database without real-time updates
def visualize_history_data(db_path, topic):
    # Initialize plot
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.canvas.manager.set_window_title("Historical Sensor Data")

    # Fetch all historical data from the database
    sensor_data = fetch_sensor_data(db_path, topic)

    # Process data for plotting
    if sensor_data:
        timestamps = [datetime.datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%S') for row in sensor_data]  # Adjusted format with 'T'
        values = [row[2] for row in sensor_data]
        sensor_ids = [row[0] for row in sensor_data]

        # For simplicity, plot data for the first sensor
        sensor_id_to_plot = sensor_ids[0]
        timestamps_filtered = [timestamps[i] for i in range(len(sensor_ids)) if sensor_ids[i] == sensor_id_to_plot]
        values_filtered = [values[i] for i in range(len(sensor_ids)) if sensor_ids[i] == sensor_id_to_plot]

        # Plot data
        ax.plot(timestamps_filtered, values_filtered, marker='o', linestyle='-', color='b')
        ax.set_title(f"Sensor ID: {sensor_id_to_plot}")
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Sensor Value')
        ax.tick_params(axis='x', rotation=45)

    # Show the plot without updating
    plt.show()

if __name__ == '__main__':    
    from main import TOPIC_FILE_PATH
    #topic = 'KNX/15/0/0<Bathroom.Sensors.CO2-ppm>'
    #visualize_history_data(CONFIG['history_db_path'],topic)
    visualize_real_time_data(CONFIG['realtime_db_path'], TOPIC_FILE_PATH)
