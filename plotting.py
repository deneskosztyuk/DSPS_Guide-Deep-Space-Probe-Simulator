import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.gridspec as gridspec
import math

class PlottingService:
    def __init__(self, parent, width):
        self.frame = tk.Frame(parent, bg='black', width=width, height=300)
        self.frame.grid_propagate(False)

        self.fig = Figure(figsize=(6, 3))
        gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])

        self.axes = {
            "Temperature (°C)": self.fig.add_subplot(gs[0, :]),
            "Humidity (%)": self.fig.add_subplot(gs[1, 0]),
            "Altitude (m)": self.fig.add_subplot(gs[1, 1])
        }

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def get_frame(self):
        return self.frame

    def update_plots(self, model):
        self.update_graph(self.axes["Temperature (°C)"], model.get_data('temperature'), "Temperature (°C)")
        self.update_graph(self.axes["Humidity (%)"], model.get_data('humidity'), "Humidity (%)")
        self.update_graph(self.axes["Altitude (m)"], model.get_data('altitude'), "Altitude (m)")
        self.canvas.draw()

    def update_graph(self, ax, data, label):
        ax.clear()
        ax.plot(data, label=label)
        ax.set_title(label)
        ax.legend(loc='upper left')
