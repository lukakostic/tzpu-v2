#import MySQLdb
# from mysql.connector import Error
import pandas as pd
#from MySQLdb._exceptions import Error

from utils.Proprerties import Properties
from datetime import datetime
import json

class DatabaseUtils:
    fileWrites = {
        "LOGS/Events.csv":"",
        "LOGS/Simulation.csv":"",
        "LOGS/Properties.csv":"",
        "LOGS/Important.txt":""
    }
    def __init__(self):
        pass
    def clear(self):
        DatabaseUtils.fileWrites = {
            "LOGS/Events.csv":"",
            "LOGS/Simulation.csv":"",
            "LOGS/Properties.csv":"",
            "LOGS/Important.txt":""
        }
    def WriteEvent(self, event_type:str,simulation_uuid:str,user_id:str,timestamp:str,duration:str):
        self.write("LOGS/Events.csv",f"{simulation_uuid}, {event_type}, User:{user_id}, Time:{timestamp}, Value:{duration}\n")
    def WriteSimulation(self, simulation_uuid:str):
        self.write("LOGS/Simulation.csv",f"{simulation_uuid}\n")
    def WriteProperties(self, simulation_uuid:str, type_:str, value:str):
        self.write("LOGS/Properties.csv",f"{simulation_uuid}, {type_}, {value}\n")
        
    def WriteImportant(self, txt:str, preTxt:str="",toPrint=False):
        if(type(txt)==bool): txt = "true" if txt else "false"
        if(type(txt)==list): txt = json.dumps(txt)
        if(preTxt == None):
            self.write("LOGS/Important.txt",f"{txt}\n")
        else:
            self.write("LOGS/Important.txt",f"\"{preTxt}\":{txt},\n")
        if toPrint: print(f"{preTxt}{txt}")
        
    def write(self, file,str_):
        #m = {'E':"Events.csv",'S':"Simulation.csv",'P':"Properties.csv"}
        #name = m[file]
        #if(name is None): name=file
        DatabaseUtils.fileWrites[file] += str_
        
        #print(self.fileWrites[file])
        #with open(file, "a") as myfile:
        #    myfile.write(str_)
    def writeAll(self):
        print("EEEEEEEEEEEEEEEEEEEEEEE")
        #print(self.fileWrites["LOGS/Events.csv"])
        for file,str_ in self.fileWrites.items():
            print("#######################")
            #print(str_)
            if file=="LOGS/Important.txt": file = f"LOGS/Important{Properties.IMPORTANT_TXT_SUFFIX}.txt"
            with open(file, "a") as myfile:
                myfile.write("\n" + str_)
    
    def log_event(self, event_type, user_id, time, duration):
        print("EVENT")
        print(event_type)
        # self.execute_query(
        #     "INSERT INTO Events (EVENT_TYPE,SIMULATION_UUID,USER_ID,TIMESTAMP,DURATION) VALUES (%s,%s,%s,%s,%s)",
        #     (event_type, Properties.SIMULATION_UUID, user_id, time, duration))
        self.WriteEvent(event_type, Properties.SIMULATION_UUID, user_id, time, duration)

    def log_simulation_start(self):
        #self.execute_query("INSERT INTO Simulation (UUID) VALUES (%s)", [Properties.SIMULATION_UUID])
        self.WriteSimulation(Properties.SIMULATION_UUID)
        self.log_simulation_parameters()

    def log_simulation_end(self):
        if self.broker is None:
            return

        self.log_event("TOTAL USER", None, None, Properties.USER_COUNT)

        pass

    def log_simulation_parameters(self):
        for name, value in Properties.get_parameters():
            # self.execute_query("INSERT INTO Properties (SIMULATION_UUID,TYPE,VALUE) VALUES (%s,%s,%s)",
            #                    (Properties.SIMULATION_UUID, name, value))
            self.WriteProperties(Properties.SIMULATION_UUID, name, value)

    def get_all_simulation_with_prop(self):
        return []
        return self.execute_simple_select_query("Select * FROM Simulation"
                                         " LEFT JOIN Properties"
                                         " ON Simulation.UUID = Properties.SIMULATION_UUID")

    def get_all_simulations_uuids(self):
        return []
        return self.execute_simple_select_query("Select * FROM Simulation")
    
    def get_props_for_simulation_uuid(self, simulation_uuid):
        return []
        return self.execute_select_query("Select * FROM Properties where SIMULATION_UUID=%s",[simulation_uuid])

    def get_data_for_simulation(self, simulation_uuid, event_type):
        return []
        return self.execute_select_query("Select * FROM Events where SIMULATION_UUID=%s AND EVENT_TYPE=%s", (simulation_uuid,event_type))