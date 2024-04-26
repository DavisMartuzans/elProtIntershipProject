# PCB Component Highlighter
## Overview
The PCB Component Highlighter is a graphical application built using Python and Tkinter. It allows users to visualize and manipulate Pick-and-Place (PNP) component data on a printed circuit board (PCB) image.
## Features
- **Load Files**: Users can load PNP data from a CSV file and select a PCB image file.
- **Display Component Data**: Component data is displayed in a Treeview widget, showing details such as name, coordinates, rotation, layer, footprint, and part numbers.
- **Visualization**: Components can be highlighted on the PCB image canvas using customizable markers.
- **Transformation**: Scaling, offsetting, rotation, and mirroring transformations can be applied to the component positions.
- **Export**: Component data can be exported to an Excel spreadsheet.
## Usage
1. Launch the application.
2. Load a PNP file and a PCB image file using the file dialogs.
3. View and manipulate component data using the controls provided.
4. Click on a component in the Treeview to highlight it on the PCB image canvas.
5. Adjust marker settings and apply transformations as needed.
6. Export the component data to an Excel spreadsheet.
## Requirements
- Python 3.x
- Tkinter
- PIL (Python Imaging Library)
- `csv` module
## Installation
1. Clone the repository to your local machine.
2. Ensure you have Python installed.
3. Install the required packages using pip:
pip install pillow
## Usage Example
python pcb_tool.py
## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
