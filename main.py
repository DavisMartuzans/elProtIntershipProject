import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, Checkbutton, IntVar, messagebox
from PIL import Image, ImageTk
import csv

class PCBTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("elProt Ibom")
        self.geometry("1920x1080")

        self.components = []
        self.load_files()

        self.scale_x = tk.DoubleVar(value=1.0)
        self.scale_y = tk.DoubleVar(value=1.0)
        self.offset_x = tk.DoubleVar(value=0.0)
        self.offset_y = tk.DoubleVar(value=0.0)
        self.rotation_angle = tk.DoubleVar(value=0.0)
        self.mirror_horizontal = IntVar(value=0)
        self.mirror_vertical = IntVar(value=0)

        control_panel = tk.Frame(self, width=self.winfo_screenwidth())  # Adjusting the width here
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
        Button(control_panel, text="Apply", command=self.refresh_canvas).pack()

        self.save_button = tk.Button(self)
        self.save_button["text"] = "Save Image"
        self.save_button["command"] = self.save_image
        self.save_button.pack(side="top")

        self.listbox = tk.Listbox(control_panel)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        for component in self.components:
            self.listbox.insert(tk.END, component['name'])

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.original_image = Image.open(self.pcb_image_path)
        self.tk_image = ImageTk.PhotoImage(self.original_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="image")

        self.pcb_width, self.pcb_height = self.original_image.size

        self.new_window = None
        self.toggle_button = tk.Button(self)
        self.toggle_button["text"] = "Toggle Image Window"
        self.toggle_button["command"] = self.toggle_image_window
        self.toggle_button.pack(side="top")

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

    def toggle_image_window(self):
        if self.new_window is None:
            self.new_window = tk.Toplevel(self.master)
            self.new_canvas = tk.Canvas(self.new_window, width=800, height=600)
            self.new_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self.new_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="image")
            self.canvas.delete("image")
        else:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="image")
            self.new_canvas.delete("image")
            self.new_window.destroy()
            self.new_window = None

    def save_image(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])
        if save_path:
            try:
                self.original_image.save(save_path)
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    app = PCBTool()
    app.mainloop()