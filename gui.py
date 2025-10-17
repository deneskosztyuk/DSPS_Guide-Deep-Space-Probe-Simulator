import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime

from model import DataModel
from plotting import PlottingService
from api import DSPS_API

class MainApp:
    def __init__(self, master):
        self.master = master
        self.model = DataModel()
        self.api = DSPS_API(self.on_data_received)
        
        self.master.title('DSPS Mission Control')
        self.master.configure(bg="#2b0057")

        self.setup_gui()
        self.start_api()
        self.update_time_label()

    def setup_gui(self):
        self.create_top_bar()
        
        self.plotting_service = PlottingService(self.master, width=480)
        self.plotting_service.get_frame().grid(row=1, column=0, sticky="nsew")

        self.create_right_panel(480).grid(row=1, column=1, sticky="nsew")
        self.create_bottom_left_panel().grid(row=2, column=0, sticky="nsew")
        self.create_bottom_right_panel().grid(row=2, column=1, sticky="nsew")

        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

    def start_api(self):
        flask_thread = threading.Thread(target=self.api.run, daemon=True)
        flask_thread.start()

    def on_data_received(self, data):
        self.model.update_data(data)
        self.plotting_service.update_plots(self.model)
        self.update_telemetry_labels()

    def create_top_bar(self):
        top_bar = tk.Frame(self.master, bg="black", height=50)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        label = tk.Label(top_bar, text="DSPS Control Software", bg="#211f1d", fg="white", anchor="w", font=("Arial", 14))
        label.pack(padx=10)

    def create_right_panel(self, width):
        right_frame = tk.Frame(self.master, bg='black', width=width, height=290)
        right_frame.pack_propagate(False)

        labels_frame = tk.Frame(right_frame, bg='black')
        labels_frame.pack(side="left", fill="both", expand=True)

        self.temp_label = self.create_label(labels_frame, "Temperature: -- °C")
        self.hum_label = self.create_label(labels_frame, "Humidity: -- %")
        self.pres_label = self.create_label(labels_frame, "Pressure: -- hPa")
        self.alt_label = self.create_label(labels_frame, "Approx Altitude: -- m")
        self.time_label = self.create_label(labels_frame, "Date & Time: --")
        self.conn_label = self.create_label(labels_frame, "Connection Status: Disconnected", 'red')
        
        return right_frame

    def create_label(self, parent, text, fg='green'):
        label = tk.Label(parent, text=text, bg='black', fg=fg, font=("Arial", 14))
        label.pack(anchor="w")
        return label

    def create_bottom_left_panel(self):
        bottom_left_frame = tk.Frame(self.master, bg='black')
        buttons_frame = tk.Frame(bottom_left_frame, bg='black')
        buttons_frame.pack(expand=True)
        
        self.on_off_button = tk.Button(buttons_frame, text="Telemetry ON/OFF", command=self.toggle_connection, bg='red')
        self.on_off_button.grid(row=0, column=0, padx=5, pady=5)
        
        reset_button = tk.Button(buttons_frame, text="Reset Device", command=self.api.send_reset)
        reset_button.grid(row=0, column=1, padx=5, pady=5)

        exit_button = tk.Button(buttons_frame, text="Exit", command=self.master.quit, bg='darkred', fg='white')
        exit_button.grid(row=0, column=2, padx=5, pady=5)

        return bottom_left_frame
    
    def create_bottom_right_panel(self):
        bottom_right_frame = tk.Frame(self.master, bg='black')
        self.chat_box = tk.Text(bottom_right_frame, height=8, state='disabled', bg='#1c1c1c', fg='white')
        self.chat_box.pack(fill='both', expand=True, padx=5, pady=5)
        return bottom_right_frame

    def toggle_connection(self):
        self.model.toggle_connection()
        status = "Connected" if self.model.is_connected else "Disconnected"
        color = "green" if self.model.is_connected else "red"
        self.on_off_button.config(bg=color)
        self.conn_label.config(text=f"Connection Status: {status}", fg=color)
        self.log_message(f"Connection toggled: {status}")
        if not self.model.is_connected:
            self.reset_telemetry_labels()

    def update_telemetry_labels(self):
        if self.model.is_connected:
            self.temp_label.config(text=f"Temperature: {self.model.get_latest('temperature'):.2f} °C")
            self.hum_label.config(text=f"Humidity: {self.model.get_latest('humidity'):.2f} %")
            self.pres_label.config(text=f"Pressure: {self.model.get_latest('pressure'):.2f} hPa")
            self.alt_label.config(text=f"Altitude: {self.model.get_latest('altitude'):.2f} m")

    def reset_telemetry_labels(self):
        self.temp_label.config(text="Temperature: -- °C")
        self.hum_label.config(text="Humidity: -- %")
        self.pres_label.config(text="Pressure: -- hPa")
        self.alt_label.config(text="Approx Altitude: -- m")

    def update_time_label(self):
        if self.model.is_connected:
            self.time_label.config(text=f"Date & Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        else:
            self.time_label.config(text="Date & Time: --")
        self.master.after(1000, self.update_time_label)

    def log_message(self, message):
        self.chat_box.config(state='normal')
        self.chat_box.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}: {message}\\n")
        self.chat_box.see(tk.END)
        self.chat_box.config(state='disabled')
