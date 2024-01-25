import tkinter as tk
from tkinter import filedialog
import pandas as pd

class FileSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("elProt Ibom")

        # Create variables to store file paths
        self.csv_file_path = tk.StringVar()
        self.png_file_path = tk.StringVar()

        # Create labels
        tk.Label(root, text="Select CSV File:").pack(pady=5)
        tk.Label(root, text="Select PNG File:").pack(pady=5)

        # Create entry widgets to display file paths
        tk.Entry(root, textvariable=self.csv_file_path, state='readonly').pack(pady=5)
        tk.Entry(root, textvariable=self.png_file_path, state='readonly').pack(pady=5)

        # Create buttons to open file dialogs
        tk.Button(root, text="Browse CSV", command=self.browse_csv).pack(pady=5)
        tk.Button(root, text="Browse PNG", command=self.browse_png).pack(pady=5)

        # Create a button to proceed to the next step
        tk.Button(root, text="Next", command=self.process_files).pack(pady=10)

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.csv_file_path.set(file_path)

    def browse_png(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        self.png_file_path.set(file_path)

    def read_csv_with_warnings(self, csv_path):
        try:
            bom_data = pd.read_csv(csv_path)
        except pd.errors.ParserError as e:
            tk.messagebox.showwarning("Warning", f"Error reading CSV: {e}")
            bom_data = pd.DataFrame()  # or None, depending on your use case
        return bom_data

    def process_files(self):
        # Get the selected file paths
        csv_path = self.csv_file_path.get()
        png_path = self.png_file_path.get()

        # Check if both files are selected
        if csv_path and png_path:
            # Read BOM data from CSV using a custom function
            bom_data = self.read_csv_with_warnings(csv_path)

            # Display BOM data (you can customize this part)
            print("BOM Data:")
            print(bom_data)

            # Perform your desired operations with BOM data and PNG file

            # For example, display a message
            tk.messagebox.showinfo("Success", "Files processed successfully!")

        else:
            # If either file is missing, show an error message
            tk.messagebox.showerror("Error", "Please select both CSV and PNG files.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSelectorApp(root)
    root.mainloop()
