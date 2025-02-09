import subprocess
import threading
import time
import sys

def stream_output(process, label):
    """Streams output (stdout and stderr) from a subprocess in real-time."""
    for line in iter(process.stdout.readline, ''):
        print(f"{label}: {line.strip()}")
    for line in iter(process.stderr.readline, ''):
        print(f"{label} [Error]: {line.strip()}")

def run_mqtt_and_dashboard():
    try:
        # Run main.py (MQTT client) in the background
        mqtt_process = subprocess.Popen(
            [sys.executable, 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True
        )
        print("Running MQTT client (main.py)...")

        # Run import_subprocess.py (Dash App) in the background
        dash_process = subprocess.Popen(
            [sys.executable, 'import subprocess.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True
        )
        print("Running Dash App (import subprocess.py)...")

        # Create threads to stream output from both processes
        mqtt_thread = threading.Thread(target=stream_output, args=(mqtt_process, "MQTT"))
        dash_thread = threading.Thread(target=stream_output, args=(dash_process, "Dash App"))

        mqtt_thread.start()
        dash_thread.start()

        # Wait for both threads to finish
        mqtt_thread.join()
        dash_thread.join()

        # Wait for both processes to complete (if they terminate)
        mqtt_process.wait()
        dash_process.wait()

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Ensure both processes are terminated properly if the script ends unexpectedly
        mqtt_process.terminate()
        dash_process.terminate()

if __name__ == "__main__":
    run_mqtt_and_dashboard()
