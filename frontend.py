import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, Checkbutton, IntVar
from PIL import Image, ImageTk

class PCBToolFrontend(tk.Tk):
    def __init__(self, load_files_callback, refresh_canvas_callback):
        super().__init__()
        self.title("PCB Component Highlighter")
        self.geometry("1000x600")

        self.load_files_callback = load_files_callback
        self.refresh_canvas_callback = refresh_canvas_callback

        self.scale_x = tk.DoubleVar(value=1.0)
        self.scale_y = tk.DoubleVar(value=1.0)
        self.offset_x = tk.DoubleVar(value=0.0)
        self.offset_y = tk.DoubleVar(value=0.0)
        self.rotation_angle = tk.DoubleVar(value=0.0)
        self.mirror_horizontal = IntVar(value=0)
        self.mirror_vertical = IntVar(value=0)

        control_panel = tk.Frame(self)
        control_panel.pack(side=tk.LEFT, fill=tk.Y)
        Label(control_panel, text="Scale X:").pack()
        Entry(control_panel, textvariable=self.scale_x).pack()
        Label(control_panel, text="Scale Y:").pack()
        Entry(control_panel, textvariable=self.scale_y).pack()
        Label(control_panel, text="Offset X:").pack()
        Entry(control_panel, textvariable=self.offset_x).pack()
        Label(control_panel, text="Offset Y:").pack()
        Entry(control_panel, textvariable=self.offset_y).pack()
        Label(control_panel, text="Rotation Angle:").pack()
        Entry(control_panel, textvariable=self.rotation_angle).pack()
        Checkbutton(control_panel, text="Mirror Horizontal", variable=self.mirror_horizontal).pack()
        Checkbutton(control_panel, text="Mirror Vertical", variable=self.mirror_vertical).pack()
        Button(control_panel, text="Apply", command=self.refresh_canvas_callback).pack()

        self.listbox = tk.Listbox(control_panel)
        self.listbox.pack(fill=tk.BOTH, expand=True)

    def populate_listbox(self, components):
        self.listbox.delete(0, tk.END)
        for component in components:
            self.listbox.insert(tk.END, f"{component['name']} - {component['Footprint']} - ({component['Center-X(mm)']}, {component['Center-Y(mm)']}) - Rotation: {component['Rotation']}")


if __name__ == "__main__":
    app = PCBToolFrontend(None, None)  # Pass None as placeholders
    app.mainloop()
