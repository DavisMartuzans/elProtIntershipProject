import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, Checkbutton, IntVar
from PIL import Image, ImageTk
import csv

class PCBTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PCB Component Highlighter")
        self.geometry("1000x600")

        self.components = []
        self.load_files()

        self.scale_x = tk.DoubleVar(value=1.0)
        self.scale_y = tk.DoubleVar(value=1.0)
        self.offset_x = tk.DoubleVar(value=0.0)
        self.offset_y = tk.DoubleVar(value=0.0)
        self.rotation_angle = tk.DoubleVar(value=0.0)
        self.mirror_horizontal = IntVar(value=0)
        self.mirror_vertical = IntVar(value=0)

        control_panel = tk.Frame(self, padx=10, pady=10)
        control_panel.pack(side=tk.LEFT, fill=tk.Y)


        scale_frame = tk.Frame(control_panel, padx=5, pady=5)
        scale_frame.pack(fill=tk.X)
        Label(scale_frame, text="Scale X:", font=("Arial", 12)).pack()
        Entry(scale_frame, textvariable=self.scale_x).pack()
        Label(scale_frame, text="Scale Y:", font=("Arial", 12)).pack()
        Entry(scale_frame, textvariable=self.scale_y).pack()

        offset_frame = tk.Frame(control_panel, padx=5, pady=5)
        offset_frame.pack(fill=tk.X)
        Label(offset_frame, text="Offset X:", font=("Arial", 12)).pack()
        Entry(offset_frame, textvariable=self.offset_x).pack()
        Label(offset_frame, text="Offset Y:", font=("Arial", 12)).pack()
        Entry(offset_frame, textvariable=self.offset_y).pack()

        rotation_frame = tk.Frame(control_panel, padx=5, pady=5)
        rotation_frame.pack(fill=tk.X)
        Label(rotation_frame, text="Rotation Angle:", font=("Arial", 12)).pack()
        Entry(rotation_frame, textvariable=self.rotation_angle).pack()

        mirror_frame = tk.Frame(control_panel, padx=5, pady=5)
        mirror_frame.pack(fill=tk.X)
        Checkbutton(mirror_frame, text="Mirror Horizontal", variable=self.mirror_horizontal, font=("Arial", 12)).pack()
        Checkbutton(mirror_frame, text="Mirror Vertical", variable=self.mirror_vertical, font=("Arial", 12)).pack()

        Button(control_panel, text="Apply", command=self.refresh_canvas, font=("Arial", 12), bg="light blue").pack()

        self.listbox = tk.Listbox(control_panel, width=50)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        for component in self.components:
            listbox_entry = f"{component['name']} - X: {component['x']}, Y: {component['y']}"
            if 'footprint' in component:
                listbox_entry += f", Footprint: {component['footprint']}"
            self.listbox.insert(tk.END, listbox_entry)

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.original_image = Image.open(self.pcb_image_path)
        self.tk_image = ImageTk.PhotoImage(self.original_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="image")

        self.pcb_width, self.pcb_height = self.original_image.size

    def load_files(self):
        pnp_file_path = filedialog.askopenfilename(title="Select Pick-and-Place File", filetypes=[("CSV Files", "*.csv")])
        self.pcb_image_path = filedialog.askopenfilename(title="Select PCB Image", filetypes=[("Image Files", "*.png"), ("Image Files", "*.jpg")])

        with open(pnp_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.components.append({
                    'name': row['Designator'],
                    'x': float(row['Center-X(mm)']),
                    'y': float(row['Center-Y(mm)']),
                    'rotation': float(row['Rotation'])
                })

    def on_select(self, event):
        self.refresh_canvas()

    def apply_transformations(self, x, y):
        # Apply scaling first
        x_scaled = x * self.scale_x.get()
        y_scaled = y * self.scale_y.get()

        # Apply offset
        x_offset = x_scaled + self.offset_x.get()
        y_offset = y_scaled + self.offset_y.get()

        # Then apply mirroring transformations if selected
        if self.mirror_horizontal.get() == 1:
            x_mirror = self.pcb_width - x_offset
        else:
            x_mirror = x_offset

        if self.mirror_vertical.get() == 1:
            y_mirror = self.pcb_height - y_offset
        else:
            y_mirror = y_offset

        return x_mirror, y_mirror

    def refresh_canvas(self):
        self.canvas.delete("highlight")

        if not self.listbox.curselection():
            return
        index = int(self.listbox.curselection()[0])
        component = self.components[index]

        x, y = self.apply_transformations(component['x'], component['y'])

        # Draw highlight
        self.canvas.create_oval(x-10, y-10, x+10, y+10, outline="red", width=2, tags="highlight")

        def move_canvas(self):
            new_window = Toplevel(self)
            new_window.title("Canvas Window")
            self.canvas.pack_forget()
            self.canvas.pack(in_=new_window, side=tk.RIGHT, fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = PCBTool()
    app.mainloop()