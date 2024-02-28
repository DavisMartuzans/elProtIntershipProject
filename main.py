import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox, QMenu, QAction, QHeaderView, QStatusBar
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QColor
from PyQt5.QtCore import Qt, QPoint

import pandas as pd
import cv2  # Import OpenCV for image processing

from image_processor import ImageProcessor


class FileSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("elProt Ibom")
        self.setGeometry(100, 100, 1000, 600)  # Increased width and height

        self.csv_file_path = None
        self.bmp_file_path = None
        self.image_processor = None

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # File paths layout
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

        # Tree view layout
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(12)  # Set column count to 12
        self.tree_widget.setHeaderLabels(["Designator", "Comment", "Layer", "Footprint", "Center-X(mm)", "Center-Y(mm)", "Rotation", "Description", "Manufacture Part Number 1", "Supplier Part Number 1", "X", "Y"])  # Set header labels
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)  # Adjust column widths
        self.tree_widget.itemClicked.connect(self.handle_table_item_click)  # Connect item click event
        file_paths_layout.addWidget(self.tree_widget)

        # Next button layout
        next_button = QPushButton("Next")
        next_button.setToolTip("Click to process files")
        next_button.clicked.connect(self.process_files)
        file_paths_layout.addWidget(next_button)

        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        # Image display layout
        self.image_label = QLabel()
        self.image_label.setFixedSize(600, 600)  # Increased size
        layout.addWidget(self.image_label)

        # Set layout
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
        try:
            # Load the bitmap image
            bitmap_image = cv2.imread(file_path)

            # Convert BGR image to RGB
            bitmap_image = cv2.cvtColor(bitmap_image, cv2.COLOR_BGR2RGB)

            # Convert the bitmap image to QImage format
            height, width, channel = bitmap_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(bitmap_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Display the QImage in the QLabel
            pixmap = QPixmap(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), aspectRatioMode=True))
            self.image_label.setText("Selected Image (Bitmap)")

            # Initialize the ImageProcessor with the bitmap image path
            self.image_processor = ImageProcessor(file_path)

        except Exception as e:
            self.status_bar.showMessage(f"Error displaying Bitmap: {e}")

    def read_csv_with_warnings(self, csv_path):
        try:
            bom_data = pd.read_csv(csv_path)
        except Exception as e:
            self.status_bar.showMessage(f"Error reading CSV: {e}")
            bom_data = pd.DataFrame()  # or None, depending on your use case
        return bom_data

    def process_files(self):
        if not self.csv_file_path or not self.bmp_file_path:
            QMessageBox.critical(self, "Error", "Please select both CSV and Bitmap files.")
            return

        self.image_processor = ImageProcessor(self.bmp_file_path)

        bom_data = self.read_csv_with_warnings(self.csv_file_path)
        if not bom_data.empty:
            self.display_bom_data(bom_data)
            self.status_bar.showMessage("Files processed successfully!", 3000)  # Show for 3 seconds
            # Placeholder for additional functionality
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
                "",  # Placeholder for X column
                "",  # Placeholder for Y column
            ])
            self.tree_widget.addTopLevelItem(item)

    def handle_table_item_click(self, item, column):
        designator_index = 0  # Assuming the designator is in the first column
        designator = item.text(designator_index)
        if self.image_processor:
            self.image_processor.draw_marker_on_designator(designator)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_selector_app = FileSelectorApp()  # Create an instance of FileSelectorApp
    file_selector_app.show()  # Show the file selector app
    sys.exit(app.exec_())
