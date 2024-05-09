import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSplitter,
    QMessageBox, QRadioButton, QTabWidget, QLineEdit, QDialog
)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QPalette, QBrush, QPainter, QPen, QColor
from PyQt5.QtCore import QTimer, QTime, Qt
import matplotlib.pyplot as plt
from PyQt5 import sip

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 150)
        self.setWindowIcon(QIcon("lock_icon.png"))

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white;")

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # Giriş doğrulaması burada yapılabilir
        if username == "admin" and password == "123456":
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Invalid username or password.")

class MapTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout for the map tab
        layout = QVBoxLayout()

        # Create label for map image
        self.map_label = QLabel()
        layout.addWidget(self.map_label)

        # Set layout for the map tab
        self.setLayout(layout)

        # Load map image
        self.map_image = QPixmap("map.png")  
        self.update_map()

    def update_map(self):
        # Create a painter object
        painter = QPainter(self.map_image)
        painter.setRenderHint(QPainter.Antialiasing)

        # Example: Draw a red circle at coordinates (100, 100) with a radius of 10
        painter.setPen(QPen(Qt.red, 2))
        painter.drawEllipse(100, 100, 10, 10)

        # Example: Draw a green rectangle at coordinates (200, 200) with a width of 20 and height of 30
        painter.setPen(QPen(Qt.green, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(200, 200, 20, 30)

        # End painting
        painter.end()

        # Update map label with the modified map image
        self.map_label.setPixmap(self.map_image)

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
        self.layout = QVBoxLayout()  # Main layout
        self.central_widget.setLayout(self.layout)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Add map tab
        self.map_tab = MapTab()
        self.tab_widget.addTab(self.map_tab, "Map")

        # Add splitter for video and table tabs
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        # Add video tab
        self.video_tab = QWidget()
        self.video_tab_layout = QVBoxLayout(self.video_tab)
        self.video_label = QLabel()
        self.video_tab_layout.addWidget(self.video_label)
        self.splitter.addWidget(self.video_tab)

        # Add table tab
        self.table_tab = QWidget()
        self.table_tab_layout = QVBoxLayout(self.table_tab)
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # Add one more column for Time
        self.table.setHorizontalHeaderLabels(["Time", "Image \n Matrix", "Altitude", "Distance to \n Other Aircraft", "Ammunition", "Battery",  "Speed"])
        self.table.verticalHeader().setFont(QFont("Arial", 12))
        self.table.horizontalHeader().setFont(QFont("Arial", 12))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(200)
        self.table.setStyleSheet("QTableWidget{background-color: #f0f0f0; color: black;}"
                                  "QTableWidget::item:selected{background-color: #3daee9; color: white;}")
        self.table_tab_layout.addWidget(self.table)
        self.splitter.addWidget(self.table_tab)

        # Layout for radio buttons
        self.radio_button_layout = QHBoxLayout()
        self.table_tab_layout.addLayout(self.radio_button_layout)

        # Create radio buttons from table headers
        self.radio_buttons = []
        for column in range(2, self.table.columnCount()):
            header = self.table.horizontalHeaderItem(column).text()
            radio_button = QRadioButton(header)
            self.radio_buttons.append(radio_button)
            self.radio_button_layout.addWidget(radio_button)

        # Graph button
        self.graph_button = QPushButton("Graph")
        self.graph_button.clicked.connect(self.show_graph)
        self.table_tab_layout.addWidget(self.graph_button)
        self.graph_button.setStyleSheet("background-color: #008CBA; color: white;")

        # Drone movement buttons
        self.depart_button = QPushButton("Depart")
        self.depart_button.clicked.connect(self.start_drone_simulation)
        self.video_tab_layout.addWidget(self.depart_button)
        self.depart_button.setStyleSheet("background-color: #4CAF50; color: white;")

        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        self.video_tab_layout.addWidget(self.start_button)
        self.start_button.setStyleSheet("background-color: #f44336; color: white;")

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        self.video_tab_layout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #f44336; color: white;")

        self.landing_button = QPushButton("Land")
        self.landing_button.clicked.connect(self.land_drone)
        self.video_tab_layout.addWidget(self.landing_button)
        self.landing_button.setEnabled(False)
        self.landing_button.setStyleSheet("background-color: #4CAF50; color: white;")

        # Camera update timers
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_frame)

        self.table_timer = QTimer()
        self.table_timer.timeout.connect(self.update_table)

        self.capture = None
        self.is_camera_started = False

        sip.setdestroyonexit(False)  

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
            self.capture.release()
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
    login_window = LoginWindow()
    if login_window.exec_() == QDialog.Accepted:
        window = DroneControlWindow()
        window.show()
        sys.exit(app.exec_())
