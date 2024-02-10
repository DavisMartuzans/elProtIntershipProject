import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QIcon, QPen, QColor
import pandas as pd

class FileSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("elProt Ibom")
        self.setGeometry(100, 100, 800, 600)

        self.csv_file_path = None
        self.png_file_path = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # File paths layout
        file_paths_layout = QHBoxLayout()
        layout.addLayout(file_paths_layout)

        csv_label = QLabel("Select CSV File:")
        file_paths_layout.addWidget(csv_label)

        self.csv_line_edit = QLineEdit()
        self.csv_line_edit.setReadOnly(True)
        file_paths_layout.addWidget(self.csv_line_edit)

        csv_button = QPushButton("Browse CSV")
        csv_button.clicked.connect(self.browse_csv)
        file_paths_layout.addWidget(csv_button)

        png_label = QLabel("Select PNG File:")
        file_paths_layout.addWidget(png_label)

        self.png_line_edit = QLineEdit()
        self.png_line_edit.setReadOnly(True)
        file_paths_layout.addWidget(self.png_line_edit)

        png_button = QPushButton("Browse PNG")
        png_button.clicked.connect(self.browse_png)
        file_paths_layout.addWidget(png_button)

        # Graphics view layout
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.scene)
        layout.addWidget(self.graphics_view)

        # Tree view layout
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(3)
        self.tree_widget.setHeaderLabels(["Designator", "X(mm)", "Y(mm)"])
        self.tree_widget.itemSelectionChanged.connect(self.on_tree_item_selection_changed)
        layout.addWidget(self.tree_widget)

        # Next button layout
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.process_files)
        layout.addWidget(next_button)

        self.setLayout(layout)

    def browse_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.csv_file_path = file_path
            self.csv_line_edit.setText(file_path)

    def browse_png(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select PNG File", "", "PNG Files (*.png)")
        if file_path:
            self.png_file_path = file_path
            self.png_line_edit.setText(file_path)

    def read_csv_with_warnings(self, csv_path):
        try:
            bom_data = pd.read_csv(csv_path)
        except pd.errors.ParserError as e:
            QMessageBox.warning(self, "Warning", f"Error reading CSV: {e}")
            bom_data = pd.DataFrame()  # or None, depending on your use case
        return bom_data

    def process_files(self):
        if not self.csv_file_path or not self.png_file_path:
            QMessageBox.critical(self, "Error", "Please select both CSV and PNG files.")
            return

        bom_data = self.read_csv_with_warnings(self.csv_file_path)
        if not bom_data.empty:
            self.display_bom_data(bom_data)
            QMessageBox.information(self, "Success", "Files processed successfully!")
        else:
            QMessageBox.warning(self, "Warning", "No data to display.")

    def display_bom_data(self, bom_data):
        self.tree_widget.clear()
        for _, row in bom_data.iterrows():
            item = QTreeWidgetItem([row["Designator"], row["Center-X(mm)"], row["Center-Y(mm)"]])
            self.tree_widget.addTopLevelItem(item)

    def on_tree_item_selection_changed(self):
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            selected_item_text = [item.text(0) for item in selected_items]
            self.highlight_graphics_items(selected_item_text)
        else:
            self.scene.clear()

    def highlight_graphics_items(self, item_text_list):
        self.scene.clear()
        for item_text in item_text_list:
            # Draw a red circle at the specified position
            x = float(self.get_item_data(item_text, "X(mm)"))
            y = float(self.get_item_data(item_text, "Y(mm)"))
            circle_item = self.scene.addEllipse(x, y, 10, 10, QPen(QColor("red")))
            circle_item.setFlag(QGraphicsItem.ItemIsSelectable)

    def get_item_data(self, designator, column):
        bom_data = pd.read_csv(self.csv_file_path)
        data = bom_data.loc[bom_data["Designator"] == designator, column].values[0]
        if isinstance(data, float):
            if pd.isnull(data):  # Check if it's NaN
                return ""  # or any default value you want
            else:
                return str(data)
        return str(data)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSelectorApp()
    window.show()
    sys.exit(app.exec_())
