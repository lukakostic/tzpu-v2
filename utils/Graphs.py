import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
#from turtledemo.chaos import f

def f(x):
    return 3.9*x*(1-x)

class Graphs:
    def __init__(self, canvas, main, utilization, wait_for_resource, arrivals):
        self.x1, self.y1, self.x2, self.y2 = 1000, 260, 1290, 340
        self.time = 0
        self.canvas = canvas

        self.utilization = utilization
        self.wait_for_resource = wait_for_resource
        self.arrivals = arrivals

        self.train = canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill="#fff")

        self.time = self.create_text_canvas_minutes("Time = " + str(round(self.time, 1)), 10, 10)
        self.avg_utilization = self.create_text_canvas(
            "Avg. utilization  = " + str(self.avg_wait(self.utilization)) + "%", 10, 30)
        self.avg_resource_wait = self.create_text_canvas_minutes(
            "Avg. wait for resource = " + str(self.avg_wait(self.wait_for_resource)), 10, 50)

        self.figure = plt.Figure(figsize=(2, 2), dpi=72)

        self.data_plot = FigureCanvasTkAgg(self.figure, master=main)
        self.data_plot.get_tk_widget().config(height=400)
        self.data_plot.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.a3 = self.figure.add_subplot(121)
        self.a3.plot()
        self.a1 = self.figure.add_subplot(222)
        self.a1.plot()
        self.a2 = self.figure.add_subplot(224)
        self.a2.plot()
        self.canvas.update()

    @staticmethod
    def avg_wait(raw_waits):
        waits = [w for i in raw_waits.values() for w in i]
        return round(np.mean(waits), 1) if len(waits) > 0 else 0

    def create_text_canvas_minutes(self, text, offset_x, offset_y):
        return self.canvas.create_text(self.x1 + offset_x, self.y1 + offset_y, text=text + "m", anchor=tk.NW)

    def create_text_canvas(self, text, offset_x, offset_y):
        return self.canvas.create_text(self.x1 + offset_x, self.y1 + offset_y, text=text, anchor=tk.NW)

    def tick(self, time):
        self.canvas.delete(self.time)
        self.canvas.delete(self.avg_utilization)
        self.canvas.delete(self.avg_resource_wait)

        self.time = self.create_text_canvas_minutes("Time = " + str(round(time, 1)), 10, 10)
        self.avg_utilization = self.create_text_canvas(
            "Avg. utilization  = " + str(self.avg_wait(self.utilization)) + "%", 10, 30)
        self.avg_resource_wait = self.create_text_canvas_minutes(
            "Avg. wait for resource = " + str(self.avg_wait(self.wait_for_resource)), 10, 50)

        self.a1.cla()
        self.a1.set_xlabel("Time")
        self.a1.set_ylabel("System utilization")
        self.a1.step([t for (t, waits) in self.utilization.items()],
                     [np.mean(waits) for (t, waits) in self.utilization.items()])

        self.a2.cla()
        self.a2.set_xlabel("Time")
        self.a2.set_ylabel("Avg. wait for resource (min)")
        self.a2.step([t for (t, waits) in self.wait_for_resource.items()],
                     [np.mean(waits) for (t, waits) in self.wait_for_resource.items()])

        self.a3.cla()
        self.a3.set_xlabel("Time")
        self.a3.set_ylabel("Arrivals")
        self.a3.bar([t for (t, a) in self.arrivals.items()], [a for (t, a) in self.arrivals.items()])

        self.data_plot.draw()
        self.canvas.update()
