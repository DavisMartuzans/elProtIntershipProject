import tkinter as tk
from frontend import PCBToolFrontend
import csv

class PCBTool(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PCB Component Highlighter")
        self.geometry("1000x600")

        self.components = []
        self.load_files()

        self.frontend = PCBToolFrontend(self.load_files, self.refresh_canvas)
        self.frontend.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
 
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.original_image = Image.open(self.pcb_image_path)
        self.tk_image = ImageTk.PhotoImage(self.original_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="image")

        self.pcb_width, self.pcb_height = self.original_image.size

    def load_files(self):
        pnp_file_path = tk.filedialog.askopenfilename(title="Select Pick-and-Place File", filetypes=[("CSV Files", "*.csv")])
        self.pcb_image_path = tk.filedialog.askopenfilename(title="Select PCB Image", filetypes=[("Image Files", "*.png"), ("Image Files", "*.jpg")])

        with open(pnp_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.components.append({
                    'name': row['Designator'],
                    'Footprint': row['Footprint'],
                    'Center-X(mm)': float(row['Center-X(mm)']),
                    'Center-Y(mm)': float(row['Center-Y(mm)']),
                    'Rotation': float(row['Rotation'])
                })

        self.frontend.populate_listbox(self.components)

    def apply_transformations(self, x, y):
        # Apply scaling first
        x_scaled = x * self.frontend.scale_x.get()
        y_scaled = y * self.frontend.scale_y.get()

        # Apply offset
        x_offset = x_scaled + self.frontend.offset_x.get()
        y_offset = y_scaled + self.frontend.offset_y.get()

        # Then apply mirroring transformations if selected
        if self.frontend.mirror_horizontal.get() == 1:
            x_mirror = self.pcb_width - x_offset
        else:
            x_mirror = x_offset

        if self.frontend.mirror_vertical.get() == 1:
            y_mirror = self.pcb_height - y_offset
        else:
            y_mirror = y_offset

        return x_mirror, y_mirror

    def refresh_canvas(self):
        self.canvas.delete("highlight")

        if not self.frontend.listbox.curselection():
            return
        index = int(self.frontend.listbox.curselection()[0])
        component = self.components[index]

        x, y = self.apply_transformations(component['Center-X(mm)'], component['Center-Y(mm)'])

        # Draw highlight
        self.canvas.create_oval(x-10, y-10, x+10, y+10, outline="red", width=2, tags="highlight")

if __name__ == "__main__":
    app = PCBTool()
    app.mainloop()
