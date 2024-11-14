import matplotlib.pyplot as plt
from database import fetch_sensor_data
import datetime

# Global flag for controlling the visualization loop
visualization_running = True

# Function to handle key press events
def on_key(event):
    global visualization_running
    if event.key == 'escape':  # Check if the ESC key is pressed
        print("Stopping visualization...")
        visualization_running = False

# Function to update the plot with real-time data from the database
def visualize_real_time_data(db_path, topic):
    global visualization_running

    # Initialize plot
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots(figsize=(10, 6))

    # Connect the key press event to the on_key function
    fig.canvas.mpl_connect('key_press_event', on_key)

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

    # Close the plot window when the loop ends
    plt.ioff()
    plt.close()

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
    topic = 'KNX/13/0/0<Livingroom.Sensors.CO2-ppm>'
    #visualize_history_data(CONFIG['history_db_path'],topic)
    visualize_real_time_data(CONFIG['history_db_path'], topic)
