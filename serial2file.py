import serial
import serial.tools.list_ports
import threading
import datetime

class ReadSerial(threading.Thread):
    def __init__(self, porta, baud):  
        """Inicia leitura Serial
        """  
        self.control_var = ""
        self.receiving_flag = False  
        self.close_var = False        
        self.ser = serial.Serial(
            port=porta,
            baudrate=baud,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2)
        self.ser.close()
        if self.ser.is_open == False:
            try:
                print("Openning RX-Indexer port")
                self.ser.open()
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.port_name = self.ser.name
            except Exception as e:
                print(e)
            self.t_thread = threading.Thread(target = self.read)
            self.t_thread.start()
    
    def read(self):
        while (True):
            if self.close_var:
                break
            data_str = ''
            resp = self.ser.in_waiting
            if (resp > 0): 
                self.receiving_flag = True  
                self.byte_size = resp              
                while(not '\n' in data_str):     
                    try:             
                        data_str += self.ser.read().decode()                        
                    except Exception as e:
                        print(str(e))
                x = data_str.split("\t")
                if self.control_var != x[3:8] and len(x)>3:
                    self.control_var = x[3:8]
                    hours = datetime.datetime.now().strftime("%H")
                    minute = datetime.datetime.now().strftime("%M")
                    seconds = datetime.datetime.now().strftime("%S")
                    time_log = str(hours) + ":" + str(minute) + ":" + str(seconds)
                    if x[3]=="1":
                        status=" [Abrindo] "
                    elif x[4]=="1":
                        status=" [Fechando] "
                    else:
                        status=""
                    with open(self.port_name+'_LOG.txt', 'a+') as datafile:
                        datafile.write(time_log+status+' - '+data_str)
            else:
                self.receiving_flag = False
                self.byte_size = 0
    
    def receiving_status(self):
        """Retorna o status da flag de recebimento e numero de bytes"""
        return (self.receiving_flag, self.byte_size)
    
    def close_port(self):
        """Fecha a porta COM e reseta as flags"""
        self.close_var = True
        self.byte_size = 0
        self.t_thread.join()
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.close()        
        self.control_var = ""
        self.receiving_flag = False

