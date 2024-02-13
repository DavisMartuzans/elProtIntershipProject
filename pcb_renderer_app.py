import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from pcb_renderer import PCBRenderer

class PCBRendererApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCB Renderer")
        self.setGeometry(100, 100, 800, 600)

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add buttons for loading PCB file and generating BOM
        load_pcb_button = QPushButton("Load PCB File")
        load_pcb_button.clicked.connect(self.load_pcb_file)
        layout.addWidget(load_pcb_button)

        generate_bom_button = QPushButton("Generate BOM")
        generate_bom_button.clicked.connect(self.generate_bom)
        layout.addWidget(generate_bom_button)

        # Add status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def load_pcb_file(self):
        # Open file dialog to select PCB file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open PCB File", "", "PCB Files (*.kicad_pcb)")

        if file_path:
            # Load PCB file
            self.renderer = PCBRenderer(file_path)
            self.status_label.setText(f"PCB file loaded: {file_path}")

    def generate_bom(self):
        if hasattr(self, 'renderer'):
            # Generate BOM using PCBRenderer instance
            self.renderer.generate_bom()
            self.status_label.setText("BOM generated successfully!")
        else:
            self.status_label.setText("No PCB file loaded.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PCBRendererApp()
    window.show()
    sys.exit(app.exec_())
