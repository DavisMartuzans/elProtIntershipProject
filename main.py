import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox, QMainWindow, QHeaderView, QStatusBar, QCheckBox, QComboBox, QSlider
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt
import pandas as pd
from image_processor import ImageProcessor
import cv2

class FileSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("elProt Ibom")
        self.setGeometry(100, 100, 1000, 600)

        self.csv_file_path = None
        self.jpg_file_path = None
        self.image_processor = None
        self.bitmap_window = None  # Reference to BitmapWindow
        self.selected_image_path = None  # Path to the currently selected image

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

        self.tree_widget = QTreeWidget(self)  # Pass the parent widget as an argument
        self.tree_widget.setColumnCount(14)  # Increased column count to accommodate checkbox
        self.tree_widget.setHeaderLabels(
            ["Check", "Designator", "Comment", "Layer", "Footprint", "Center-X(mm)", "Center-Y(mm)", "Rotation",
             "Description", "Manufacture Part Number 1", "Supplier Part Number 1", ""])  # Added empty label for checkbox column
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        file_paths_layout.addWidget(self.tree_widget)

        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

        # Connect itemClicked signal to custom slot
        self.tree_widget.itemClicked.connect(self.onTreeItemClicked)

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
            self.selected_image_path = file_path  # Update selected image path
            self.status_bar.showMessage("JPG/PNG file selected: " + file_path)
            self.show_image(file_path)

    def show_image(self, file_path):
        if not self.bitmap_window:
            self.bitmap_window = BitmapWindow(file_path, self.image_processor)
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

        # Initialize ImageProcessor with the image path and resolution
        self.image_processor = ImageProcessor(self.jpg_file_path, image_resolution)

        # Create BitmapWindow and pass the ImageProcessor instance to it
        if not self.bitmap_window:
            self.bitmap_window = BitmapWindow(self.selected_image_path, self.image_processor)
        else:
            self.bitmap_window.image_processor = self.image_processor
            self.bitmap_window.show_image(self.selected_image_path)

        # Show BitmapWindow
        self.bitmap_window.show()

        # Read CSV file and store designator coordinates in ImageProcessor
        bom_data = self.read_csv_with_warnings(self.csv_file_path)
        if not bom_data.empty:
            self.display_bom_data(bom_data)
            self.status_bar.showMessage("Files processed successfully!", 3000)

            # Store designator coordinates in ImageProcessor
            for _, row in bom_data.iterrows():
                footprint = row["Designator"]
                x_mm = row["Center-X(mm)"]
                y_mm = row["Center-Y(mm)"]
                rotation = row["Rotation"]
                self.image_processor.draw_marker_on_designator(footprint, x_mm, y_mm, rotation)

    def display_bom_data(self, bom_data):
        self.tree_widget.clear()
        self.tree_widget.setColumnCount(14)
        self.tree_widget.setHeaderLabels(
            ["Check", "Designator", "Comment", "Layer", "Footprint", "Center-X(mm)", "Center-Y(mm)", "Rotation",
             "Description", "Manufacture Part Number 1", "Supplier Part Number 1", ""])

        for _, row in bom_data.iterrows():
            item = QTreeWidgetItem(self.tree_widget)
            item.setCheckState(0, Qt.Unchecked)
            item.setText(1, row["Designator"])
            item.setText(2, row["Comment"])
            item.setText(3, row["Layer"])
            item.setText(4, row["Footprint"])
            item.setText(5, str(row["Center-X(mm)"]))
            item.setText(6, str(row["Center-Y(mm)"]))
            item.setText(7, str(row["Rotation"]))
            item.setText(8, row["Description"])
            item.setText(9, row["Manufacture Part Number 1"])
            item.setText(10, row["Supplier Part Number 1"])

    def onTreeItemClicked(self, item, column):
        if column == 0:
            item.setCheckState(column, Qt.Checked if item.checkState(column) == Qt.Unchecked else Qt.Unchecked)

    def get_image_resolution(self):
        try:
            # Load the image using OpenCV to get its resolution
            image = cv2.imread(self.image_path)
            if image is None:
                print("Error: Failed to load the image.")
                return None
            else:
                h, w, _ = image.shape
                print("Image loaded successfully.")
                print(f"Image shape: {w}x{h}")
                return w, h
        except Exception as e:
            print(f"Error getting image resolution: {e}")
            return None


class BitmapWindow(QMainWindow):
    def __init__(self, image_path, image_processor):
        super().__init__()
        self.setWindowTitle("Bitmap Window")
        self.setGeometry(200, 200, 600, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.bitmap_label = QLabel()
        layout.addWidget(self.bitmap_label)

        self.ratio_label = QLabel("Scale Ratio: 1.0")
        layout.addWidget(self.ratio_label)

        self.ratio_slider = QSlider(Qt.Horizontal)
        self.ratio_slider.setMinimum(1)
        self.ratio_slider.setMaximum(10)
        self.ratio_slider.setTickPosition(QSlider.TicksBelow)
        self.ratio_slider.setTickInterval(1)
        self.ratio_slider.valueChanged.connect(self.update_ratio)
        layout.addWidget(self.ratio_slider)

        self.image_processor = image_processor

        # Show the image at the start
        self.show_image(image_path)
        self.scale_ratio = 1.0

    def show_image(self, file_path):
        # Load the image using QImage
        q_image = QImage(file_path)
        if q_image.isNull():
            QMessageBox.critical(self, "Error", "Failed to load image")
            return

        # Convert QImage to QPixmap for display
        pixmap = QPixmap.fromImage(q_image)

        # Resize the image if necessary to fit the window
        max_size = max(self.width(), self.height())
        if pixmap.width() > max_size or pixmap.height() > max_size:
            pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Display the image
        self.bitmap_label.setPixmap(pixmap)
        self.bitmap_label.setScaledContents(True)

        print("Image displayed successfully.")

    def mark_designators_on_image(self):
        if self.image_processor:
            pixmap_label = self.bitmap_label
            self.image_processor.mark_designators_on_image(pixmap_label, self.scale_ratio, lock_to_real_size=True)
        else:
            QMessageBox.critical(self, "Error", "Image processor not initialized.")

    def update_ratio(self, value):
        self.scale_ratio = value / 10
        self.ratio_label.setText(f"Scale Ratio: {self.scale_ratio:.1f}")
        self.mark_designators_on_image()

    def paintEvent(self, event):
        QMainWindow.paintEvent(self, event)
        if self.image_processor:
            pixmap_label = self.bitmap_label
            painter = QPainter(pixmap_label.pixmap())
            painter.setPen(QPen(Qt.gray, 1, Qt.DotLine))

            # Draw vertical lines
            for x in range(0, pixmap_label.width(), 15):  # Adjust the spacing of the grid as needed
                painter.drawLine(x, 0, x, pixmap_label.height())

            # Draw horizontal lines
            for y in range(0, pixmap_label.height(), 15):  # Adjust the spacing of the grid as needed
                painter.drawLine(0, y, pixmap_label.width(), y)

            painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_selector_app = FileSelectorApp()
    file_selector_app.show()

    sys.exit(app.exec_())
