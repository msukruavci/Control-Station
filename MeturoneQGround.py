import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSplitter, QMessageBox, QRadioButton
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QPalette, QBrush
from PyQt5.QtCore import QTimer, Qt, QTime
#from PyQt5 import sip
import matplotlib.pyplot as plt
import subprocess

class DroneControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeturoneQGround")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon("meturone.jpg"))

        # Set palette for background image
        palette = self.palette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("background.jpg")))
        self.setPalette(palette)

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Add horizontal splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        # Layout for table in the left panel
        self.table_layout = QVBoxLayout()
        self.splitter.addWidget(QWidget())  # Add a blank widget for the left panel
        self.splitter.addWidget(QWidget())  # Add a blank widget for the right panel
        self.splitter.setSizes([200, 800])  # Set splitter sizes
        self.splitter.setStyleSheet("QSplitter::handle{background-color: gray;}")  # Style for splitter handle

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # Add one more column for Time
        self.table.setHorizontalHeaderLabels(["Time", "Image \n Matrix", "Altitude", "Distance to \n Other Aircraft", "Ammunition", "Battery",  "Speed"])
        self.table.verticalHeader().setFont(QFont("Arial", 12))
        self.table.horizontalHeader().setFont(QFont("Arial", 12))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(200)
        self.table.setStyleSheet("QTableWidget{background-color: #f0f0f0; color: black;}"
                                  "QTableWidget::item:selected{background-color: #3daee9; color: white;}")
        self.table_layout.addWidget(self.table)
        self.splitter.widget(0).setLayout(self.table_layout)

        # Set column widths
        column_width = 50
        for column in range(self.table.columnCount()):
            self.table.setColumnWidth(column, column_width)

        # Layout for clear table button
        self.clear_button_layout = QHBoxLayout()
        self.clear_button_layout.addStretch()
        self.clear_button = QPushButton("Clear Table")
        self.clear_button.setStyleSheet("QPushButton{background-color: #ff4d4d; color: white; border: 2px solid #ff4d4d; border-radius: 10px; font-weight: bold;}"
                                         "QPushButton:hover{background-color: #ff6666; border: 2px solid #ff6666;}")
        self.clear_button.setFixedSize(150, 50)
        self.clear_button_layout.addWidget(self.clear_button)
        self.splitter.widget(0).layout().addLayout(self.clear_button_layout)
        self.clear_button.clicked.connect(self.clear_table)


        # Layout for video playback in the right panel
        self.video_layout = QVBoxLayout()
        self.splitter.widget(1).setLayout(self.video_layout)

        # Label for video image
        self.video_label = QLabel()
        self.video_layout.addWidget(self.video_label)

        # Drone movement buttons
        self.depart_button = QPushButton("Depart")
        self.depart_button.setStyleSheet("QPushButton{background-color: #3daee9; color: white; border: 2px solid #3daee9; border-radius: 10px; font-weight: bold;}"
                                          "QPushButton:hover{background-color: #4fc1f5; border: 2px solid #4fc1f5;}")
        self.depart_button.clicked.connect(self.start_drone_simulation)
        self.depart_button.setFixedSize(150, 50)
        self.video_layout.addWidget(self.depart_button)

        self.start_button = QPushButton("Start Camera")
        self.start_button.setStyleSheet("QPushButton{background-color: #5cb85c; color: white; border: 2px solid #5cb85c; border-radius: 10px; font-weight: bold;}"
                                         "QPushButton:hover{background-color: #70db70; border: 2px solid #70db70;}")
        self.start_button.setFixedSize(150, 50)
        self.start_button.clicked.connect(self.start_camera)
        self.video_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.setStyleSheet("QPushButton{background-color: #d9534f; color: white; border: 2px solid #d9534f; border-radius: 10px; font-weight: bold;}"
                                        "QPushButton:hover{background-color: #e57373; border: 2px solid #e57373;}")
        self.stop_button.setFixedSize(150, 50)
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        self.video_layout.addWidget(self.stop_button)

        self.landing_button = QPushButton("Land")
        self.landing_button.setStyleSheet("QPushButton{background-color: #ff9900; color: white; border: 2px solid #ff9900; border-radius: 10px; font-weight: bold;}"
                                           "QPushButton:hover{background-color: #ffb266; border: 2px solid #ffb266;}")
        self.landing_button.setFixedSize(150, 50)
        self.landing_button.clicked.connect(self.land_drone)
        self.landing_button.setEnabled(False)
        self.video_layout.addWidget(self.landing_button)

        # Button for camera settings
        self.command_test_button = QPushButton("command_test")
        self.command_test_button.setStyleSheet("QPushButton{background-color: #ffcc00; color: black; border: 2px solid #ffcc00; border-radius: 10px; font-weight: bold;}"
                                                   "QPushButton:hover{background-color: #ffd633; border: 2px solid #ffd633;}")
        self.command_test_button.setFixedSize(150, 50)
        self.command_test_button.clicked.connect(self.command_test)
        self.video_layout.addWidget(self.command_test_button)



        # Camera update timers
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_frame)

        self.table_timer = QTimer()
        self.table_timer.timeout.connect(self.update_table)

        self.capture = None
        self.is_camera_started = False

        #sip.setdestroyonexit(False)  

        # Layouts for graph button and radio buttons
        self.graph_button_layout = QVBoxLayout()
        self.graph_button_layout.addStretch()

        self.graph_button = QPushButton("Graph")
        self.graph_button.setStyleSheet("QPushButton{background-color: #6666ff; color: white; border: 2px solid #6666ff; border-radius: 10px; font-weight: bold;}"
                                         "QPushButton:hover{background-color: #9999ff; border: 2px solid #9999ff;}")
        self.graph_button.setFixedSize(150, 50)
        self.graph_button.clicked.connect(self.show_graph)
        self.graph_button_layout.addWidget(self.graph_button)

        self.video_layout.addLayout(self.graph_button_layout)

        # Layout for radio buttons
        self.radio_button_layout = QVBoxLayout()
        self.radio_button_layout.addStretch()

        # Create radio buttons from table headers
        self.radio_buttons = []
        for column in range(2,self.table.columnCount()):
            header = self.table.horizontalHeaderItem(column).text()
            radio_button = QRadioButton(header)
            self.radio_buttons.append(radio_button)
            self.radio_button_layout.addWidget(radio_button)

        self.video_layout.addLayout(self.radio_button_layout)

    def command_test(self):

        komut1 = "roscore"
        komut2 = "gazebo"

        try:
            subprocess.run(["gnome-terminal", "--", "bash", "-c", komut1])
            subprocess.run(["gnome-terminal", "--", "bash", "-c", komut2])
        except Exception as e:
            print(f'Hata oluştu: {e}')
        else:
            print('Komut calisti.')
            
    def start_camera(self):
        if not self.is_camera_started:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                print("Error: Camera could not be opened.")
                return
            self.is_camera_started = True
            self.camera_timer.start(30)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.landing_button.setEnabled(True)

    def stop_camera(self):
        if self.is_camera_started:
            self.camera_timer.stop()
            if self.capture is not None:  # Check if capture is initialized
                self.capture.release()  # Release capture only if initialized
            self.video_label.clear()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.landing_button.setEnabled(False)
            self.is_camera_started = False

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
            self.display_video(frame)

    def display_video(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        pixmap = pixmap.scaledToWidth(self.video_label.width())
        self.video_label.setPixmap(pixmap)

    def start_drone_simulation(self):
        if not self.table_timer.isActive():
            self.table_timer.start(1000)  

    def land_drone(self):
        if self.table_timer.isActive():
            self.table_timer.stop()

    def update_table(self):
        if not self.isVisible():
            return  # Skip table update if window is not visible
        current_time = QTime.currentTime().toString("hh:mm:ss")
        altitude = np.random.randint(0, 1000)
        distance = np.random.randint(0, 1000)
        ammunition = np.random.randint(0, 100)
        battery = np.random.randint(0, 100)
        matrix = np.random.randint(0, 255, size=(3, 3))
        speed = np.random.randint(0, 100)

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(current_time))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(matrix)))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(altitude)))
        self.table.setItem(row_position, 3, QTableWidgetItem(str(distance)))
        self.table.setItem(row_position, 4, QTableWidgetItem(str(ammunition)))
        self.table.setItem(row_position, 5, QTableWidgetItem(str(battery)))
        self.table.setItem(row_position, 6, QTableWidgetItem(str(speed)))

        # Limit table rows to a certain number (optional)
        max_rows = 100
        if self.table.rowCount() > max_rows:
            self.table.removeRow(0)

    def clear_table(self):
        self.table.clearContents()  # Clear cell contents
        self.table.setRowCount(0)  # Set row count to 0

    def show_graph(self):
        # Get index of selected radio button
        selected_index = -1
        for index, radio_button in enumerate(self.radio_buttons):
            if radio_button.isChecked():
                selected_index = index + 2
                break

        if selected_index == -1:
            QMessageBox.warning(self, "Warning", "Please select a column.")
            return

        # Get header of selected column
        header = self.table.horizontalHeaderItem(selected_index).text()

        # Get data based on column
        data = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, selected_index)
            if item is not None and item.text().isdigit():
                data.append(int(item.text()))

        # There should be at least two data points
        if len(data) < 2:
            QMessageBox.warning(self, "Warning", "Not enough data points to plot.")
            return

        # Create matplotlib graph
        plt.figure()
        plt.plot(data)
        plt.xlabel("Index")
        plt.ylabel(header)
        plt.title(f"{header} vs. Index")
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneControlWindow()
    window.show()
    sys.exit(app.exec_())
