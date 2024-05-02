import os, signal, threading, itertools, requests, tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from datetime import datetime
from flask import Flask, request, jsonify
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.gridspec as gridspec
import math


# Initialize Flask app and queue for sensor data
app = Flask(__name__)

# Initialize global variables for telemetry labels and states
is_connected = False
should_reset = False
temperature_label = None
humidity_label = None
pressure_label = None
altitude_label = None
date_time_label = None
connection_status_label = None
chat_box = None
on_off_button = None
temperature_data = []
humidity_data = []
altitude_data = []
graphs = {}


@app.route('/sensor-data', methods=['POST'])
def receive_data():
    global is_connected, should_reset
    if not is_connected:
        return jsonify({"status": "Connection not established"}), 503
    try:
        sensor_data = request.json
        temperature = sensor_data.get("temperature")
        humidity = sensor_data.get("humidity")
        altitude = sensor_data.get("altitude")
        if temperature is not None and humidity is not None and altitude is not None:
            on_data_received(sensor_data, graphs)
            if should_reset:
                should_reset = False
                return jsonify("reset"), 200
            else:
                return jsonify({"status": "Data received"}), 200
        else:
            return jsonify({"error": "Missing data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reset', methods=['POST'])
def reset_device():
    global should_reset
    should_reset = True
    return jsonify({"status": "Reset signal sent"}), 200

def run_flask_app():
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

# Function to update the labels with sensor data
def update_sensor_data(sensor_data):
    global temperature_label, humidity_label, pressure_label, altitude_label, connection_status_label
    if temperature_label and humidity_label and pressure_label:
        temperature_label.config(text=f"Temperature: {sensor_data.get('temperature', '--')} °C")
        humidity_label.config(text=f"Humidity: {sensor_data.get('humidity', '--')} %")
        pressure_label.config(text=f"Pressure: {sensor_data.get('pressure', '--')} hPa")
        altitude_label.config(text=f"Altitude: {sensor_data.get('altitude', '--')} m")
        connection_status_label.config(text="Connection Status: Connected", fg='green')
    else:
        connection_status_label.config(text="Connection Status: Disconnected", fg='red')

# Function to toggle the reset state
def send_reset_command():
    response = requests.post('http://localhost:5000/reset')
    if response.ok:
        print("Reset command sent successfully")
    else:
        print("Failed to send reset command")

# GUI Functions
def create_top_bar(parent):
    top_bar = tk.Frame(parent, bg="black", height=50)
    top_bar.pack(side="top", fill="x")
    label = tk.Label(top_bar, text="DSPS Control Software", bg="#211f1d", fg="white", anchor="w", font=("Arial", 14))
    label.pack(padx=10)
    return top_bar

def setup_figure():
    # Adjust figsize to be smaller or to fit better with other panels
    fig = Figure(figsize=(6, 3))  # Adjust width and height to fit the GUI layout
    gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])  # Keep the layout of one large and two small graphs
    return fig, gs


def update_graph(canvas, ax, data, label):
    ax.clear()
    num_data_points = len(data)
    max_ticks = 10  # Maximum number of ticks to display on the X-axis

    # Determine the interval between ticks based on the number of data points
    tick_interval = max(1, math.ceil(num_data_points / max_ticks))
    x_ticks = list(range(0, num_data_points, tick_interval))

    # Slice the data according to the tick interval for plotting
    plot_data = data[::tick_interval]

    ax.plot(x_ticks, plot_data, label=label)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(i * tick_interval + 1) for i in range(len(x_ticks))])

    # Set Y-ticks based on the plot data
    if all(isinstance(x, (int, float)) for x in plot_data):
        ax.set_yticks(plot_data)
        ax.set_yticklabels([f"{val:.1f}" for val in plot_data])

    ax.legend()
    ax.set_xlabel('Time (indices)')
    ax.set_ylabel(label)
    canvas.draw()


# Create left panel
def create_left_panel(parent, width):
    # Adjust the frame size to better match other panels
    left_frame = tk.Frame(parent, bg='black', width=width, height=300)  # Adjusted height to match other panels
    left_frame.grid(row=1, column=0, sticky="nsew")
    left_frame.grid_propagate(False)  # Prevents the frame from resizing to fit the canvas

    fig, gs = setup_figure()
    graphs = {
        "Temperature (°C)": (fig.add_subplot(gs[0, :]), None),
        "Humidity (%)": (fig.add_subplot(gs[1, 0]), None),
        "Altitude (m)": (fig.add_subplot(gs[1, 1]), None)
    }

    # Setup canvas once and apply to all graphs
    canvas = FigureCanvasTkAgg(fig, master=left_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Use pack with fill and expand for better resizing

    for label, (ax, _) in graphs.items():
        ax.set_title(f'{label}')
        graphs[label] = (canvas, ax)

    return left_frame, graphs

def handle_new_data(graphs, temperature, humidity, altitude):
    temperature_data.append(temperature)
    humidity_data.append(humidity)
    altitude_data.append(altitude)

    # Update each graph with new data
    update_graph(*graphs["Temperature (°C)"], temperature_data, "Temperature (°C)")
    update_graph(*graphs["Humidity (%)"], humidity_data, "Humidity (%)")
    update_graph(*graphs["Altitude (m)"], altitude_data, "Altitude (m)")

# Assuming this function is called when new data is received
def on_data_received(new_data, graphs):
    temperature = new_data.get("temperature", 0)
    humidity = new_data.get("humidity", 0)
    altitude = new_data.get("altitude", 0)
    handle_new_data(graphs, temperature, humidity, altitude)
    update_sensor_data(new_data) 



def create_right_panel(parent, width):
    global temperature_label, humidity_label, pressure_label, altitude_label, date_time_label, connection_status_label
    right_frame = tk.Frame(parent, bg='black', width=width, height=290)
    right_frame.pack_propagate(False)

    # Setup for telemetry labels
    labels_frame = tk.Frame(right_frame, bg='black')
    labels_frame.pack(side="left", fill="both", expand=True)

    temperature_label = tk.Label(labels_frame, text="Temperature: -- °C", bg='black', fg='green', font=("Arial", 14))
    temperature_label.pack(anchor="w")
    humidity_label = tk.Label(labels_frame, text="Humidity: -- %", bg='black', fg='green', font=("Arial", 14))
    humidity_label.pack(anchor="w")
    pressure_label = tk.Label(labels_frame, text="Pressure: -- hPa", bg='black', fg='green', font=("Arial", 14))
    pressure_label.pack(anchor="w")
    altitude_label = tk.Label(labels_frame, text="Approx Altitude: -- m", bg='black', fg='green', font=("Arial", 14))
    altitude_label.pack(anchor="w")
    date_time_label = tk.Label(labels_frame, text="Date & Time: --", bg='black', fg='green', font=("Arial", 14))
    date_time_label.pack(anchor="w")
    connection_status_label = tk.Label(labels_frame, text="Connection Status: Disconnected", bg='black', fg='red', font=("Arial", 14))
    connection_status_label.pack(anchor="w")

    # Simulation sub-frame
    sim_frame = tk.Frame(right_frame, bg='black', width=width//3)
    sim_frame.pack(side="right", fill="both", expand=True)
    canvas = tk.Canvas(sim_frame, bg='black', width=200, height=290)
    canvas.pack(fill="both", expand=True)
    canvas.create_arc(10, 100, 190, 280, start=0, extent=180, fill='blue')  # Earth
    canvas.create_oval(30, 120, 170, 260, outline='green')  # Orbit path
    satellite_id = canvas.create_oval(145, 185, 155, 195, fill='red')  # Satellite
    
    def update_satellite_position(angle):
        # Calculate new position along the orbit
        radius = 70
        center_x, center_y = 100, 190
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        canvas.coords(satellite_id, x-5, y-5, x+5, y+5)
        
        # Schedule next update
        angle += math.radians(5)
        parent.after(1000, lambda: update_satellite_position(angle))

    update_satellite_position(0)  # Start the animation

    return right_frame



def update_telemetry(temperature, humidity, pressure, altitude, date_time, connection_status):
    temperature_label.config(text=f"Temperature: {temperature} °C")
    humidity_label.config(text=f"Humidity: {humidity} %")
    pressure_label.config(text=f"Pressure: {pressure} hPa")
    altitude_label.config(text=f"Approx Altitude: {altitude} m")
    date_time_label.config(text=f"Date & Time: {date_time}")
    connection_status_label.config(text=f"Connection Status: {connection_status}")


def create_bottom_left_panel(parent, on_off_command):
    global on_off_button
    # Define the width and height of the buttons
    button_width = 15
    button_height = 3
    
    bottom_left_frame = tk.Frame(parent, bg='black')
    bottom_left_frame.grid(row=2, column=0, sticky="nsew")
    parent.grid_rowconfigure(2, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    # Buttons grid frame for 3x3 button layout
    buttons_grid_frame = tk.Frame(bottom_left_frame, bg='black')
    buttons_grid_frame.grid(row=0, column=1, sticky="nsew")

    # Create and grid buttons
    for i in range(3):
        for j in range(3):
            if i*3+j+1 == 9:  # If this is the 9th button
                button = tk.Button(buttons_grid_frame, text="Exit",
                                   command=exit,  # Set the command to exit
                                   bg="red", fg="white", font=("Arial", 10),
                                   width=button_width, height=button_height)
            else:
                button = tk.Button(buttons_grid_frame, text=f"Button {i*3+j+1}",
                                   bg="#211f1d", fg="white", font=("Arial", 10),
                                   width=button_width, height=button_height)
            button.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
        buttons_grid_frame.grid_rowconfigure(i, weight=1)
        buttons_grid_frame.grid_columnconfigure(j, weight=1)

    # Add empty columns on either side of the buttons
    bottom_left_frame.grid_columnconfigure(0, weight=1)
    bottom_left_frame.grid_columnconfigure(2, weight=1)

    # Function to toggle the indicator color
    def toggle_indicator(button, color):
        button.config(bg=color)

    # Create the 'On/Off' button and indicator
    on_off_button = tk.Button(buttons_grid_frame, text="Telemetry On/Off", command=on_off_command, bg="#211f1d", fg="white", font=("Arial", 10), width=button_width, height=button_height)
    on_off_button.grid(row=0, column=0, padx=10, pady=10)

    # Create the 'Reset' button and binding to press and release
    reset_button = tk.Button(buttons_grid_frame, text="Reset Device", bg='green', fg="white", font=("Arial", 10), width=button_width, height=button_height)
    reset_button.grid(row=0, column=1, padx=10, pady=10)
    reset_button.bind('<ButtonPress>', lambda event: toggle_indicator(reset_button, 'red'))
    reset_button.bind('<ButtonRelease>', lambda event: toggle_indicator(reset_button, 'green'))
    reset_button.bind('<ButtonRelease>', lambda event: send_reset_command())

    return bottom_left_frame

def update_date_time():
    if is_connected:
        now = datetime.now()
        date_time_label.config(text=f"Date & Time: {now.strftime('%d-%m-%Y %H:%M:%S')}")
        # Call this function again after 1000 ms (1 second)
        window.after(1000, update_date_time)

# Define the commands for the buttons
def on_off_command():
    global is_connected, connection_status_label, temperature_label, humidity_label, pressure_label, date_time_label, on_off_button, chat_box
    is_connected = not is_connected
    status_text = "Connected" if is_connected else "Disconnected"  # Define status_text based on is_connected
    button_color = "green" if is_connected else "red"
    on_off_button.config(bg=button_color)
    connection_status_label.config(text=f"Connection Status: {status_text}", fg='green' if is_connected else 'red')
    # Update the chat box with the connection status
    if chat_box:
        chat_box.config(state='normal')
        chat_box.insert(tk.END, f"Connection Status: {status_text}\n")
        chat_box.see(tk.END)
    if not is_connected:
        temperature_label.config(text="Temperature: -- °C")
        humidity_label.config(text="Humidity: -- %")
        pressure_label.config(text="Pressure: -- hPa")
        altitude_label.config(text="Aprox Altitude: -- m")
        date_time_label.config(text="Date & Time: --")
    chat_box.config(state='disabled')
    if is_connected:
        # Start updating date and time every second
        update_date_time()
    

# Function to toggle the indicator color
def toggle_indicator(button, color):
    button.config(bg=color)

def create_bottom_right_panel(parent):
    global chat_box
    # Chat and Prompt boxes frame to the right of the buttons
    bottom_right_frame = tk.Frame(parent, bg='green')  # Changed bg to green for visibility
    bottom_right_frame.grid(row=2, column=1, sticky="nsew")
    parent.grid_columnconfigure(1, weight=1)

    chat_box = tk.Text(bottom_right_frame, height=1, width=59)  #59 Adjust height and width
    chat_box.grid(row=0, column=0, sticky="nsew")  
    bottom_right_frame.grid_rowconfigure(0, weight=6)  
    bottom_right_frame.grid_columnconfigure(0, weight=2)  
    chat_box.insert("end", "Welcome to the DSPS Control Software!\n")
    chat_box.insert("end", "To start, use the command buttons on your left. \nType "'!help'" for extra console controls.\n")
    chat_box.config(state="disabled")  # Disable the chat box

    input_area = tk.Entry(bottom_right_frame, font=('Arial', 16))
    input_area.grid(row=1, column=0, sticky="ew", columnspan=2, pady=5)

    def send_message(event):
        message = input_area.get()  # Get the message from the input area
        insert_text(message)  # Add the message to the text box
        input_area.delete(0, "end")  # Clear the input area

    input_area.bind("<Return>", send_message) # Bind the 'Return' key to the send_message function  

    # Define the commands
    commands = {
        "!clear": lambda: clear_chat_box(),
        "!help": lambda: insert_text("Available commands: \n !clear (Clear the console) \n !help (Display all console commands) \n !telon (Turn Telemetry On) \n !teloff (Turn Telemetry Off) \n !exit (Quit Application)"),
        "!telon": lambda: on_off_command(),
        "!teloff": lambda: on_off_command(),
        "!exit": lambda: exit_software(),
        # More commands if need be 
    }

    def clear_chat_box():
        chat_box.config(state="normal")  # Enable the chat box
        chat_box.delete(1.0, "end")  # Delete all text in the chat box
        chat_box.config(state="disabled")  # Disable the chat box again

    def send_message(event):
        message = input_area.get()  # Get the message from the input area
        if message in commands:  # If the message is a command
            commands[message]()  # Execute the command
        else:
            insert_text(message)  # Add the message to the text box
        input_area.delete(0, "end")  # Clear the input area
    input_area.bind("<Return>", send_message) 

    return bottom_right_frame

# Function to insert text into the chat box
def insert_text(text):
    if chat_box:  # Check if the chat box is initialized
        chat_box.config(state="normal")  # Enable the chat box to insert text
        chat_box.insert("end", text + "\n")  # Insert the text
        chat_box.see("end")  # Scroll to the bottom
        chat_box.config(state="disabled")  # Disable the chat box again

def exit_software():
    # Function to exit the software
    insert_text("Exiting DSPS Control Software...")
    try:
        # This is how you would typically stop a Flask server running in debug mode
        os.kill(os.getpid(), signal.SIGINT)
    except Exception as e:
        insert_text(f"Failed to stop Flask server: {e}")

    # Close the Tkinter window
    window.destroy()

def main():
    global window, graphs
    window = tk.Tk()
    window.title('DSPS Mission Control')
    window.configure(bg="#2b0057")

    create_top_bar(window).grid(row=0, column=0, columnspan=2, sticky="nsew")
    left_panel, graphs = create_left_panel(window, 480)
    left_panel.grid(row=1, column=0, sticky="nsew")
    create_right_panel(window, 480).grid(row=1, column=1, sticky="nsew")

    # Ensure equal size for bottom panels
    bottom_left_panel = create_bottom_left_panel(window, on_off_command)
    bottom_right_panel = create_bottom_right_panel(window)
    bottom_left_panel.grid(row=2, column=0, sticky="nsew")
    bottom_right_panel.grid(row=2, column=1, sticky="nsew")
    
    window.grid_rowconfigure(1, weight=1)
    window.grid_rowconfigure(2, weight=1)  # Ensure both panels in row 2 have equal weight
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)

    window.mainloop()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    main()
