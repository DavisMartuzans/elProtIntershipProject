import pandas as pd
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class InteractiveBOMApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Interactive BoM and Assembly Guide")

        # Load BoM data (replace 'your_bom.csv' with your actual file)
        self.bom_data = pd.read_csv('your_bom.csv')

        # Create GUI elements
        self.bom_listbox = tk.Listbox(master)
        self.bom_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        self.assembly_frame = tk.Frame(master)
        self.assembly_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.load_bom()
        self.show_assembly_guide()

        # Bind events
        self.bom_listbox.bind('<<ListboxSelect>>', self.show_assembly_guide)

    def load_bom(self):
        # Populate BoM listbox with product names
        for index, row in self.bom_data.iterrows():
            self.bom_listbox.insert(tk.END, row['Product'])

    def show_assembly_guide(self, event=None):
        # Clear previous assembly guide
        for widget in self.assembly_frame.winfo_children():
            widget.destroy()

        # Get selected product
        selected_index = self.bom_listbox.curselection()
        if not selected_index:
            return

        selected_product = self.bom_data.iloc[selected_index[0]]

        # Display assembly information
        assembly_label = tk.Label(self.assembly_frame, text=f"Assembly Guide for {selected_product['Product']}")
        assembly_label.pack()

        # Load and display assembly image (replace 'your_image.jpg' with your actual image)
        image_path = 'your_image.jpg'
        image = Image.open(image_path)
        image = ImageTk.PhotoImage(image)
        image_label = tk.Label(self.assembly_frame, image=image)
        image_label.image = image
        image_label.pack()

        # Add more details as needed

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveBOMApp(root)
    root.mainloop()
