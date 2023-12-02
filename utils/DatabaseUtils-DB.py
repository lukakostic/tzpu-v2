#import MySQLdb
# from mysql.connector import Error
import pandas as pd
from MySQLdb._exceptions import Error

from utils.Proprerties import Properties


class DatabaseUtils:
    def __init__(self):
        self.connection = self.create_server_connection("remotemysql.com", "d7nGU51E4c", "iqiyEKUAlU", "d7nGU51E4c")

    @staticmethod
    def create_server_connection(host_name, user_name, user_password, database):
        connection = None
        try:
            """
            connection = MySQLdb.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=database
            )"""
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection

    def execute_simple_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            print(cursor._executed)
            self.connection.commit()
            # print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

    def execute_simple_select_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            # print(cursor._executed)

            return cursor.fetchall()
            # print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

    def execute_select_query(self, query, values):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values)
            # print(cursor._executed)

            return cursor.fetchall()
            # print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

    def execute_query(self, query, values):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values)
            print(cursor._executed)
            self.connection.commit()
            # print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

    def log_event(self, event_type, user_id, time, duration):
        self.execute_query(
            "INSERT INTO Events (EVENT_TYPE,SIMULATION_UUID,USER_ID,TIMESTAMP,DURATION) VALUES (%s,%s,%s,%s,%s)",
            (event_type, Properties.SIMULATION_UUID, user_id, time, duration))

    def log_simulation_start(self):
        self.execute_query("INSERT INTO Simulation (UUID) VALUES (%s)", [Properties.SIMULATION_UUID])
        self.log_simulation_parameters()

    def log_simulation_end(self):
        if self.broker is None:
            return

        self.log_event("TOTAL USER", None, None, Properties.USER_COUNT)

        pass

    def log_simulation_parameters(self):
        for name, value in Properties.get_parameters():
            self.execute_query("INSERT INTO Properties (SIMULATION_UUID,TYPE,VALUE) VALUES (%s,%s,%s)",
                               (Properties.SIMULATION_UUID, name, value))

    def get_all_simulation_with_prop(self):
        return self.execute_simple_select_query("Select * FROM Simulation"
                                         " LEFT JOIN Properties"
                                         " ON Simulation.UUID = Properties.SIMULATION_UUID")

    def get_all_simulations_uuids(self):
        return self.execute_simple_select_query("Select * FROM Simulation")
    
    def get_props_for_simulation_uuid(self, simulation_uuid):
        return self.execute_select_query("Select * FROM Properties where SIMULATION_UUID=%s",[simulation_uuid])

    def get_data_for_simulation(self, simulation_uuid, event_type):
        return self.execute_select_query("Select * FROM Events where SIMULATION_UUID=%s AND EVENT_TYPE=%s", (simulation_uuid,event_type))