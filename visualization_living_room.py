import matplotlib.pyplot as plt
from database import fetch_sensor_data
import datetime
import json
import time
from matplotlib.lines import Line2D

# Constants for thresholds
OCCUPANCY_THRESHOLD = 429.5  # CO2 value (ppm) above which room is considered occupied
TEMPERATURE_LOW = 18  # Temperature below this value is considered low
TEMPERATURE_HIGH = 24  # Temperature above this value is considered high
HUMIDITY_LOW = 30  # Humidity below this value is considered low
HUMIDITY_HIGH = 60  # Humidity above this value is considered high

# Function to fetch selected topics from JSON file
def get_selected_topics(json_path):
    """Fetch all selected topics from the shared JSON file."""
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data.get('visual_topics', [])

# Function to handle plot closure
def on_close(event):
    global running
    print("Visualization window closed.")
    running = False

# Function to handle key press events
def on_key(event):
    global running
    if event.key == 'escape':  # Check if the ESC key is pressed
        print("Stopping visualization...")
        running = False

# Function to determine status for temperature and humidity
def determine_status(value, low, high):
    if value < low:
        return "Low", 'lightblue'
    elif value > high:
        return "High", 'lightsalmon'
    else:
        return "Normal", 'lightgreen'

# Function to update the plot with real-time data from the database
def visualize_real_time_data(db_path, json_path):
    global running
    running = True

    # Get topics dynamically from the JSON file
    original_topics = get_selected_topics(json_path)
    living_room_topics = [
        "KNX/13/0/0<Livingroom.Sensors.CO2-ppm>",  # CO2
        "KNX/13/0/2<Livingroom.Sensors.Air-temperature-C>",  # Air Temperature
        "KNX/13/0/1<Livingroom.Sensors.Rh-percent>"  # Relative Humidity
    ]

    # Set up the figure and subplots
    fig, axs = plt.subplots(len(living_room_topics), 1, figsize=(10, 12))  # Subplots for each topic

    # Connect the close event and key press event
    fig.canvas.mpl_connect('close_event', on_close)
    fig.canvas.mpl_connect('key_press_event', on_key)

    # Create the custom legend for occupancy and statuses
    occupied_patch = Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', markersize=10, label="Occupied")
    unoccupied_patch = Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=10, label="Unoccupied")
    low_patch = Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=10, label="Low")
    normal_patch = Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=10, label="Normal")
    high_patch = Line2D([0], [0], marker='o', color='w', markerfacecolor='lightsalmon', markersize=10, label="High")

    while running:
        for i, topic in enumerate(living_room_topics):
            ax = axs[i]  # Select the corresponding subplot for the sensor
            
            # Clear the axis to refresh the plot
            ax.clear()

            # Fetch the latest data from the database for the topic
            sensor_data = fetch_sensor_data(db_path, topic)

            # Process data for plotting
            if sensor_data:
                timestamps = [datetime.datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%S') for row in sensor_data]
                values = [row[2] for row in sensor_data]

                # Plot data for this topic
                ax.plot(timestamps, values, marker='o', linestyle='-', label=topic)

                # Determine status based on sensor type
                latest_value = values[-1] if values else None
                if topic.endswith("CO2-ppm>"):
                    if latest_value and latest_value > OCCUPANCY_THRESHOLD:
                        status = "Occupied"
                        color = 'lightcoral'
                    else:
                        status = "Unoccupied"
                        color = 'lightgreen'
                elif topic.endswith("Air-temperature-C>"):
                    status, color = determine_status(latest_value, TEMPERATURE_LOW, TEMPERATURE_HIGH)
                elif topic.endswith("Rh-percent>"):
                    status, color = determine_status(latest_value, HUMIDITY_LOW, HUMIDITY_HIGH)
                else:
                    status, color = "Unknown", 'white'

                ax.set_facecolor(color)  # Set background color based on status

                # Set title for each graph
                ax.set_title(f"Real-Time Sensor Data: {topic}", fontsize=14)

                # Add status annotation
                ax.annotate(f"Status: {status}",
                            xy=(0.5, 0.95), xycoords='axes fraction',
                            ha='center', va='center', fontsize=12,
                            color='black', bbox=dict(facecolor='white', alpha=0.7))

                # Set x-axis label only for the bottom graph
                if i == len(living_room_topics) - 1:
                    ax.set_xlabel('Timestamp')
                else:
                    ax.set_xlabel('')

                # Set y-axis label
                ax.set_ylabel('Value')

                # Add legend
                if topic.endswith("CO2-ppm>"):
                    ax.legend(handles=[occupied_patch, unoccupied_patch], loc='upper right', fontsize=10)
                else:
                    ax.legend(handles=[low_patch, normal_patch, high_patch], loc='upper right', fontsize=10)

        # Add more space between subplots
        plt.subplots_adjust(hspace=0.4)

        # Redraw the plot
        plt.draw()
        plt.pause(1)

    plt.ioff()
    plt.close(fig)
    print("Visualization stopped.")

if __name__ == '__main__':
    from dt_config import CONFIG
    from main import TOPIC_FILE_PATH
    visualize_real_time_data(CONFIG['realtime_db_path'], TOPIC_FILE_PATH)
