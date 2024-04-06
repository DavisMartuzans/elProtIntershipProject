import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox, QMainWindow, QHeaderView, QStatusBar, QCheckBox
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QTransform
from PyQt5.QtCore import Qt, QPoint, QRect

import pandas as pd
import cv2
import numpy as np

class ImageProcessor:
    def __init__(self, image_path, image_resolution):
        self.image_path = image_path
        self.image_resolution = image_resolution
        self.designator_markers = {}  # Dictionary to store designator markers

    def draw_marker_on_designator(self, footprint, x_mm, y_mm, rotation):
        # Convert mm to pixels
        x_px = int(x_mm * self.image_resolution[0] / 25.4)  # Convert mm to inches
        y_px = int(y_mm * self.image_resolution[1] / 25.4)  # Convert mm to inches
        self.designator_markers[footprint] = (x_px, y_px, rotation)

    def draw_designator_markers(self, pixmap):
        painter = QPainter()
        if painter.begin(pixmap):
            print("QPainter started successfully.")
            pen = QPen(Qt.red, 4)  # Red pen with line width of 4
            painter.setPen(pen)
            painter.setBrush(Qt.yellow)  # Yellow brush for filled circle

            for footprint, (x, y, rotation) in self.designator_markers.items():
                print(f"Drawing marker for {footprint} at ({x}, {y}) with rotation {rotation}.")
                painter.drawEllipse(QPoint(x, y), 10, 10)  # Draw the ellipse with center at (x,y) and radius 10

            painter.end()
            print("QPainter ended successfully.")
        else:
            print("Failed to start QPainter.")
            
    def mark_designators_on_image(self, pixmap_label, designator=None):
        try:
            # Load the selected image using OpenCV
            image = cv2.imread(self.image_path)

            for footprint, (x, y, rotation) in self.designator_markers.items():
                # Draw marker on the image if designator is None or matches the given designator
                if designator is None or footprint == designator:
                    cv2.circle(image, (x, y), 10, (0, 0, 255), -1)  # Red circle marker

            # Convert OpenCV image to QImage
            h, w, c = image.shape
            bytes_per_line = c * w
            q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_BGR888)

            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(q_image)

            # Overlay the pixmap with the designator markers
            self.draw_designator_markers(pixmap)

            # Display the updated image
            pixmap_label.setPixmap(pixmap)
            pixmap_label.setScaledContents(True)  # Scale the pixmap to fit the label

            print("Designators marked on image.")
        except Exception as e:
            print(f"Error marking designators on image: {e}")

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

        # Connect itemClicked signal to custom slot
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)

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

        # Inicializējiet ImageProcessor ar attēla ceļu un izšķirtspēju
        self.image_processor = ImageProcessor(self.jpg_file_path, image_resolution)

        # Izveidojiet BitmapWindow un padodiet tai ImageProcessor instanci
        if not self.bitmap_window:
            self.bitmap_window = BitmapWindow(self.selected_image_path, self.image_processor)
        else:
            self.bitmap_window.image_processor = self.image_processor
            self.bitmap_window.show_image(self.selected_image_path)

        # Parādiet BitmapWindow
        self.bitmap_window.show()

        bom_data = self.read_csv_with_warnings(self.csv_file_path)
        if not bom_data.empty:
            self.display_bom_data(bom_data)
            self.mark_designators_on_image()  
            self.status_bar.showMessage("Files processed successfully!", 3000)
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

    def mark_designators_on_image(self):
        if self.bitmap_window and self.selected_image_path:
            pixmap_label = self.bitmap_window.bitmap_label
            image_processor = self.bitmap_window.image_processor
            if image_processor:
                image_processor.mark_designators_on_image(pixmap_label)
            else:
                QMessageBox.critical(self, "Error", "Image processor not initialized.")

    
    def on_tree_item_clicked(self, item, column):
        # Šeit nav vajadzības definēt metodi divreiz, ja ir vairākas funkcijas ar to pašu nosaukumu, tas var radīt neskaidrības
        # Tāpēc nodrošiniet, ka šī ir vienīgā on_tree_item_clicked definīcija

        # Iegūstam koordinātas no kokveida elementa
        try:
            x_mm = float(item.text(5))  # "Center-X(mm)" kolonna
            y_mm = float(item.text(6))  # "Center-Y(mm)" kolonna
            rotation = float(item.text(7))  # "Rotation" kolonna
        except ValueError:
            QMessageBox.warning(self, "Invalid data", "Selected item does not contain valid coordinates.")
            return

        # Iegūstam atzīmējamā komponenta nosaukumu
        designator = item.text(1)  # "Designator" kolonna

        if self.bitmap_window and self.bitmap_window.isVisible():
            if self.image_processor:
                self.image_processor.draw_marker_on_designator(designator, x_mm, y_mm, rotation)
                self.bitmap_window.update_image()
            else:
                QMessageBox.warning(self, "Error", "Image processor not initialized.")
class BitmapWindow(QMainWindow):
    def __init__(self, image_path, image_processor):
        super().__init__()
        self.setWindowTitle("Bitmap Window")
        self.setGeometry(200, 200, 600, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.bitmap_label = QLabel()
        layout.addWidget(self.bitmap_label)
        self.central_widget.setLayout(layout)

        self.image_processor = image_processor

        # Show the image at the start
        self.show_image(image_path)

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

    def mousePressEvent(self, event):
        # Ensure that the click is within the image bounds
        if self.image_processor and event.button() == Qt.LeftButton and self.bitmap_label.pixmap():
            pos = self.bitmap_label.mapFromParent(event.pos())
            if pos.x() >= 0 and pos.y() >= 0:
                # Calculate the actual image position based on the scale factor
                scale_factor = self.bitmap_label.pixmap().width() / self.bitmap_label.width()
                image_pos = QPoint(int(pos.x() * scale_factor), int(pos.y() * scale_factor))

                # Add designator marker at the clicked position
                self.image_processor.draw_marker_on_designator("Clicked", image_pos.x(), image_pos.y(), 0)

                # Update the pixmap
                self.update_image()

    # Update this method
    def update_image(self):
        # Check if the image processor is available and a pixmap currently exists
        if self.image_processor and self.bitmap_label.pixmap():
            # Load the image fresh from the file each time to prevent drawing over old markers
            q_image = QImage(self.image_processor.image_path)
            if q_image.isNull():
                QMessageBox.critical(self, "Error", "Failed to load image")
                return
            
            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(q_image)

            # Draw designator markers on the QPixmap
            self.image_processor.draw_designator_markers(pixmap)

            # Set the QPixmap onto the QLabel
            self.bitmap_label.setPixmap(pixmap)
            print("Designators should be marked on image now.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_selector_app = FileSelectorApp()
    file_selector_app.show()

    sys.exit(app.exec_())
