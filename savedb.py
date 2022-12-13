import sqlite3

class SaveToDataBase():
    def __init__(self):
        """Inicia a conexão com o banco de dados"""
        self.db_name = ""
        self.sql_msg = ""
        try:
            self.db_connection = sqlite3.connect('db.sqlite3')
            self.is_db_connected = True
            self.sql_msg = "Conexão com banco de dados realizada"
        except Exception as e:
            self.db_connection = None
            self.is_db_connected = False
            self.sql_msg = str(e)
    
    def status_db(self):
        """Retorna mensagens do DB e informa se está online"""
        return (self.is_db_connected, self.sql_msg)

    def check_addr(self, cursor, addr):
        cursor.execute("SELECT id FROM controle_opd_dispmodel WHERE name = ?", (addr,))
        data = cursor.fetchone()
        if data is None:
            self.sql_msg = "Dispositivo não cadastrado no banco de dados"
            return None
        else:
            return data[0]

    def save_row(self, data):
        """Salva uma nova linha no banco de dados"""
        if self.is_db_connected:
            try:            
                cursor = self.db_connection.cursor()

                addr = self.check_addr(cursor, data[4])
                if addr:
                    sqlite_insert_query = """INSERT INTO controle_opd_reportmodel
                                        (status, bits, horario, timestamp, addr_id) 
                                        VALUES 
                                        (?,?,?,?,?)"""

                    values = (data[0], data[1], data[2], data[3], addr)
                    count = cursor.execute(sqlite_insert_query, values)
                    self.db_connection.commit()
                    cursor.close()

            except sqlite3.Error as error:
                self.sql_msg = "Falha ao inserir nova linha no banco de dados: " + str(error)

    def close_dbconnection(self):
        """Fecha a conexão com o banco de dados"""
        if self.db_connection:
            self.db_connection.close()
            self.sql_msg = "Conexão com banco de dados fechada"