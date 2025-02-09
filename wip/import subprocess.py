import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import base64
import datetime
import dash_bootstrap_components as dbc
import webbrowser  # Import webbrowser module to open the browser automatically
from database import fetch_sensor_data
from dt_config import CONFIG

# Set Matplotlib to non-GUI backend
matplotlib.use('Agg')

# Constants for thresholds
OCCUPANCY_THRESHOLD = 429.5  # CO2 occupancy threshold
SAFETY_THRESHOLD = 1000      # CO2 safety threshold
TEMPERATURE_LOW = 18
TEMPERATURE_HIGH = 24
HUMIDITY_LOW = 30
HUMIDITY_HIGH = 60

# Initialize Dash app with Bootstrap for styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Real-Time Sensor Dashboard"

# Function to determine the status and background color
def determine_status(value, low, high):
    if value is None:
        return "No Data", "white"
    if value < low:
        return "Low", 'lightblue'
    elif value > high:
        return "High", 'lightsalmon'
    else:
        return "Normal", 'lightgreen'

# Function to generate plots with status, colors, and a legend
def generate_plot(room_type):
    room_topics = {
        'Bedroom': [
            "KNX/14/0/0<Bedroom.Sensors.CO2-ppm>",
            "KNX/14/0/2<Bedroom.Sensors.Air-temperature-C>",
            "KNX/14/0/1<Bedroom.Sensors.Rh-percent>"
        ],
        'Living Room': [
            "KNX/13/0/0<Livingroom.Sensors.CO2-ppm>",
            "KNX/13/0/2<Livingroom.Sensors.Air-temperature-C>",
            "KNX/13/0/1<Livingroom.Sensors.Rh-percent>"
        ],
        'Bathroom': [
            "KNX/15/0/0<Bathroom.Sensors.CO2-ppm>",
            "KNX/15/0/2<Bathroom.Sensors.Air-temperature-C>",
            "KNX/15/0/1<Bathroom.Sensors.RH|percent>"
        ]
    }.get(room_type, [])

    fig, axs = plt.subplots(len(room_topics), 1, figsize=(10, 12))
    alerts = []  # Store alerts to be triggered

    for i, topic in enumerate(room_topics):
        ax = axs[i]
        sensor_data = fetch_sensor_data(CONFIG['realtime_db_path'], topic)
        if sensor_data:
            timestamps = [datetime.datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%S') for row in sensor_data]
            values = [row[2] for row in sensor_data]

            # Determine latest value and status
            latest_value = values[-1] if values else None
            if topic.endswith("CO2-ppm>"):
                status, color = ("Occupied", 'lightcoral') if latest_value and latest_value > OCCUPANCY_THRESHOLD else ("Unoccupied", 'lightgreen')
                if latest_value and latest_value > OCCUPANCY_THRESHOLD:
                    alerts.append(f"CO2 level in {room_type} is high: {latest_value} ppm (Exceeds occupancy threshold).")
                if latest_value and latest_value > SAFETY_THRESHOLD:
                    alerts.append(f"CO2 level in {room_type} is extremely high: {latest_value} ppm (Exceeds safety threshold).")
            elif topic.endswith("Air-temperature-C>"):
                status, color = determine_status(latest_value, TEMPERATURE_LOW, TEMPERATURE_HIGH)
                if latest_value and latest_value < TEMPERATURE_LOW:
                    alerts.append(f"Temperature in {room_type} is low: {latest_value} °C (Below minimum threshold).")
                if latest_value and latest_value > TEMPERATURE_HIGH:
                    alerts.append(f"Temperature in {room_type} is high: {latest_value} °C (Above maximum threshold).")
            elif topic.endswith("Rh-percent>"):
                status, color = determine_status(latest_value, HUMIDITY_LOW, HUMIDITY_HIGH)
                if latest_value and latest_value < HUMIDITY_LOW:
                    alerts.append(f"Humidity in {room_type} is low: {latest_value} % (Below minimum threshold).")
                if latest_value and latest_value > HUMIDITY_HIGH:
                    alerts.append(f"Humidity in {room_type} is high: {latest_value} % (Above maximum threshold).")
            else:
                status, color = "Unknown", "white"

            # Plot data
            ax.plot(timestamps, values, marker='o', linestyle='-', label=f"{topic.split('<')[1].split('>')[0]}")
            ax.set_facecolor(color)

            # Add annotations and titles
            ax.annotate(f"Status: {status}", xy=(0.5, 0.95), xycoords='axes fraction',
                        ha='center', fontsize=10, color='black',
                        bbox=dict(facecolor='white', alpha=0.7))
            ax.set_title(f"Sensor: {topic.split('<')[1].split('>')[0]}", fontsize=12)
            ax.set_ylabel("Value")
            if i == len(room_topics) - 1:
                ax.set_xlabel("Timestamp")
        else:
            ax.text(0.5, 0.5, "No Data Available", horizontalalignment='center', verticalalignment='center',
                    fontsize=12, transform=ax.transAxes)
            ax.set_facecolor("white")
    plt.tight_layout()

    # Convert plot to base64
    buf = BytesIO()
    FigureCanvas(fig).print_png(buf)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return img_str, alerts

# Layout
app.layout = html.Div(
    [
        html.H1("Real-Time Sensor Dashboard", style={"text-align": "center", "font-size": "28px", "color": "#333", "margin-bottom": "20px"}),
        dcc.Dropdown(
            id='room-dropdown',
            options=[
                {'label': 'Bedroom', 'value': 'Bedroom'},
                {'label': 'Living Room', 'value': 'Living Room'},
                {'label': 'Bathroom', 'value': 'Bathroom'}
            ],
            value='Bedroom',
            style={'width': '50%', 'margin': 'auto', 'margin-bottom': '20px'}
        ),
        dbc.Container(id='graph-container', style={"background-color": "#fff", "padding": "20px", "border-radius": "8px",
                                                   "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}),
        # Modal for alerts
        dbc.Modal(
            [
                dbc.ModalHeader("Alert", style={"background-color": "lightcoral"}),
                dbc.ModalBody(id="modal-body"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto", n_clicks=0)
                ),
            ],
            id="alert-modal",
            is_open=False,
        ),
        dcc.Interval(
            id='graph-update-interval',
            interval=10000,  # Update every 10 seconds
            n_intervals=0
        )
    ],
    style={"font-family": "Century Gothic", "background-color": "#f8f9fa", "padding": "20px"}
)

# Callback for updating graphs and displaying alerts in a modal dialog
@app.callback(
    [Output('graph-container', 'children'),
     Output('modal-body', 'children'),
     Output('alert-modal', 'is_open')],
    [Input('room-dropdown', 'value'),
     Input('graph-update-interval', 'n_intervals'),
     Input('close', 'n_clicks')]  # Close button in modal
)
def update_graph_and_alerts(room, n_intervals, close_clicks):
    img_str, alerts = generate_plot(room)
    
    # Display the alerts as a list of alert messages in the modal
    alert_text = html.Div([html.P(alert) for alert in alerts])

    # Open the modal if there are alerts, otherwise close it
    modal_is_open = bool(alerts) and close_clicks == 0

    return dbc.Row(
               dbc.Col(html.Img(src=f"data:image/png;base64,{img_str}", style={'width': '100%'}))
           ), alert_text, modal_is_open  # Return alerts in the modal dialog

if __name__ == '__main__':
    # Open the browser automatically
    webbrowser.open("http://127.0.0.1:8050/")  # Open the Dash app in the default browser
    app.run_server(debug=True, use_reloader=False)  # Disable the reloader to prevent opening multiple tabs    