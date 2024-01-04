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
    bottom_frame = tk.Frame(parent, bg='black', width=960, height=290)
    bottom_frame.place(x=0, y=320)
    label = tk.Label(bottom_frame, text="Control Commands", bg='#211f1d', fg='white', font=("Arial", 14))
    bottom_frame.pack_propagate(False)
    label.pack()

    return bottom_frame

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
