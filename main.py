import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox, QMainWindow, QHeaderView, QStatusBar, QCheckBox
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QTransform
from PyQt5.QtCore import Qt, QPoint

import pandas as pd
import cv2
import numpy as np

class ImageProcessor:
    def __init__(self, image_path, image_resolution):
        self.image_path = image_path
        self.image_resolution = image_resolution
        self.designator_markers = {}  # Dictionary to store designator markers

    def draw_marker_on_designator(self, designator, x_mm, y_mm, rotation):
        # Convert mm to pixels
        x_px = int(x_mm * self.image_resolution[0] / 25.4)  # Convert mm to inches
        y_px = int(y_mm * self.image_resolution[1] / 25.4)  # Convert mm to inches
        self.designator_markers[designator] = (x_px, y_px, rotation)

    def draw_designator_markers(self, pixmap):
        # Draw circles for each designator marker on the pixmap
        painter = QPainter(pixmap)
        pen = QPen(Qt.red)
        pen.setWidth(2)
        painter.setPen(pen)

        for designator, (x, y, rotation) in self.designator_markers.items():
            painter.save()
            painter.translate(x, y)
            painter.rotate(rotation)
            painter.drawEllipse(QPoint(0, 0), 20, 20)
            painter.restore()

        painter.end()

    def mark_designator_on_image(self, designator, pixmap_label):
        try:
            # Load the image using OpenCV
            image = cv2.imread(self.image_path)

            # Get designator coordinates from dictionary
            x, y, rotation = self.designator_markers.get(designator, (0, 0, 0))

            # Draw marker on the image
            cv2.circle(image, (x, y), 10, (0, 0, 255), -1)  # Red circle marker

            # Convert OpenCV image to QImage
            h, w, c = image.shape
            bytes_per_line = c * w
            q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_BGR888)

            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(q_image)

            # Overlay the pixmap with the designator marker
            self.draw_designator_markers(pixmap)

            # Display the updated image
            pixmap_label.setPixmap(pixmap)
            pixmap_label.setScaledContents(True)  # Scale the pixmap to fit the label

            print("Designator marked on image.")
        except Exception as e:
            print(f"Error marking designator on image: {e}")

class FileSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("elProt Ibom")
        self.setGeometry(100, 100, 1000, 600)

        self.csv_file_path = None
        self.jpg_file_path = None
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

        jpg_button = QPushButton("Browse JPG/PNG")
        jpg_button.setToolTip("Click to browse for a JPG or PNG file")
        jpg_button.clicked.connect(self.browse_jpg)
        file_paths_layout.addWidget(jpg_button)

        next_button = QPushButton("Next")
        next_button.setToolTip("Click to process files")
        next_button.clicked.connect(self.process_files)
        file_paths_layout.addWidget(next_button)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(14)  # Increased column count to accommodate checkbox
        self.tree_widget.setHeaderLabels(
            ["Check", "Designator", "Comment", "Layer", "Footprint", "Center-X(mm)", "Center-Y(mm)", "Rotation",
             "Description", "Manufacture Part Number 1", "Supplier Part Number 1", "X", "Y", ""])  # Added empty label for checkbox column
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        file_paths_layout.addWidget(self.tree_widget)

        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def browse_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.csv_file_path = file_path
            self.status_bar.showMessage("CSV file selected: " + file_path)

    def browse_jpg(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select JPG/PNG File", "", "Image Files (*.jpg *.jpeg *.png)")
        if file_path:
            self.jpg_file_path = file_path
            self.status_bar.showMessage("JPG/PNG file selected: " + file_path)
            self.show_image(file_path)

    def show_image(self, file_path):
        if not self.bitmap_window:
            self.bitmap_window = BitmapWindow(file_path)
            self.bitmap_window.show()
        else:
            self.bitmap_window.show_image(file_path)

    def read_csv_with_warnings(self, csv_path):
        try:
            bom_data = pd.read_csv(csv_path)
        except Exception as e:
            self.status_bar.showMessage(f"Error reading CSV: {e}")
            bom_data = pd.DataFrame()
        return bom_data

    def process_files(self):
        if not self.csv_file_path or not self.jpg_file_path:
            QMessageBox.critical(self, "Error", "Please select both CSV and JPG/PNG files.")
            return

        image_resolution = self.get_image_resolution()
        if not image_resolution:
            QMessageBox.critical(self, "Error", "Failed to read image resolution.")
            return

        self.image_processor = ImageProcessor(self.jpg_file_path, image_resolution)

        bom_data = self.read_csv_with_warnings(self.csv_file_path)
        if not bom_data.empty:
            self.display_bom_data(bom_data)
            self.status_bar.showMessage("Files processed successfully!", 3000)
            self.mark_designators_on_image(bom_data)  # Call method to mark designators on the image
        else:
            self.status_bar.showMessage("No data to display.")

    def display_bom_data(self, bom_data):
        self.tree_widget.clear()
        for _, row in bom_data.iterrows():
            item = QTreeWidgetItem([
                "",
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
                ""
            ])
            self.tree_widget.addTopLevelItem(item)
            checkbox = QCheckBox()
            self.tree_widget.setItemWidget(item, 0, checkbox)  # Set checkbox widget at column 0

    def get_image_resolution(self):
        try:
            # Load the image using OpenCV to get its resolution
            image = cv2.imread(self.jpg_file_path)
            h, w, _ = image.shape
            return w, h
        except Exception as e:
            print(f"Error getting image resolution: {e}")
            return None

    def mark_designators_on_image(self, bom_data):
        for _, row in bom_data.iterrows():
            designator = str(row["Designator"])
            x_mm = float(row["Center-X(mm)"])
            y_mm = float(row["Center-Y(mm)"])
            rotation = float(row["Rotation"])
            self.image_processor.draw_marker_on_designator(designator, x_mm, y_mm, rotation)

        # Get the pixmap label from the BitmapWindow and mark designators on the image
        if self.bitmap_window:
            pixmap_label = self.bitmap_window.bitmap_label
            self.image_processor.mark_designator_on_image(None, pixmap_label)  # Pass None for designator

class BitmapWindow(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Bitmap Window")
        self.setGeometry(200, 200, 600, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.bitmap_label = QLabel()
        layout.addWidget(self.bitmap_label)
        self.central_widget.setLayout(layout)

        self.show_image(image_path)

    def show_image(self, file_path):
        try:
            print("Loading image...")
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

            print("Image displayed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error displaying image: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_selector_app = FileSelectorApp()
    file_selector_app.show()

    sys.exit(app.exec_())
