from serial2file import ReadSerial
import sys
import serial.tools.list_ports
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, Qt

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pyQTfileName = resource_path("window.ui")
Ui_MainWindow, QtBaseClass = uic.loadUiType(pyQTfileName)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        #Botões
        self.btnStart.clicked.connect(self.start_reading)
        self.btnStop.clicked.connect(self.close_ports)
        self.btnRefresh.clicked.connect(self.com_ports)

        self.com_ports()
        list_baud = ['', '2400', '4800', '9600', '14400', '19200', '115200']
        #UI elements    
        self.btnRefresh.setText('\u267A') #unicode pra mostrar icone de refresh    
        self.box_baud.clear()        
        self.box_baud.addItems(list_baud)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setAlignment(Qt.AlignCenter)

        #Status/controle
        self.com_var = None
        self.status = False

        #timer
        self.timer_update = QTimer()
        self.start_timer()        
    
    def com_ports(self):
        """Verifica as comports disponiveis e atualiza o ComboBox"""
        listP = serial.tools.list_ports.comports()
        connected = [""]
        for element in listP:
            connected.append(element.device)

        self.box_com.clear()
        self.box_com.addItems(connected)

    def close_ports(self):
        """Fecha o programa"""
        self.status = False        
        if self.com_var:
            self.com_var.close_port()
            self.com_var = None
        #UI elements 
        self.progressBar.setValue(0)
        self.label_status.setStyleSheet("background-color: indianred")

    def start_reading(self):        
        """O Arquivo txt gerado deve ser aberto usando notepad++
        para facilitar a visualização de caracteres epesciais, i.i, ACK, EOF, etc"""
        if "COM" in self.box_com.currentText() and self.box_baud.currentText() != '':
            self.com_var = ReadSerial(self.box_com.currentText(), self.box_baud.currentText())  
            self.status = True
            #UI elements       
            self.label_status.setStyleSheet("background-color: lightgreen")            
    
    def receiving_status(self):  
        """Verifica se existe dados na serial e plota via progressbar
        o numero de bytes e indica que está recebendo"""
        if self.com_var:
            stat, size, error = self.com_var.receiving_status()
            #UI elements 
            if stat:
                self.progressBar.setFormat(f'{size} Bytes')
                self.progressBar.setValue(50)
                self.progressBar.setValue(100)
            else:
                self.progressBar.setFormat(f'0 Bytes')
                self.progressBar.setValue(0)
            if error:
                self.txtError.setText(error)
            else: 
                self.txtError.setText("")

    def closeEvent(self, event):
        """Fecha o programa"""
        if self.status:
            self.close_ports()        
        event.accept()     

    def start_timer(self):
        self.timer_update.timeout.connect(self.receiving_status)
        self.timer_update.stop()
        self.timer_update.start(50)   
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    
    window.show()
    sys.exit(app.exec_())
