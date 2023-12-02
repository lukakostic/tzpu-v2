import tkinter as tk


class DisplayLog:
    TEXT_HEIGHT = 24

    def __init__(self, canvas, x_top, y_top):
        self.canvas = canvas
        self.x_top = x_top
        self.y_top = y_top
        self.count = 0

    def next_arrival(self, minutes):
        x = self.x_top
        y = self.y_top + (self.count * self.TEXT_HEIGHT)
        self.canvas.create_text(x, y, anchor=tk.NW, text=f"Next login in {round(minutes, 1)} minutes")
        # self.count = self.count + 1
        self.canvas.update()

    def arrived(self, people):
        x = self.x_top + 165
        y = self.y_top + (self.count * self.TEXT_HEIGHT)
        self.canvas.create_text(x, y, anchor=tk.NW, text=f"{people} users attempted login", fill="green")
        self.count = self.count + 1
        self.canvas.update()
