import uuid

from matplotlib.pyplot import margins
from simpy import RealtimeEnvironment

from entities.Broker import Broker
from entities.BrokerNoPreparing import BrokerNoPreparing
from entities.BrokerPrepareWhenZero import BrokerPrepareWhenZero
from entities.EventType import EventType
from entities.ResourceProvider import ResourceProvider
from entities.User import User
from entities.UserScheduler import UserScheduler
from utils.Analytics import Analytics
from utils.Graphs import Graphs
from utils.DatabaseUtils import DatabaseUtils
from utils.DisplayLog import DisplayLog
from utils.Proprerties import Properties
from utils.Options import Options

import simpy
import json
import time
import tkinter as tk

import numpy as np
import random
import sys

from datetime import datetime
#import threading
import os

SEED = 42
ui = False    #ovde dal hoces UI

_arrival_pattern = None
_broker_choice = None
_initial_wave = None
#_sla = None
_resurs_mean = None
_resurs_std = Options.RESOURCE_PREPARE_TIME_STD_OPTS
_set_raspodela = None
pocetne_vrednosti = [0, 0, 0, 0, True] #mean, arrival, broker, set, initial

_single_run = False
one_important_txt = False

_i_ = 0
args = list(map(lambda x: x.lower(), sys.argv[1:]))
while _i_ < len(args):
    if(args[_i_]=="seed"):
        SEED = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="u" or args[_i_]=="ui"):
        ui = ((args[_i_+1])[0]=="t" or (args[_i_+1])[0]=="y" or (args[_i_+1])[0]=="true")
        _i_+=1
    elif(args[_i_]=="i" or args[_i_]=="iw" or args[_i_]=="initial_wave"):
        _initial_wave = ((args[_i_+1])[0]=="t" or (args[_i_+1])[0]=="y" or (args[_i_+1])[0]=="true")
        _i_+=1
    elif(args[_i_]=="one_txt"):
        one_important_txt = True
    elif(args[_i_]=="one_txt_f"):
        one_important_txt = False
    elif(args[_i_]=="e" or args[_i_]=="exit"):
        _single_run = True
    elif(args[_i_]=="broker" or args[_i_]=="b"):
        _broker_choice = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="arrival" or args[_i_]=="a"):
        _arrival_pattern = int(args[_i_+1])
        _i_+=1
    # elif(args[_i_]=="sla" or args[_i_]=="s"):
    #     _sla = float(args[_i_+1])
    #     _i_+=1
    elif(args[_i_]=="set" or args[_i_]=="s_r"):
        _set_raspodela = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="resurs_mean" or args[_i_]=="r_m"):
        _resurs_mean = float(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="resurs_std" or args[_i_]=="r_s"):
        _resurs_std = float(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="ready_count" or args[_i_]=="r_c"):
        Properties.READY_COUNT = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="max_available_resources" or args[_i_]=="m_a_r"):
        Properties.MAX_AVAILABLE_RESOURCES = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="critical_utilisation_percent" or args[_i_]=="c_u_p"):
        Properties.CRITICAL_UTILISATION_PERCENT = float(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="resource_add_number" or args[_i_]=="r_a_n"):
        Properties.RESOURCE_ADD_NUMBER = int(args[_i_+1])
        _i_+=1
    else:
        print(f"Bad argument: {args[_i_]}")
        sys.exit()
    _i_+=1




main = None
graph = None
user_scheduler = None
database = None
analytics = None
canvas = None
log = None
if ui:
    main = tk.Tk()
    main.title("Simulation")
    main.config(bg="#fff")
    top_frame = tk.Frame(main)
    top_frame.pack(side=tk.TOP, expand=False)
    canvas = tk.Canvas(main, width=1300, height=350, bg="white")
    canvas.pack(side=tk.TOP, expand=False)

############################################
# def rnd(tp,idx=None):
#     return random.choice(tp) if(idx==None) else tp[idx]
# # Tp
# Properties.RESOURCE_PREPARE_TIME_MEAN = random.uniform(0.5,8)
# Properties.RESOURCE_PREPARE_TIME_STD = random.uniform(0.1,0.3)
# # SLA kriterijumi
# Properties.SLA = rnd((0.1, 0.5, 1, 1.5))
# # arrival pattern

# if(arrival_pattern == None):
#     print("Choose arrival pattern option (1, 2, 3)")
#     Properties.ARRIVAL_PATTERN = int(input())
# else:
#     Properties.ARRIVAL_PATTERN = arrival_pattern

# if(broker_choice == None):
#     print("Choose broker option (1, 2, 3) "
#         "1=Broker(CriticalUserPercent) "
#         "2=PrepareWhenZero "
#         "3=NoPreparing")
#     Properties.BROKER_TYPE = int(input())
# else:
#     Properties.BROKER_TYPE = broker_choice

# if(initial_wave == None):
#     print("Is initial wave known (y/N)")
#     y_n = input()
#     if y_n == "y" or y_n == "Y":
#         Properties.INITIAL_WAVE_KNOWN = True
#     else:
#         Properties.INITIAL_WAVE_KNOWN = False
# else:
#     Properties.INITIAL_WAVE_KNOWN = initial_wave

## option 1
##Properties.USER_COUNT = 300
##Properties.NEXT_LOGIN_MEAN = rnd((90,120))
##Properties.USERS_PER_LOGIN_MEAN = rnd((20,35))

## option 2
Properties.USER_COUNT = 100  # 300
#### T = 0
##Properties.USERS_PER_LOGIN_MEAN = rnd((20,35,100))
#### T>0
##Properties.USERS_PER_LOGIN_MEAN = rnd((3,5,8))

## option 3
#### csv = xlsx ?
# usage time
#### xlsx     - ovde se ucitavaju raspodele one
# aspekti
## poznatost T=0
#### option 1
#### option 2
## broker algoritam
#### Broker
#### BrokerPrepareWhenZero
#### BrokerNoPreparing
# kriterijumi optimizacije
## option 1:  ukupno vreme resursa min
## option 2:  pool size min

############################################

DONE = True

def create_clock(environment):
    while not DONE:
        yield environment.timeout(1)
        if ui and graph:
            graph.tick(environment.now)


def start_simulation(env: RealtimeEnvironment, broker, user_scheduler,opcije):
    Properties.SIMULATION_UUID = str(uuid.uuid4())
    print(Properties.SIMULATION_UUID)

    user_id = 1
    next_person_id = 0

    database.WriteImportant(f"\n{'{'}\n\"id\":\"{Properties.SIMULATION_UUID}\",\"time\":\"{datetime.now()}\",",None)
    database.WriteImportant(opcije,"opcije")
    database.WriteImportant(SEED,"SEED")
    #database.WriteImportant(Properties.SLA,"SLA")
    database.WriteImportant(Properties.ARRIVAL_PATTERN,"ARRIVAL_PATTERN")
    database.WriteImportant(Properties.INITIAL_WAVE_KNOWN,"INITIAL_WAVE_KNOWN")
    database.WriteImportant(Properties.BROKER_TYPE,"BROKER_TYPE")
    database.WriteImportant(Properties.READY_COUNT,"READY_COUNT")
    database.WriteImportant(Properties.MAX_AVAILABLE_RESOURCES,"MAX_AVAILABLE_RESOURCES")
    database.WriteImportant(Properties.CRITICAL_UTILISATION_PERCENT,"CRITICAL_UTILISATION_PERCENT")
    database.WriteImportant(Properties.RESOURCE_ADD_NUMBER,"RESOURCE_ADD_NUMBER")
    database.WriteImportant(Properties.SET_RASPOREDA,"SET_RASPOREDA")
    database.WriteImportant(Properties.RESOURCE_PREPARE_TIME_MEAN,"RESOURCE_PREPARE_TIME_MEAN")
    database.WriteImportant(Properties.RESOURCE_PREPARE_TIME_STD,"RESOURCE_PREPARE_TIME_STD")
    database.WriteImportant(Properties.USERS_PER_LOGIN_MEAN,"USERS_PER_LOGIN_MEAN")
    database.WriteImportant(Properties.NEXT_LOGIN_MEAN,"NEXT_LOGIN_MEAN")
    database.WriteImportant(Properties.NEXT_LOGIN_STD,"NEXT_LOGIN_STD")
    database.WriteImportant(Properties.USER_COUNT,"USER_COUNT")
    database.WriteImportant(user_scheduler.INTER_ARRIVAL_TIMES,"INTER_ARRIVAL_TIMES")
    database.WriteImportant(user_scheduler.USERS_NUMBER,"USERS_NUMBER")
    database.WriteImportant(user_scheduler.USAGE_TIME,"USAGE_TIME")
    database.WriteImportant(user_scheduler.TIME_BETWEEN_LOGINS,"TIME_BETWEEN_LOGINS")

    ## ako je poznato T = 0 i intenzitet inicijalnog udara

    if Properties.INITIAL_WAVE_KNOWN:
        broker.prepare_more_resources(env, user_scheduler.USERS_NUMBER[-1])


    while len(user_scheduler.INTER_ARRIVAL_TIMES) > 0 and len(user_scheduler.USERS_NUMBER) > 0:

        #print("XXXXXXXXXXXXXXX")
        # unapred kreirati vektor sa vremenma dolaska, zadrzavanja i broja ljudi koji dodju
        next_arrival = user_scheduler.INTER_ARRIVAL_TIMES.pop()
        users_number = user_scheduler.USERS_NUMBER.pop()


        # Wait for the bus
        if ui:
            log.next_arrival(next_arrival)
        yield env.timeout(next_arrival)
        if ui:
            log.arrived(users_number)

        # self.analytics.register_user_login() below is for reporting purposes only
        database.log_event(EventType.USER_LOGIN.value, None, env.now, users_number)
        for user in range(users_number):
            user = User("user", user_id)
            user_id += 1
            env.process(broker.user_login(user))

            yield env.timeout(user_scheduler.TIME_BETWEEN_LOGINS.pop())


    database.WriteImportant(graph.avg_wait(graph.utilization),"avg_utilization ")
    database.WriteImportant(graph.avg_wait(graph.wait_for_resource),"avg_wait ")
    database.WriteImportant(broker.analytics.SLA1_broke,"SLA1_broke ")
    database.WriteImportant(broker.analytics.SLA2_broke,"SLA2_broke ")
    database.WriteImportant(broker.analytics.SLA3_broke,"SLA3_broke ")
    database.WriteImportant(broker.analytics.SLA4_broke,"SLA4_broke ")
    database.WriteImportant("},",None)
    
    env.process(broker.end_process())
    database.writeAll()
    database.clear()
    print("DONE !!!!!!!!!!!!!!!!!")
    DONE = True
    if ui:
        create_window()
        #input()
        main.destroy()
    #else:
    if _single_run: sys.exit()


def create_window(broker):
    t = tk.Toplevel(main)
    t.wm_title("Finished")
    l = tk.Label(t, text=f"Simulation uuid: {Properties.SIMULATION_UUID} \n"
    # f"Total users: {sum(user_scheduler.USERS_NUMBER)} \n"
                         f"Utilization: {broker.analytics.utilization} \n"
                         f"Resource count: {broker.resource_provider.get_resource_count()}\n")
                         #f"SLA brakes: {broker.analytics.SLA_broke}")
    l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
    button = tk.Button(t, text="Close", command=close)
    button.pack(side="top", padx=10, pady=10)


def close():
    main.destroy()


def test_option(opcije):
    global DONE, database, analytics, user_scheduler, graph, main, canvas, log
    DONE = False
    random.seed(SEED)
    np.random.seed(seed=SEED)
    if not one_important_txt:
        Properties.IMPORTANT_TXT_SUFFIX = json.dumps(opcije)

    print("###$$$$$$$~~~~~~~~~~~~~~~~~~~~~~~~~$$$$$$$###")
    print(f" RESOURCE_PREPARE_TIME_MEAN: {Properties.RESOURCE_PREPARE_TIME_MEAN}")
    print(f" RESOURCE_PREPARE_TIME_STD: {Properties.RESOURCE_PREPARE_TIME_STD}")
    #print(f" SLA: {Properties.SLA}")
    print(f" ARRIVAL_PATTERN: {Properties.ARRIVAL_PATTERN}")
    print(f" ARRIVAL_PATTERN: {Properties.ARRIVAL_PATTERN}")
    print(f"BROKER_TYPE: {Properties.BROKER_TYPE}")
    print(f"SET_RASPOREDA: {Properties.SET_RASPOREDA}")
    print(f"INITIAL_WAVE_KNOWN: {Properties.INITIAL_WAVE_KNOWN}")

    database = DatabaseUtils()
    database.clear()

    env = simpy.rt.RealtimeEnvironment(factor=(1.0 / Properties.TIME_SPEEDUP), strict=False)

    analytics = Analytics()

    user_scheduler = UserScheduler()

    user_scheduler.real_mod()
    database.log_simulation_start()
    
    log = None
    if ui:
        log = DisplayLog(canvas, 5, 20)
    graph = Graphs(canvas, main, analytics.utilization_percent, analytics.waits_for_getting,
                    analytics.arrivals)

    resource_provider = ResourceProvider(env)
    if Properties.BROKER_TYPE == 2:
        broker = BrokerPrepareWhenZero(log, resource_provider, user_scheduler, env)
    elif Properties.BROKER_TYPE == 3:
        broker = BrokerNoPreparing(log, resource_provider, user_scheduler, env)
    else:
        broker = Broker(log, resource_provider, user_scheduler, env)

    process = env.process(start_simulation(env, broker, user_scheduler,opcije))
    env.process(create_clock(env))

    if Properties.CONSTANT_USER_COUNT_ENABLED:
        env.run()
    else:
        env.run(until=Properties.SIMULATION_DURATION_MINUTES)

    if ui:
        main.mainloop()


def start_proc(opcije,ready_count,max_available_resources,critical_utilisation_percent,resource_add_number):
    #time.sleep(0.2)
    os.system(f"python3 main.py e r_m {opcije[0]} a {opcije[1]} b {opcije[2]} s_r {opcije[3]} i {opcije[4]} r_c {ready_count} m_a_r {max_available_resources} c_u_p {critical_utilisation_percent} r_a_n {resource_add_number}")

if _single_run == False:
    for tp_mean_opt in Options.RESOURCE_PREPARE_TIME_MEAN_OPTS[pocetne_vrednosti[0]:]:
        Properties.RESOURCE_PREPARE_TIME_MEAN = tp_mean_opt
        Properties.RESOURCE_PREPARE_TIME_STD = Options.RESOURCE_PREPARE_TIME_STD_OPTS
        for arrival_pat in range(pocetne_vrednosti[1], 3):
            Properties.ARRIVAL_PATTERN = arrival_pat
            if True:
                broker_type = 1
                #for broker_type in range(pocetne_vrednosti[2], 3):
                Properties.BROKER_TYPE = broker_type
                for set_raspodela in range(pocetne_vrednosti[3], 9):
                    Properties.SET_RASPOREDA = set_raspodela
                    opcije = [tp_mean_opt,arrival_pat,broker_type,set_raspodela,pocetne_vrednosti[-1]]
                    for max_available_resources in [50,100,150]:
                        for critical_utilisation_percent in [0.2,0.6,0.8]:
                            for ready_count in [10,30,50,100]:
                                if ready_count > max_available_resources: continue
                                for resource_add_number in [1,5,10,20]:
                                    if Properties.ARRIVAL_PATTERN == 2:
                                        if pocetne_vrednosti[-1]:
                                            opcije[-1] = True
                                            Properties.INITIAL_WAVE_KNOWN = True
                                            start_proc(opcije,ready_count,max_available_resources,critical_utilisation_percent,resource_add_number)
                                        opcije[-1] = False
                                        Properties.INITIAL_WAVE_KNOWN = False
                                        start_proc(opcije,ready_count,max_available_resources,critical_utilisation_percent,resource_add_number)
                                    else:
                                        start_proc(opcije,ready_count,max_available_resources,critical_utilisation_percent,resource_add_number)
                                    pocetne_vrednosti[-1] = True
                pocetne_vrednosti[3] = 0
            pocetne_vrednosti[2] = 0
        pocetne_vrednosti[1] = 0
else:
    opcije = [_resurs_mean,_arrival_pattern,_broker_choice,_set_raspodela,_initial_wave]
    Properties.RESOURCE_PREPARE_TIME_MEAN = _resurs_mean
    Properties.RESOURCE_PREPARE_TIME_STD = _resurs_std
    #Properties.SLA = _sla
    Properties.ARRIVAL_PATTERN = _arrival_pattern
    Properties.BROKER_TYPE = _broker_choice
    Properties.SET_RASPOREDA = _set_raspodela
    Properties.INITIAL_WAVE_KNOWN = _initial_wave
    test_option(opcije)




