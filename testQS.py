import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit,
    QMessageBox, QRadioButton, QTabWidget, QDialog
)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QPalette, QBrush
from PyQt5.QtCore import QTimer, QTime, Qt
import os

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(1100, 550, 400, 200)
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

        if username == "admin" and password == "123456":
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Invalid username or password.")

class DroneControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeturoneQGround")
        self.setGeometry(800, 500, 1000, 600)
        self.setWindowIcon(QIcon("meturone.jpg"))

        palette = self.palette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("background.jpg")))
        self.setPalette(palette)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()  # Main layout
        self.central_widget.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.table_tab = QWidget()
        self.tab_widget.addTab(self.table_tab, "Table")

        self.table_layout = QVBoxLayout(self.table_tab)

        self.table = QTableWidget()
        self.table.setColumnCount(7) 
        self.table.setHorizontalHeaderLabels(["Time", "Image \n Matrix", "Altitude", "Distance to \n Other Aircraft", "Ammunition", "Battery",  "Speed"])
        self.table.verticalHeader().setFont(QFont("Arial", 12))
        self.table.horizontalHeader().setFont(QFont("Arial", 12))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(200)
        self.table.setStyleSheet("QTableWidget{background-color: #f0f0f0; color: black;}"
                                  "QTableWidget::item:selected{background-color: #3daee9; color: white;}")
        self.table_layout.addWidget(self.table)

        self.radio_button_layout = QHBoxLayout()
        self.table_layout.addLayout(self.radio_button_layout)

        self.radio_buttons = []
        for column in range(2, self.table.columnCount()):
            header = self.table.horizontalHeaderItem(column).text()
            radio_button = QRadioButton(header)
            self.radio_buttons.append(radio_button)
            self.radio_button_layout.addWidget(radio_button)

        self.graph_button = QPushButton("Graph")
        self.graph_button.clicked.connect(self.show_graph)
        self.table_layout.addWidget(self.graph_button)
        self.graph_button.setStyleSheet("background-color: #008CBA; color: white;")

        self.video_tab = QWidget()
        self.tab_widget.addTab(self.video_tab, "Video")

        self.video_layout = QVBoxLayout(self.video_tab)

        self.video_label = QLabel()
        self.video_layout.addWidget(self.video_label)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address")
        self.video_layout.addWidget(self.ip_input)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_ip)
        self.video_layout.addWidget(self.connect_button)
        self.connect_button.setStyleSheet("background-color: #4CAF50; color: white;")

        self.depart_button = QPushButton("Depart")
        self.depart_button.clicked.connect(self.start_drone_simulation)
        self.video_layout.addWidget(self.depart_button)
        self.depart_button.setStyleSheet("background-color: #4CAF50; color: white;")

        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        self.video_layout.addWidget(self.start_button)
        self.start_button.setStyleSheet("background-color: #f44336; color: white;")

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        self.video_layout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #f44336; color: white;")

        self.landing_button = QPushButton("Land")
        self.landing_button.clicked.connect(self.land_drone)
        self.video_layout.addWidget(self.landing_button)
        self.landing_button.setEnabled(False)
        self.landing_button.setStyleSheet("background-color: #4CAF50; color: white;")

        self.start_recording_button = QPushButton("Start Recording")
        self.start_recording_button.clicked.connect(self.start_recording)
        self.video_layout.addWidget(self.start_recording_button)
        self.start_recording_button.setStyleSheet("background-color: #008CBA; color: white;")

        self.stop_recording_button = QPushButton("Stop Recording")
        self.stop_recording_button.clicked.connect(self.stop_recording)
        self.video_layout.addWidget(self.stop_recording_button)
        self.stop_recording_button.setEnabled(False)
        self.stop_recording_button.setStyleSheet("background-color: #f44336; color: white;")

        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_frame)

        self.table_timer = QTimer()
        self.table_timer.timeout.connect(self.update_table)

        self.capture = None
        self.is_camera_started = False
        self.is_recording = False
        self.recording_folder = None
        self.video_writer = None

    def connect_to_ip(self):
        ip_address = self.ip_input.text().strip()
        if not ip_address:
            QMessageBox.warning(self, "Warning", "Please enter a valid IP address.")
            return

        # Try connecting with different backends
        backends = [cv2.CAP_FFMPEG, cv2.CAP_DSHOW, cv2.CAP_GSTREAMER, cv2.CAP_ANY]

        for backend in backends:
            self.capture = cv2.VideoCapture(f'rtsp://username:password@{ip_address}:port/stream', backend)
            if self.capture.isOpened():
                QMessageBox.information(self, "Info", f"Connected to IP: {ip_address} using backend {backend}")
                return

        QMessageBox.warning(self, "Warning", "Cannot connect to IP camera with any available backend.")
        print(f"Failed to connect to IP: {ip_address} with all tested backends.")

    def start_camera(self):
        if not self.is_camera_started:
            # Test with local camera first
            self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.capture.isOpened():
                QMessageBox.warning(self, "Warning", "Local camera could not be opened.")
                return
            self.is_camera_started = True
            self.camera_timer.start(30)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_camera(self):
        if self.is_camera_started:
            self.camera_timer.stop()
            self.capture.release()
            self.is_camera_started = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qImg))

    def show_graph(self):
        # Implement your graph display logic here
        QMessageBox.information(self, "Info", "Graph button clicked")

    def start_drone_simulation(self):
        # Implement your drone simulation logic here
        QMessageBox.information(self, "Info", "Depart button clicked")

    def land_drone(self):
        # Implement your drone landing logic here
        QMessageBox.information(self, "Info", "Land button clicked")

    def start_recording(self):
        # Implement your start recording logic here
        self.is_recording = True
        self.stop_recording_button.setEnabled(True)
        self.start_recording_button.setEnabled(False)
        QMessageBox.information(self, "Info", "Recording started")

    def stop_recording(self):
        # Implement your stop recording logic here
        self.is_recording = False
        self.stop_recording_button.setEnabled(False)
        self.start_recording_button.setEnabled(True)
        QMessageBox.information(self, "Info", "Recording stopped")

    def update_table(self):
        # Implement your table update logic here
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        window = DroneControlWindow()
        window.show()
        sys.exit(app.exec_())
