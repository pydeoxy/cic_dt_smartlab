import matplotlib.pyplot as plt
from database import fetch_sensor_data
import datetime, time
import json
import keyboard

# Function to fetch selected topic from JSON file
def get_selected_topic(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data.get('visual_topic')

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

# Function to update the plot with real-time data from the database
def visualize_real_time_data(db_path, json_path):
    global visualization_running, running
    visualization_running = True
    running = True

    # Continuously check for updates to the topic or closed plot
    while running:
        # Get the current topic from the JSON file
        topic = get_selected_topic(json_path)

        # Initialize plot
        plt.ion()  # Enable interactive mode
        fig, ax = plt.subplots(figsize=(6, 4))

        # Connect the close event and key press event
        fig.canvas.mpl_connect('close_event', on_close)
        fig.canvas.mpl_connect('key_press_event', on_key)

        visualization_running = True  # Reset to True for the new loop

        while visualization_running: 
            # Clear the axis to refresh the plot
            ax.clear()

            # Fetch the latest data from the database
            sensor_data = fetch_sensor_data(db_path, topic)

            # Process data for plotting (adjust this if you are visualizing multiple sensors)
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
                ax.set_title(f"Real-Time Sensor Data for Sensor ID: {sensor_id_to_plot}")
                ax.set_xlabel('Timestamp')
                ax.set_ylabel('Sensor Value')
                ax.tick_params(axis='x', rotation=45)

            # Pause for a short period to allow for updates
            plt.draw()
            plt.pause(1)  # Pause to allow interactive updates

            # Check if the topic has changed; if so, break to reinitialize
            if topic != get_selected_topic(json_path):
                visualization_running = False  # Stop the current plot to restart
                break

        # Close the plot window when the loop ends
        plt.ioff()  
        plt.close(fig)

        # Small delay to prevent excessive checking
        time.sleep(1)

        if keyboard.is_pressed('esc'):
            print("Esc pressed. Exiting...")
            break

# Function to visualize historical data from the database without real-time updates
def visualize_history_data(db_path, topic):
    # Initialize plot
    fig, ax = plt.subplots(figsize=(10, 6))

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
        ax.set_title(f"Historical Sensor Data for Sensor ID: {sensor_id_to_plot}")
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Sensor Value')
        ax.tick_params(axis='x', rotation=45)

    # Show the plot without updating
    plt.show()

if __name__ == '__main__':
    from dt_config import CONFIG
    from main import TOPIC_FILE_PATH
    #visualize_history_data(CONFIG['history_db_path'],topic)
    visualize_real_time_data(CONFIG['realtime_db_path'], TOPIC_FILE_PATH)
