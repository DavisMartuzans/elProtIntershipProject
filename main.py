import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox, QMenu, QAction, QStatusBar, QMainWindow, QHeaderView
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

import pandas as pd
import cv2
import numpy as np

class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.designator_markers = {}  # Dictionary to store designator markers

    def draw_marker_on_designator(self, designator):
        # Placeholder method to draw a marker on the image based on the designator
        # Replace this with your actual implementation
        print(f"Drawing marker for designator: {designator}")

        # For demonstration, let's just store the designator as a marker
        self.designator_markers[designator] = True

    def draw_designator_markers(self, pixmap):
        # Draw circles for each designator marker on the pixmap
        painter = QPainter(pixmap)
        pen = QPen(Qt.red)
        pen.setWidth(2)
        painter.setPen(pen)

        for designator in self.designator_markers.keys():
            # Example: Draw circle at position (100, 100) with radius 20
            painter.drawEllipse(QPoint(100, 100), 20, 20)

        painter.end()

class FileSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("elProt Ibom")
        self.setGeometry(100, 100, 1000, 600)  

        self.csv_file_path = None
        self.bmp_file_path = None
        self.image_processor = None
        self.bitmap_window = None  # Reference to BitmapWindow

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        file_paths_layout = QVBoxLayout()
        layout.addLayout(file_paths_layout)

        csv_button = QPushButton("Browse CSV")
        csv_button.setToolTip("Click to browse for a CSV file")
        csv_button.clicked.connect(self.browse_csv)
        file_paths_layout.addWidget(csv_button)

        bmp_button = QPushButton("Browse Bitmap")
        bmp_button.setToolTip("Click to browse for a Bitmap file")
        bmp_button.clicked.connect(self.browse_bmp)
        file_paths_layout.addWidget(bmp_button)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(12)  
        self.tree_widget.setHeaderLabels(["Designator", "Comment", "Layer", "Footprint", "Center-X(mm)", "Center-Y(mm)", "Rotation", "Description", "Manufacture Part Number 1", "Supplier Part Number 1", "X", "Y"])
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)  
        self.tree_widget.itemClicked.connect(self.handle_table_item_click)
        file_paths_layout.addWidget(self.tree_widget)

        next_button = QPushButton("Next")
        next_button.setToolTip("Click to process files")
        next_button.clicked.connect(self.process_files)
        file_paths_layout.addWidget(next_button)

        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def browse_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.csv_file_path = file_path
            self.status_bar.showMessage("CSV file selected: " + file_path)

    def browse_bmp(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Bitmap File", "", "Bitmap Files (*.bmp)")
        if file_path:
            self.bmp_file_path = file_path
            self.status_bar.showMessage("Bitmap file selected: " + file_path)
            self.show_bmp_image(file_path)

    def show_bmp_image(self, file_path):
        if not self.bitmap_window:
            self.bitmap_window = BitmapWindow(file_path)
            self.bitmap_window.show()
        else:
            self.bitmap_window.show_bmp_image(file_path)

    def read_csv_with_warnings(self, csv_path):
        try:
            bom_data = pd.read_csv(csv_path)
        except Exception as e:
            self.status_bar.showMessage(f"Error reading CSV: {e}")
            bom_data = pd.DataFrame()  
        return bom_data

    def process_files(self):
        if not self.csv_file_path or not self.bmp_file_path:
            QMessageBox.critical(self, "Error", "Please select both CSV and Bitmap files.")
            return

        self.image_processor = ImageProcessor(self.bmp_file_path)

        bom_data = self.read_csv_with_warnings(self.csv_file_path)
        if not bom_data.empty:
            self.display_bom_data(bom_data)
            self.status_bar.showMessage("Files processed successfully!", 3000) 
        else:
            self.status_bar.showMessage("No data to display.")

    def display_bom_data(self, bom_data):
        self.tree_widget.clear()
        for _, row in bom_data.iterrows():
            item = QTreeWidgetItem([
                str(row["Designator"]),
                str(row["Comment"]),
                str(row["Layer"]),
                str(row["Footprint"]),
                str(row["Center-X(mm)"]),
                str(row["Center-Y(mm)"]),
                str(row["Rotation"]),
                str(row["Description"]),
                str(row["Manufacture Part Number 1"]),
                str(row["Supplier Part Number 1"]),
                "",  
                "",  
            ])
            self.tree_widget.addTopLevelItem(item)

    def handle_table_item_click(self, item, column):
        designator_index = 0  
        designator = item.text(designator_index)
        if self.image_processor:
            self.image_processor.draw_marker_on_designator(designator)

class BitmapWindow(QMainWindow):
    def __init__(self, bitmap_path):
        super().__init__()
        self.setWindowTitle("Bitmap Window")
        self.setGeometry(200, 200, 600, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.bitmap_label = QLabel()
        layout.addWidget(self.bitmap_label)
        self.central_widget.setLayout(layout)

        self.show_bmp_image(bitmap_path)

    def show_bmp_image(self, file_path):
        try:
            print("Loading bitmap image...")
            # Load the image using QImage
            q_image = QImage(file_path)
            if q_image.isNull():
                raise Exception("Failed to load image")
            
            # Convert QImage to QPixmap for display
            pixmap = QPixmap.fromImage(q_image)
            
            # Resize the image if necessary
            max_size = 600
            if pixmap.width() > max_size or pixmap.height() > max_size:
                pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio)

            # Display the image
            self.bitmap_label.setPixmap(pixmap)
            self.bitmap_label.setScaledContents(True)  # Scale the pixmap to fit the label
            
            print("Bitmap image displayed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error displaying Bitmap: {e}")

    def closeEvent(self, event):
        self.parent().bitmap_window = None
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_selector_app = FileSelectorApp()  
    file_selector_app.show()  

    sys.exit(app.exec_())
