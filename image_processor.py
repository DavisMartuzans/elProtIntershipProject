import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox, QMainWindow, QHeaderView, QStatusBar, QCheckBox, QComboBox, QSlider
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QImageReader
from PyQt5.QtCore import Qt
import pandas as pd

import cv2
import numpy as np

class ImageProcessor:
    def __init__(self, image_path, image_resolution):
        self.image_path = image_path
        self.image_resolution = image_resolution
        self.designator_markers = {}

    def draw_marker_on_designator(self, footprint, x_mm, y_mm, rotation):
        x_px = int(x_mm * self.image_reso+lution[0] / 25.4)
        y_px = int(y_mm * self.image_resolution[1] / 25.4)
        self.designator_markers[footprint] = (x_px, y_px, rotation)

    def draw_designator_markers(self, pixmap):
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

        for footprint, (x, y, rotation) in self.designator_markers.items():
            # Draw marker on the pixmap
            painter.drawEllipse(x - 5, y - 5, 10, 10)

        painter.end()

    def mark_designators_on_image(self, pixmap_label, scale_ratio=1.0, lock_to_real_size=False):
        try:
            # Load the selected image using OpenCV
            image = cv2.imread(self.image_path)
            for footprint, (x, y, rotation) in self.designator_markers.items():
                # Draw marker on the image if designator is None or matches the given designator
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

            # Lock the image to its real size if requested
            if lock_to_real_size:
                pixmap_label.setScaledContents(False)
                pixmap_label.adjustSize()

        except Exception as e:
            print(f"Error marking designators on image: {e}")

    def get_image_resolution(self):
        try:
            # Use QImageReader to get the image resolution
            image_reader = QImageReader(self.image_path)
            size = image_reader.size()
            if size.isValid():
                return size.width(), size.height()
            else:
                print("Error: Invalid image size.")
                return None
        except Exception as e:
            print(f"Error getting image resolution: {e}")
            return None