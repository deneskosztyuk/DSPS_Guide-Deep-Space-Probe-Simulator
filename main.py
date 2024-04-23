import os, signal, threading, itertools, requests, tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from datetime import datetime
from flask import Flask, request, jsonify


# Initialize Flask app and queue for sensor data
app = Flask(__name__)

# Initialize global variables for telemetry labels and states
is_connected = False
should_reset = False
temperature_label = None
humidity_label = None
pressure_label = None
date_time_label = None
connection_status_label = None
chat_box = None
on_off_button = None

# Flask route for receiving sensor data
@app.route('/sensor-data', methods=['POST'])
def receive_data():
    global is_connected, should_reset
    if not is_connected:
        return jsonify({"status": "Connection not established"}), 503
    sensor_data = request.json
    print(sensor_data)

    # Update GUI with new sensor data
    update_sensor_data(sensor_data)

    if should_reset:
        should_reset = False  # Reset the flag
        return jsonify("reset"), 200
    else:
        return jsonify({"status": "Data received"}), 200

@app.route('/reset', methods=['POST'])
def reset_device():
    global should_reset
    should_reset = True  # Set the reset flag
    return jsonify({"status": "Reset signal sent"}), 200

# Function to run the Flask server in a background thread
def run_flask_app():
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

# Function to update the labels with sensor data
def update_sensor_data(sensor_data):
    global temperature_label, humidity_label, pressure_label, connection_status_label
    if temperature_label and humidity_label and pressure_label:
        temperature_label.config(text=f"Temperature: {sensor_data.get('temperature', '--')} °C")
        humidity_label.config(text=f"Humidity: {sensor_data.get('humidity', '--')} %")
        pressure_label.config(text=f"Pressure: {sensor_data.get('pressure', '--')} hPa")
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
# Create top bar
def create_top_bar(parent):
    top_bar = tk.Frame(parent, bg="black", height=50)
    top_bar.pack(side="top", fill="x")
    label = tk.Label(top_bar, text="DSPS Control Software", bg="#211f1d", fg="white", anchor="w", font=("Arial", 14))
    label.pack(padx=10)
    return top_bar

# Create left panel
def create_left_panel(parent, width):
    left_frame = tk.Frame(parent, bg='black', width=width, height=290)
    # left_frame.place(x=0, y=29)
    left_frame.pack_propagate(False)
    label = tk.Label(left_frame, text="Probe Live View", bg='#211f1d', fg='white', font=("Arial", 14))
    label.pack()

    gif_path = "src/media/sat_deploy.gif"
    pil_image = Image.open(gif_path)
    frames = [ImageTk.PhotoImage(image.copy()) for image in ImageSequence.Iterator(pil_image)]
    frame_iterator = itertools.cycle(frames)

    image_label = tk.Label(left_frame, image=next(frame_iterator))
    image_label.pack()

    def update_image():
        image_label.configure(image=next(frame_iterator))
        parent.after(100, update_image)

    parent.after(100, update_image)
    return left_frame

# Create right panel
def create_right_panel(parent, width):
    global temperature_label, humidity_label, pressure_label, date_time_label, connection_status_label
    right_frame = tk.Frame(parent, bg='black', width=width, height=290)
    right_frame.pack_propagate(False)
    label = tk.Label(right_frame, text="Live Telemetry", bg='#211f1d', fg='white', font=("Arial", 14))
    label.pack()

    temperature_label = tk.Label(right_frame, text="Temperature: -- °C", bg='black', fg='green', font=("Arial", 14))
    temperature_label.pack(anchor="w")
    humidity_label = tk.Label(right_frame, text="Humidity: -- %", bg='black', fg='green', font=("Arial", 14))
    humidity_label.pack(anchor="w")
    pressure_label = tk.Label(right_frame, text="Pressure: -- hPa", bg='black', fg='green', font=("Arial", 14))
    pressure_label.pack(anchor="w")
    date_time_label = tk.Label(right_frame, text="Date & Time: --", bg='black', fg='green', font=("Arial", 14))
    date_time_label.pack(anchor="w")
    connection_status_label = tk.Label(right_frame, text="Connection Status: Disconnected", bg='black', fg='red', font=("Arial", 14))
    connection_status_label.pack(anchor="w")

    return right_frame

def update_telemetry(temperature, humidity, pressure, date_time, connection_status):
    temperature_label.config(text=f"Temperature: {temperature} °C")
    humidity_label.config(text=f"Humidity: {humidity} %")
    pressure_label.config(text=f"Pressure: {pressure} hPa")
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
            if i*3+j+1 == 9: 
                button = tk.Button(buttons_grid_frame, text="Exit",
                                   command=exit, 
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
        date_time_label.config(text=f"Date & Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
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

    chat_box = tk.Text(bottom_right_frame, height=1, width=59)  #59 
    chat_box.grid(row=0, column=0, sticky="nsew")  
    bottom_right_frame.grid_rowconfigure(0, weight=6)  
    bottom_right_frame.grid_columnconfigure(0, weight=2)  
    chat_box.insert("end", "Welcome to the DSPS Control Software!\n")
    chat_box.insert("end", "To start, use the command buttons on your left. Type "'!help'" for extra console controls.\n")
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
        "!help": lambda: insert_text("Available commands: \n !clear (Clear the console), \n !help (Display all console commands), \n !telon (Turn Telemetry On), \n !teloff (Turn Telemetry Off), \n !exit (Quit Application)"),
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

# Main application window
def main():
    global window
    window = tk.Tk()
    window.title('DSPS Mission Control')
    window.attributes('-fullscreen', True)
    window.resizable(False, False)
    window.configure(bg="#2b0057")

    create_top_bar(window).grid(row=0, column=0, columnspan=2, sticky="nsew")
    create_left_panel(window, 480).grid(row=1, column=0, sticky="nsew")
    create_right_panel(window, 480).grid(row=1, column=1, sticky="nsew")
    create_bottom_left_panel(window, on_off_command).grid(row=2, column=0, sticky="nsew")
    create_bottom_right_panel(window).grid(row=2, column=1, sticky="nsew")

    window.grid_rowconfigure(1, weight=2)  # Allocate space for left and right panels
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)

    window.mainloop()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    main()
