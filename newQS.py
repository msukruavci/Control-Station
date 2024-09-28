import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
    QMessageBox, QRadioButton, QTabWidget, QLineEdit, QDialog
)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QPalette, QBrush
from PyQt5.QtCore import QTimer, QTime, Qt
import matplotlib.pyplot as plt
from PyQt5 import sip
import csv
import os
import datetime

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

        sip.setdestroyonexit(False)

    def start_camera(self):
        # kamera calıstırma için olan fonksiyon
        # suanda bılgısayrın ana kamerasına baglı
        # Ip adresi texte yazılmıs halını kullanmak ıcın self.ip_input.text() kullanılabılır 
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
        # kamerayı durdurmak ıcın olan fonksiyon
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
            if self.is_recording:
                self.video_writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

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
        # burda random bı sekılde verıler olusturulup tabloda gosterılıyor
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

        if self.is_recording:
            self.save_table_data()

    def save_table_data(self):
        if self.recording_folder is None:
            return
        filename = os.path.join(self.recording_folder, 'table_data.csv')
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            for row in range(self.table.rowCount()):
                row_data = []
                for column in range(self.table.columnCount()):
                    item = self.table.item(row, column)
                    row_data.append(item.text() if item else '')
                writer.writerow(row_data)

    def start_recording(self):
        if not self.is_recording:
            self.recording_folder = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
            os.makedirs(self.recording_folder)
            self.is_recording = True
            self.start_recording_button.setEnabled(False)
            self.stop_recording_button.setEnabled(True)
            self.start_table_data_saving()
            self.start_video_recording()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.start_recording_button.setEnabled(True)
            self.stop_recording_button.setEnabled(False)
            self.stop_table_data_saving()
            self.stop_video_recording()

    def start_table_data_saving(self):
        if not self.table_timer.isActive():
            self.table_timer.start(1000)

    def stop_table_data_saving(self):
        if self.table_timer.isActive():
            self.table_timer.stop()

    def start_video_recording(self):
        if self.capture is not None and self.capture.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            filename = os.path.join(self.recording_folder, 'video.avi')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

    def stop_video_recording(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

    def show_graph(self):
        selected_index = -1
        for index, radio_button in enumerate(self.radio_buttons):
            if radio_button.isChecked():
                selected_index = index + 2
                break

        if selected_index == -1:
            QMessageBox.warning(self, "Warning", "Please select a column.")
            return

        header = self.table.horizontalHeaderItem(selected_index).text()
        data = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, selected_index)
            if item is not None and item.text().isdigit():
                data.append(int(item.text()))

        if len(data) < 2:
            QMessageBox.warning(self, "Warning", "Not enough data points to plot.")
            return

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
