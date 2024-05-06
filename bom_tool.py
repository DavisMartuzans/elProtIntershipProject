import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, Checkbutton, IntVar, Listbox, ttk, Toplevel
from PIL import Image, ImageTk
import csv

class PCBTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PCB Component Highlighter")
        self.geometry("1200x600")

        # Saraksts,kas saglabātu komponentu datus, kas tiek ielādēti no failiem
        self.components = []
        
        # Marker iestatījumu mainīgie
        self.marker_color = tk.StringVar(value="red")  # Default marker color
        self.marker_size = tk.DoubleVar(value=10.0)    # Default marker size
        self.marker_shape = tk.StringVar(value="oval")# Default marker shape
        
        # Atver failu datus un iestata sākotnējo GUI(Vadības panelis)
        self.load_files()
        self.setup_gui()

    def load_files(self):
        # Pieprasa izvēlēties failu ar komponentu datiem un attēlu
        pnp_file_path = filedialog.askopenfilename(title="Select Pick-and-Place File", filetypes=[("CSV Files", "*.csv")])
        self.pcb_image_path = filedialog.askopenfilename(title="Select PCB Image", filetypes=[("Image Files", "*.png"), ("Image Files", "*.jpg")])

        # Lasa datus no Pick-and-Place faila (CSV) un saglabājiet tos self.components sarakstā
        with open(pnp_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.components.append({
                    'name': row['Designator'],
                    'x': float(row['Center-X(mm)']),
                    'y': float(row['Center-Y(mm)']),
                    'rotation': float(row['Rotation']),
                    'layer': row['Layer'],
                    'footprint': row['Footprint'],
                    'manufacture_part_number': row['Manufacture Part Number 1'],
                    'supplier_part_number': row['Supplier Part Number 1']
                })

    def setup_gui(self):
        # Inicializē mainīgos mērogošanas, nobīdes, pagriešanas un spoguļošanas
        self.scale_x = tk.DoubleVar(value=1.0)
        self.scale_y = tk.DoubleVar(value=1.0)
        self.offset_x = tk.DoubleVar(value=0.0)
        self.offset_y = tk.DoubleVar(value=0.0)
        self.rotation_angle = tk.DoubleVar(value=0.0)
        self.mirror_horizontal = IntVar(value=0)
        self.mirror_vertical = IntVar(value=0)

        # Izveido vadības paneļa rāmi
        control_panel = tk.Frame(self, padx=10, pady=10)
        control_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mērogošanas kontroles
        scale_frame = tk.Frame(control_panel, padx=5, pady=5)
        scale_frame.pack(fill=tk.X)
        Label(scale_frame, text="Scaling", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        Label(scale_frame, text="Scale X:", font=("Arial", 12)).pack(anchor=tk.W)
        Entry(scale_frame, textvariable=self.scale_x).pack(anchor=tk.W)
        Label(scale_frame, text="Scale Y:", font=("Arial", 12)).pack(anchor=tk.W)
        Entry(scale_frame, textvariable=self.scale_y).pack(anchor=tk.W)

        # Nobīdes kontroles
        offset_frame = tk.Frame(control_panel, padx=5, pady=5)
        offset_frame.pack(fill=tk.X)
        Label(offset_frame, text="Offset", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        Label(offset_frame, text="Offset X:", font=("Arial", 12)).pack(anchor=tk.W)
        Entry(offset_frame, textvariable=self.offset_x).pack(anchor=tk.W)
        Label(offset_frame, text="Offset Y:", font=("Arial", 12)).pack(anchor=tk.W)

        # Rotācijas kontroles
        rotation_frame = tk.Frame(control_panel, padx=5, pady=5)
        rotation_frame.pack(fill=tk.X)
        Label(rotation_frame, text="Rotation", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        Label(rotation_frame, text="Rotation Angle:", font=("Arial", 12)).pack(anchor=tk.W)
        Entry(rotation_frame, textvariable=self.rotation_angle).pack(anchor=tk.W)

        # Spoguļošanas kontroles
        mirror_frame = tk.Frame(control_panel, padx=5, pady=5)
        mirror_frame.pack(fill=tk.X)
        Label(mirror_frame, text="Mirroring", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        Checkbutton(mirror_frame, text="Mirror Horizontal", variable=self.mirror_horizontal, font=("Arial", 12)).pack(anchor=tk.W)
        Checkbutton(mirror_frame, text="Mirror Vertical", variable=self.mirror_vertical, font=("Arial", 12)).pack(anchor=tk.W)

        # Marķiera iestatījumu kontroles
        marker_frame = tk.Frame(control_panel, padx=5, pady=5)
        marker_frame.pack(fill=tk.X)
        Label(marker_frame, text="Marker Settings", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        Label(marker_frame, text="Marker Color:", font=("Arial", 12)).pack(anchor=tk.W)
        Entry(marker_frame, textvariable=self.marker_color).pack(anchor=tk.W)
        Label(marker_frame, text="Marker Size:", font=("Arial", 12)).pack(anchor=tk.W)
        Entry(marker_frame, textvariable=self.marker_size).pack(anchor=tk.W)
        Label(marker_frame, text="Marker Shape:", font=("Arial", 12)).pack(anchor=tk.W)
        ttk.Combobox(marker_frame, textvariable=self.marker_shape, values=["oval", "square", "square with dot"], state="readonly").pack(anchor=tk.W)

        # Apply and Export Pogas
        Button(control_panel, text="Apply", command=self.refresh_canvas, font=("Arial", 12), bg="light blue").pack(anchor=tk.W)
        Button(control_panel, text="Export", command=self.export_spreadsheet, font=("Arial", 12), bg="light green").pack(anchor=tk.W)

        # Pārslēgšanās poga, lai pārslēgtos starp canvas izmantošanu tajā pašā logā un citā logā
        self.toggle_canvas_button = Button(control_panel, text="Toggle Canvas", command=self.toggle_canvas, font=("Arial", 12), bg="orange")
        self.toggle_canvas_button.pack(anchor=tk.W)

        # Treeview logrīks lai parādītu komponentu datus
        self.treeview = ttk.Treeview(control_panel)
        self.treeview["columns"] = ("Name", "X", "Y", "Rotation", "Layer", "Footprint", "Manufacture Part Number", "Supplier Part Number")
        self.treeview.heading("#0", text="", anchor=tk.W)
        self.treeview.heading("Name", text="Name")
        self.treeview.heading("X", text="X")
        self.treeview.heading("Y", text="Y")
        self.treeview.heading("Rotation", text="Rotation")
        self.treeview.heading("Layer", text="Layer")
        self.treeview.heading("Footprint", text="Footprint")
        self.treeview.heading("Manufacture Part Number", text="Manufacture Part Number")
        self.treeview.heading("Supplier Part Number", text="Supplier Part Number")
        self.treeview.column("#0", width=0, stretch=tk.NO)
        self.treeview.column("Name", width=100)
        self.treeview.column("X", width=50)
        self.treeview.column("Y", width=50)
        self.treeview.column("Rotation", width=70)
        self.treeview.column("Layer", width=100)
        self.treeview.column("Footprint", width=150)
        self.treeview.column("Manufacture Part Number", width=150)
        self.treeview.column("Supplier Part Number", width=150)
        self.treeview.pack(fill=tk.BOTH, expand=True)
        self.treeview.bind("<ButtonRelease-1>", self.on_treeview_click)

        # Ievieto komponentu datus Treeview
        for component in self.components:
            self.treeview.insert("", "end", values=(component["name"], component["x"], component["y"], component["rotation"], component.get("layer", ""), component.get("footprint", ""), component.get("manufacture_part_number", ""), component.get("supplier_part_number", "")))

        # Canvas lai parādītu PCB attēlu un komponentu highlights
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.original_image = Image.open(self.pcb_image_path)
        self.tk_image = ImageTk.PhotoImage(self.original_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="image")
        self.pcb_width, self.pcb_height = self.original_image.size

        # Atzīmē, lai izsekotu kanvas atrašanās vietu
        self.canvas_in_window = False
        self.canvas_window = None

    def toggle_canvas(self):
        if self.canvas_in_window:
            # Store the geometry of the current window
            geometry = self.canvas_window.geometry()
            self.canvas_window.destroy()
            
            # Re-create the canvas in the original parent window
            self.canvas = tk.Canvas(self.original_parent, bg='white')  
            self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self.tk_image = ImageTk.PhotoImage(self.original_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="image")
            self.canvas_window = None  # Reset the canvas window reference
            self.canvas_in_window = False
            self.toggle_canvas_button.config(text="Toggle Canvas (In Separate Window)")
        else:
            # Store the original parent window
            self.original_parent = self.winfo_toplevel()
            
            # Create a new window for the canvas
            self.canvas_window = Toplevel(self)
            self.canvas_window.title("PCB Canvas")
            self.canvas_window.attributes("-topmost", True)
            self.canvas_frame = tk.Frame(self.canvas_window, padx=10, pady=10)
            self.canvas_frame.pack(fill=tk.BOTH, expand=True)
            self.canvas = tk.Canvas(self.canvas_frame, bg='white')
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.tk_image = ImageTk.PhotoImage(self.original_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="image")
            self.pcb_width, self.pcb_height = self.original_image.size
            self.canvas.bind("<Button-1>", self.scale_to_image)
            self.toggle_canvas_button.config(text="Toggle Canvas (In Window)")
            self.canvas_in_window = True

    def scale_to_image(self, event):
        # Funkcija loga mērogošanai, lai tas atbilstu attēla izmēram, noklikšķinot
        self.canvas_window.geometry("{}x{}".format(self.pcb_width, self.pcb_height))

    def on_treeview_click(self, event):
        # Funkcija, lai apstrādātu klikšķu notikumus Treeview
        item = self.treeview.selection()[0]
        index = self.treeview.index(item)
        component = self.components[index]
        self.refresh_canvas(component)

    def refresh_canvas(self, component=None):
        # Funkcija displeja atsvaidzināšanai, pamatojoties uz atlasīto komponentu
        self.canvas.delete("highlight")
        if component:
            x, y = self.apply_transformations(component['x'], component['y'])
            # Zīmē marķieri uz attēla
            marker_color = self.marker_color.get()
            marker_size = self.marker_size.get()
            marker_shape = self.marker_shape.get()
            if marker_shape == "oval":
                self.canvas.create_oval(x - marker_size, y - marker_size, x + marker_size, y + marker_size, outline=marker_color, width=2, tags="highlight")
            elif marker_shape == "square":
                self.canvas.create_rectangle(x - marker_size, y - marker_size, x + marker_size, y + marker_size, outline=marker_color, width=2, tags="highlight")
            elif marker_shape == "square with dot":
                self.canvas.create_rectangle(x - marker_size, y - marker_size, x + marker_size, y + marker_size, outline=marker_color, width=2, tags="highlight")
                self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=marker_color, outline=marker_color, tags="highlight")
                self.canvas.create_line(x - marker_size, y - marker_size, x - marker_size, y + marker_size, fill=marker_color, tags="highlight")
            # Šeit var pievienot citus marķiera veidus, ja ir vajadzība

    def apply_transformations(self, x, y):
        # Funkcija mērogošanas, nobīdes, pagriešanas un spoguļošanas transformāciju pielietošanai
        x_scaled = x * self.scale_x.get()
        y_scaled = y * self.scale_y.get()
        x_offset = x_scaled + self.offset_x.get()
        y_offset = y_scaled + self.offset_y.get()
        if self.mirror_horizontal.get() == 1:
            x_mirror = self.pcb_width - x_offset
        else:
            x_mirror = x_offset
        if self.mirror_vertical.get() == 1:
            y_mirror = self.pcb_height - y_offset
        else:
            y_mirror = y_offset
        return x_mirror, y_mirror

    def export_spreadsheet(self):
        # Funkcija komponentu datu eksportēšanai uz izklājlapu
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if filename:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Designator', 'Center-X(mm)', 'Center-Y(mm)', 'Rotation', 'Layer', 'Footprint', 'Manufacture Part Number 1', 'Supplier Part Number 1']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for component in self.components:
                    writer.writerow({
                        'Designator': component['name'],
                        'Center-X(mm)': component['x'],
                        'Center-Y(mm)': component['y'],
                        'Rotation': component['rotation'],
                        'Layer': component.get('layer', ''),
                        'Footprint': component.get('footprint', ''),
                        'Manufacture Part Number 1': component.get('manufacture_part_number', ''),
                        'Supplier Part Number 1': component.get('supplier_part_number', '')
                    })

if __name__ == "__main__":
    app = PCBTool()
    app.mainloop()
