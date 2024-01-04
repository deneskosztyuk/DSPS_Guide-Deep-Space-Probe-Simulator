import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import itertools

def create_top_bar(parent):
    # Creating a top bar frame
    top_bar = tk.Frame(parent, bg="black", height=50)  # Set a distinct background color
    top_bar.pack(side="top", fill="x")  # Fill the frame along the x-axis
    # Creating a label in the top bar
    label = tk.Label(top_bar, text="DSPS Control Software", bg="#211f1d", fg="white", anchor="w", font=("Arial", 14))  # Adjusted text color to white
    label.pack(padx=10)  # Padding for some space from the left edge

    return top_bar

def create_left_panel(parent, width):
    left_frame = tk.Frame(parent, bg='black', width=width, height=290)
    left_frame.place(x=0, y=29)
    left_frame.pack_propagate(False)  # Prevent widgets from changing frame's size
    label = tk.Label(left_frame, text="Probe Live View", bg='#211f1d', fg='white', font=("Arial", 14))
    label.pack()

    # Load the GIF with Pillow
    gif_path = "media/sat_deploy.gif"
    pil_image = Image.open(gif_path)
    frames = [ImageTk.PhotoImage(image.copy()) for image in ImageSequence.Iterator(pil_image)]
    frame_iterator = itertools.cycle(frames)

    image_label = tk.Label(left_frame, image=next(frame_iterator))
    image_label.pack()  # Use pack here instead of grid

    # Function to update the label with the next GIF frame
    def update_image():
        image_label.configure(image=next(frame_iterator))
        parent.after(100, update_image)  # Adjust the delay as needed

    # Start the animation
    parent.after(100, update_image)
    return left_frame

def create_right_panel(parent, width):
    right_frame = tk.Frame(parent, bg='black', width=width, height=290)  # Use the provided width
    right_frame.place(x=width, y=29)  # Position it to the right of the left panel
    right_frame.pack_propagate(False)  # Prevent widgets from changing frame's size
    label = tk.Label(right_frame, text="Live Telemetry", bg='#211f1d', fg='white', font=("Arial", 14))
    label.pack()

    # Create labels for each line of text
    text_labels = [
        "Humidity: 0.05%",
        "Atmospheric pressure: 6013 hPa",
        "Temperature: -165°C",
        "Time: 12:41 PM"
    ]

    # Add the text labels to the right frame with green color
    for text in text_labels:
        label = tk.Label(right_frame, text=text, bg='black', fg='green', font=("Arial", 14))  # Adjusted text color to green
        label.pack(anchor="w")  # Align the text to the left



    return right_frame

def create_bottom_panel(parent):
    button_frame = tk.Frame(parent, bg='black', height=100)
    button_frame.pack(side="bottom", fill="x")

    # Define the width of the buttons (you can adjust this value)
    button_width = 18
    button_height = 5

    indicators = {}

    # Function to toggle the indicator color
    def toggle_indicator(canvas, color):
        canvas.config(bg=color)
        canvas.itemconfig("indicator", fill=color)

    # Define the commands for the buttons
    def on_off_command():
        toggle_indicator(indicators['On/Off'], 'green' if indicators['On/Off'].cget("bg") == 'red' else 'red')
        print("Toggled On/Off")

    def solar_panel_deployment_command():
        toggle_indicator(indicators["Solar Panel \n Deployment"], 'green' if indicators["Solar Panel \n Deployment"].cget("bg") == 'red' else 'red')
        print("Solar Panel \n Deployment")

    def receive_telemetry_data_command():
        toggle_indicator(indicators["Receiving telemetry data"],'green' if indicators["Receiving telemetry data"].cget("bg") == 'red' else 'red')
        print("Receiving telemetry data")

    def change_to_camera_view_command():
        toggle_indicator(indicators["Change to \n Camera View"],'green' if indicators["Change to \n Camera View"].cget("bg") == 'red' else 'red')
        print("Change to Camera View")

    def change_to_gyroscope_view_command():
        toggle_indicator(indicators["Change to \n Gyroscope View"], 'green' if indicators['Change to \n Gyroscope View'].cget("bg") == 'red' else 'red')
        print("Change to Gyroscope View")

    # Define button texts and associated commands in a list of tuples
    buttons_info = [
        ("On/Off", on_off_command),
        ("Solar Panel \n Deployment", solar_panel_deployment_command),
        ("Receiving telemetry data", receive_telemetry_data_command),
        ("Change to \n Camera View", change_to_camera_view_command),
        ("Change to \n Gyroscope View", change_to_gyroscope_view_command)
    ]

    # Create and pack buttons and indicators into the frame
    for text, command in buttons_info:
        # Create a frame to hold the button and indicator
        button_indicator_frame = tk.Frame(button_frame, bg='black')
        button_indicator_frame.pack(side="left", padx=5, pady=65, expand=True)

        # Create the button
        button = tk.Button(button_indicator_frame, text=text, command=command, bg="#211f1d", fg="white", font=("Arial", 10), width=button_width, height=button_height)
        button.pack(side="left")

        # Create the indicator canvas
        indicator = tk.Canvas(button_indicator_frame, width=20, height=92, bg='red', highlightthickness=0)
        indicator.pack(side="left", padx=0, pady=10)

        # Store the indicator canvas in the dictionary
        indicators[text] = indicator

    return button_frame

def configure_main_window(window):
    window.title('DSPS Mission Control')
    window.geometry('960x540')
    window.resizable(False, False)
    window.configure(bg="#2b0057")


def main():
    global window  # Remove the global declaration for left_panel_width
    window = tk.Tk()
    configure_main_window(window)

    create_top_bar(window)

    # Assign the desired widths for the left and right panels
    left_panel_width = 480  # Specify the desired width for the left panel
    right_panel_width = 480  # Specify the desired width for the right panel

    create_left_panel(window, left_panel_width)
    create_right_panel(window, right_panel_width)
    create_bottom_panel(window)

    window.mainloop()


if __name__ == "__main__":
    main()


