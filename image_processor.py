import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage

class ImageProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image to Coordinates Converter")
        self.image_path = None
        self.image_processor = None  # Initialize ImageProcessor object

        layout = QVBoxLayout()

        self.image_label = QLabel("No image selected.")
        layout.addWidget(self.image_label)

        select_button = QPushButton("Select Image")
        select_button.clicked.connect(self.select_image)
        layout.addWidget(select_button)

        convert_button = QPushButton("Convert to Coordinates Image")
        convert_button.clicked.connect(self.convert_to_coordinates_image)
        layout.addWidget(convert_button)

        save_button = QPushButton("Save Bitmap Image")
        save_button.clicked.connect(self.save_bitmap_image)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def select_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaledToWidth(400))
            self.image_label.setText("Selected Image: " + file_path)
            self.image_processor = ImageProcessor(file_path)  # Create ImageProcessor object

    def convert_to_coordinates_image(self):
        if self.image_path is None or self.image_processor is None:
            return
    
        # Extract coordinates using ImageProcessor
        coordinates = self.image_processor.extract_coordinates()
        
        if coordinates:
            # Load the image
            image = cv2.imread(self.image_path)

            # Process the image (if needed)

            # Convert the image to bitmap format
            bitmap_image = self.image_processor.convert_to_bitmap(image)

            # Display the bitmap image
            self.display_bitmap_image(bitmap_image)
            
            print("Coordinates image transformed and displayed successfully.")
        else:
            print("Failed to extract coordinates.")

    def save_bitmap_image(self):
        if self.image_path is None or self.image_processor is None:
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Save Bitmap Image", "", "Image Files (*.bmp)")
        if file_path:
            success = self.image_processor.save_bitmap(file_path)
            if success:
                print("Bitmap image saved successfully.")
            else:
                print("Failed to save bitmap image.")

    def display_bitmap_image(self, bitmap_image):
        # Display the bitmap image in the QLabel
        pixmap = QPixmap(bitmap_image)
        self.image_label.setPixmap(pixmap.scaledToWidth(400))
        self.image_label.setText("Selected Image (Bitmap)")

class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path

    def preprocess_image(self):
        try:
            image = cv2.imread(self.image_path)
            if image is None:
                raise ValueError("Failed to load image.")
            # Your preprocessing logic here
            return image
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None

    def extract_coordinates(self):
        try:
            # Preprocess the image
            processed_image = self.preprocess_image()
            if processed_image is None:
                return None

            # Your coordinate extraction logic here
            coordinates = [(100, 100), (200, 200)]  # Example coordinates
            return coordinates
        except Exception as e:
            print(f"Error extracting coordinates: {e}")
            return None

    def convert_to_bitmap(self, image):
        # Convert the OpenCV image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Threshold the grayscale image to create a binary image
        _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)

        # Convert the binary image to bitmap format
        bitmap_image = QImage(binary_image.data, binary_image.shape[1], binary_image.shape[0], QImage.Format_Grayscale8)

        return bitmap_image

    def save_bitmap(self, output_path):
        try:
            # Preprocess the image
            processed_image = self.preprocess_image()
            if processed_image is None:
                return False
            
            # Convert the image to grayscale
            gray_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

            # Save the grayscale image
            success = cv2.imwrite(output_path, gray_image)
            if success:
                print("Image saved successfully.")
                return True
            else:
                print("Failed to save image.")
                return False
        except Exception as e:
            print(f"Error converting image to bitmap and saving: {e}")
            return False

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec_())
