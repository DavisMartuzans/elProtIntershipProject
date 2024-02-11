import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox, QMenu, QAction, QHeaderView, QStatusBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import pandas as pd

class FileSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("elProt Ibom")
        self.setGeometry(100, 100, 1000, 600)  # Increased width and height

        self.csv_file_path = None
        self.png_file_path = None

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

        png_button = QPushButton("Browse PNG")
        png_button.setToolTip("Click to browse for a PNG file")
        png_button.clicked.connect(self.browse_png)
        file_paths_layout.addWidget(png_button)

        # Tree view layout
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(12)  # Set column count to 12
        self.tree_widget.setHeaderLabels(["Designator", "Comment", "Layer", "Footprint", "Center-X(mm)", "Center-Y(mm)", "Rotation", "Description", "Manufacture Part Number 1", "Supplier Part Number 1", "X", "Y"])  # Set header labels
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)  # Adjust column widths
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

    def browse_png(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select PNG File", "", "PNG Files (*.png)")
        if file_path:
            self.png_file_path = file_path
            self.status_bar.showMessage("PNG file selected: " + file_path)
            self.show_png_image(file_path)

    def show_png_image(self, file_path):
        try:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), aspectRatioMode=True))
        except Exception as e:
            self.status_bar.showMessage(f"Error displaying PNG: {e}")

    def read_csv_with_warnings(self, csv_path):
        try:
            bom_data = pd.read_csv(csv_path)
        except Exception as e:
            self.status_bar.showMessage(f"Error reading CSV: {e}")
            bom_data = pd.DataFrame()  # or None, depending on your use case
        return bom_data

    def process_files(self):
        if not self.csv_file_path or not self.png_file_path:
            QMessageBox.critical(self, "Error", "Please select both CSV and PNG files.")
            return

        bom_data = self.read_csv_with_warnings(self.csv_file_path)
        if not bom_data.empty:
            self.display_bom_data(bom_data)
            self.status_bar.showMessage("Files processed successfully!", 3000)  # Show for 3 seconds
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

    def context_menu_requested(self, pos):
        context_menu = QMenu(self)
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self.edit_selected_item)
        context_menu.addAction(edit_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_item)
        context_menu.addAction(delete_action)

        context_menu.exec_(self.tree_widget.viewport().mapToGlobal(pos))

    def edit_selected_item(self):
        selected_item = self.tree_widget.currentItem()
        if selected_item:
            column = self.tree_widget.currentColumn()
            if column != 0:  # Allow editing only for certain columns
                selected_item.setFlags(selected_item.flags() | Qt.ItemIsEditable)
                self.tree_widget.editItem(selected_item, column)

    def delete_selected_item(self):
        selected_item = self.tree_widget.currentItem()
        if selected_item:
            parent = selected_item.parent() or self.tree_widget.invisibleRootItem()
            parent.removeChild(selected_item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSelectorApp()
    window.show()
    sys.exit(app.exec_())
