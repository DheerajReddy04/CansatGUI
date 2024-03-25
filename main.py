import sys
import time
import random
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QGridLayout, QDial, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
import matplotlib.figure as Figure
from AnalogGaugeWidget import AnalogGaugeWidget

# Initialize the serial connection to the Arduino
ser = serial.Serial('COM5', baudrate=9600, timeout=1)

class RealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.graph_canvas = []
        self.graph_figures = []
        #self.dials = []

        self.gauges = []          #Testing
         
        #self.dial_labels = []
        self.gauge_labels = []


        self.init_ui()

        # Create a QTimer to update the dials, labels, and graphs every 2 seconds
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(1000)

    def init_ui(self):
        self.setWindowTitle("Real-Time Data Display")
        self.setWindowState(Qt.WindowFullScreen)  # Set to full screen
        self.central_widget = QWidget(self)
        self.setCentralWidget
        (self.central_widget)
        self.layout = QGridLayout(self.central_widget)
        self.setStyleSheet("background-color: purple;")   # TO CHANGE THE BACKGROUND COLOUR OF THE ENTIRE GUI

        # Initialize class attributes
        #self.create_dial("Temperature", 0, 0, 'orange', 10, 40)
        #self.create_dial("Humidity", 0, 1, 'white', 0, 80)
        #self.create_dial("Pressure", 0, 2, 'green', 0, 1000)
        #self.create_graph("NO2", 1, 0, 'NO2', 'b')cd
        #self.create_graph("NH3", 1, 1, 'NH3', 'g')
        #self.create_graph("CO", 1, 2, 'CO', 'r')
        #self.create_graph("XYZ",1, 3, 'XYZ', 'violet')

        #Testing
        self.create_gauge("Temperature", 0, 0, "℃", 'orange', 10, 40)
        self.create_gauge("Humidity", 0, 1, "%", 'white', 0, 80)
        self.create_gauge("Air Quality", 0, 2, "kPa", 'green', 0, 100)
        self.create_graph("NO2", 1, 0, 'NO2', 'b')
        self.create_graph("NH3", 1, 1, 'NH3', 'g')
        self.create_graph("CO", 1, 2, 'CO', 'r')
        #self.create_graph("XYZ",1, 3, 'XYZ', 'violet')

        self.start_button = self.create_button("Start", self.start_plotting, 2, 0)
        self.stop_button = self.create_button("Stop", self.stop_plotting, 2, 3)

        self.start_button.setStyleSheet(f"background-color: white;")
        self.stop_button.setStyleSheet(f"background-color: white;")


        self.x_data = []
        self.y_temp_data = []
        self.y_humidity_data = []
        self.y_airquality_data = []   #changed from pressure to airqulaity
        self.y_no2_data = []
        self.y_nh3_data = []
        self.y_co_data = []
        #self.y_xyz_data = []

        self.plotting = False  # Variable to control plotting
        self.timer = None  # Initialize timer
    #create_dial to create_gauge
    def create_gauge(self, name, row, col, unit, color ='black', min_value=None, max_value=None):
        #dial = QDial(self)
        gauge = AnalogGaugeWidget(self)

        #dial.setNotchesVisible(True)
        #gauge.setNotchesVisible(True)

        #dial.setFixedSize(450, 450)  # Adjust the size as desired
        gauge.setFixedSize(450, 450)  # Adjust the size as desired

        gauge.setGaugeTheme(6)   #To change the gauge theme  8 yellow 12 light yellow 15 green 17 blue 21 purple0
        
        gauge.units = unit #to change the units inside the gauge
        #gauge.scalaCount = 10 #to change the number of scales

        #dial.setStyleSheet(f"background-color: {color}; QDial::indicator {{ background-color: white; }}")  # Set the indicator color to white
        gauge.setStyleSheet(f"background-color: {color}; QDial::indicator {{ background-color: white; }}")  # Set the indicator color to white
        #self.layout.addWidget(dial, row, col)   #COMMENTING FOR TIME BEING
        label = QLabel(f'{name}: 0',self)  # added self inside
        label.setStyleSheet("font-weight: bold; font-size: 30px;")  # Set label font to bold and increase font size(added recently)

        #ADDING FOR TIME BEING
        #dial_label_layout = QVBoxLayout()  # Create a vertical layout
        #dial_label_layout.addWidget(dial, alignment=Qt.AlignHCenter)
        #dial_label_layout.addWidget(label, alignment=Qt.AlignHCenter)

        #ADDING FOR TIME BEING
        gauge_label_layout = QVBoxLayout()  # Create a vertical layout
        gauge_label_layout.addWidget(gauge, alignment=Qt.AlignHCenter)
        gauge_label_layout.addWidget(label, alignment=Qt.AlignHCenter)

        #ADDING FOR TIME BEING(2)
        #container_widget = QWidget(self)  # Create a container widget to hold the dial and label
        #container_widget.setLayout(dial_label_layout)

        #ADDING FOR TIME BEING(2)
        container_widget = QWidget(self)  # Create a container widget to hold the dial and label
        container_widget.setLayout(gauge_label_layout)

        # Set a fixed size for the container widget (adjust the values as needed)
        #container_widget.setFixedSize(500, 500)

        # Set the size policy for the container widget
        container_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        #ADDING FOR TIME BEING 
        self.layout.addWidget(container_widget, row, col, alignment=Qt.AlignHCenter)  # Center-align the container widget      
        #self.layout.addWidget(label, row + 1, col)

        #if min_value is not None and max_value is not None:
        #    dial.setMinimum(min_value)
        #    dial.setMaximum(max_value)

        if min_value is not None and max_value is not None:
            gauge.setMinValue(min_value)
            gauge.setMaxValue(max_value)

        # Store references to the dial and label for updating
        #self.dials.append(dial)
        #self.dial_labels.append(label)

        # Store references to the dial and label for updating
        self.gauges.append(gauge)
        #self.dial_labels.append(label)
        self.gauge_labels.append(label)

    def create_graph(self, name, row, col, ylabel, color, background_color='wheat'):
        # Create a QWidget with the desired background color
        background_widget = QWidget()
        background_widget.setStyleSheet(f"background-color: {background_color};")

        # Create a Figure and FigureCanvas as before
        figure, ax = plt.subplots()
        canvas = FigureCanvas(figure)

        # Add the FigureCanvas to the background QWidget
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        background_widget.setLayout(layout)

        self.layout.addWidget(background_widget, row + 2, col)

        ax.set_facecolor('wheat')   # TO CHANGE THE COLOUR OF THE GRAPH(PLOTTING AREA)

        ax.set_xlabel('Time')
        ax.set_ylabel(ylabel)
        ax.set_title(f'{name} Data')
        ax.grid(True, linestyle='--')
        ax.plot([], [], color=color, label=f'{name}')
        ax.legend()

        self.graph_canvas.append(canvas)
        self.graph_figures.append(figure)

    def create_button(self, text, callback, row, col):
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        self.layout.addWidget(button, row + 3, col)
        return button

    def start_plotting(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.plotting = True
        self.x_data = []  # Reset x_data
        self.y_temp_data = []
        self.y_humidity_data = []
        self.y_airquality_data = []
        self.y_no2_data = []  # Reset NO2 data
        self.y_nh3_data = []  # Reset NH3 data
        self.y_co_data = []  # Reset CO data
        #self.y_xyz_data = []
        self.start_time = time.time()  # Record start time
        self.timer = self.startTimer(2000)  # Update every 2 seconds

    def stop_plotting(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.plotting = False
        if self.timer is not None:
            self.killTimer(self.timer)  # Stop the timer

    def timerEvent(self, event):
        if self.plotting:
            #data = ser.readline().decode().strip()   #remove if needed later

            try:
                data = ser.readline().decode('ascii', errors='ignore').strip()
            except UnicodeDecodeError:
            #Handle the error gracefully (e.g., print a message or log the error)
                data = ""


            temperature, humidity, airquality, no2, nh3, co = data.split(',')
            
            try:
                temperature = float(temperature)
                humidity = float(humidity)
                airquality = float(airquality)
            except ValueError:
                temperature = 0
                humidity = 0
                airquality = 0

            self.y_temp_data.append(temperature)
            self.y_humidity_data.append(humidity)
            self.y_airquality_data.append(airquality)

            # Simulate reading data (random values)
            
            #temperature = random.uniform(10, 40)
            #humidity = random.uniform(0, 80)
            #airquality = random.uniform(900, 1100)
            #no2 = random.uniform(0, 50)
            #nh3 = random.uniform(0, 100)
            #co = random.uniform(0, 500)
            #xyz = random.uniform(0,50)

            self.y_no2_data.append(no2)
            self.y_nh3_data.append(nh3)
            self.y_co_data.append(co)
            #self.y_xyz_data.append(xyz)

            current_time = time.time()
            elapsed_time = current_time - self.start_time
            self.x_data.append(elapsed_time)

            self.update_graph(0, self.x_data, self.y_no2_data)
            self.update_graph(1, self.x_data, self.y_nh3_data)
            self.update_graph(2, self.x_data, self.y_co_data)
            #self.update_graph(3, self.x_data, self.y_xyz_data)

            #Update the gauges with the new values
            self.update_gauges()

    def update_graph(self, index, x_data, y_data):
        ax = self.graph_figures[index].gca()
        ax.clear()
        ax.plot(x_data, y_data, color='b')
        ax.set_xlabel('Time')
        no2 = self.y_no2_data[-1]
        nh3 = self.y_nh3_data[-1]
        co = self.y_co_data[-1]
        ax.set_ylabel(['NO2', 'NH3', 'CO'][index])
        ax.set_title([f'NO2: {no2}', f'NH3: {nh3}', f'CO: {co}'][index] + ' Data')
        ax.grid(True, linestyle='--')
        self.graph_canvas[index].draw()

    def update_gauges(self):
        if len(self.gauges) > 0 and len(self.y_temp_data) > 0:
            temperature = int(self.y_temp_data[-1])  # Convert to integer
            humidity = int(self.y_humidity_data[-1])  # Convert to integer
            airquality = int(self.y_airquality_data[-1])
            self.gauges[0].setValue(temperature)
            self.gauges[1].setValue(humidity)
            self.gauges[2].setValue(airquality)

            # Update the labels for temperature and humidity
            #self.dial_labels[0].setText(f'Temperature: {temperature}')
            #self.dial_labels[1].setText(f'Humidity: {humidity}')
            #self.dial_labels[2].setText(f'Pressure: {pressure}')

            self.gauge_labels[0].setText(f'Temperature: {temperature}')
            self.gauge_labels[1].setText(f'Humidity: {humidity}')
            self.gauge_labels[2].setText(f'Air Quality: {airquality}')

    def update_data(self):
        self.update_gauges()

#REMOVE LINE 240 in AnalogGaugeWidget.py if needed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec_())