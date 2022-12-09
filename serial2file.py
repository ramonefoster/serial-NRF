import serial
import serial.tools.list_ports
import threading
import datetime
import time

class ReadSerial(threading.Thread):
    def __init__(self, porta, baud):  
        """Inicia leitura Serial
        """  
        self.control_var = ""
        self.receiving_flag = False  
        self.byte_size = 0
        self.close_var = False  
        self.txt_error = ""      
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
                self.ser.open()
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.port_name = self.ser.name
            except Exception as e:
                print(e)
        self.t_thread = threading.Thread(target = self.read)
        self.t_thread.start()
    
    def start(self):
        """Start threar que re em loop a COM"""
        if self.ser.is_open == False:
            try:
                self.ser.open()
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.port_name = self.ser.name
            except Exception as e:
                self.txt_error = str(e) 
            else:
                self.txt_error = ""    
    
    def read(self):
        while (True):
            if self.close_var:
                break
            data_str = ''
            try:
                resp = self.ser.in_waiting
            except Exception as e:
                #tenta reabrir COM  
                self.ser.close()  
                self.start()
                time.sleep(5)
                self.txt_error = str(e)
            else:
                self.txt_error = ""
            if (resp > 0): 
                self.receiving_flag = True  
                self.byte_size = resp              
                while(not '\n' in data_str):     
                    try:             
                        data_str += self.ser.read().decode()                        
                    except Exception as e:
                        self.ser.flush()
                        self.txt_error = str(e)
                    else:
                        self.txt_error = ""
                x = data_str.split("\t")
                if self.control_var != x[0:5]:
                    self.control_var = x[0:5]
                    datevalue = datetime.date.today()
                    hours = datetime.datetime.now().strftime("%H")
                    minute = datetime.datetime.now().strftime("%M")
                    seconds = datetime.datetime.now().strftime("%S")                
                    time_log = str(datevalue) + "\t"+ str(hours) + ":" + str(minute) + ":" + str(seconds)
                    with open(self.port_name+'_LOG.txt', 'a+') as datafile:
                        text = ""
                        for bit in x[0:5]:
                            text += bit + "\t"
                        wegStatus = ""
                        if (x[2]!="0" and x[2]!="1"):
                            wegStatus = "ERROR"
                        if (x[3]!="0" and x[3]!="1"):
                            wegStatus = "ERROR"
                        if (x[4]!="0" and x[4]!="1"):
                            wegStatus = "ERROR"

                        if x[0] == "1": 
                            wegStatus = "Abrindo"
                        if x[1] == "1": 
                            wegStatus = "Fechando"
                        datafile.write(time_log+'\t'+text+wegStatus+'\r')
                    
                    with open(self.port_name+'_LOG_FULLDATA.txt', 'a+') as datafile:
                        datafile.write(time_log+'\t'+data_str)
            else:
                self.receiving_flag = False
                self.byte_size = 0
            time.sleep(.003)
    
    def receiving_status(self):
        """Retorna o status da flag de recebimento e numero de bytes"""
        return (self.receiving_flag, self.byte_size, self.txt_error)
    
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

