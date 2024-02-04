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
import tkinter as tk

import numpy as np
import random
import sys


SEED = 42

random.seed(SEED)
np.random.seed(seed=SEED)

ui = False    #ovde dal hoces UI

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
def rnd(tp,idx=None):
    return random.choice(tp) if(idx==None) else tp[idx]
# Tp
Properties.RESOURCE_PREPARE_TIME_MEAN = random.uniform(0.5,8)
Properties.RESOURCE_PREPARE_TIME_STD = random.uniform(0.1,0.3)
# SLA kriterijumi
Properties.SLA = rnd((0.1, 0.5, 1, 1.5))
# arrival pattern

print("Choose arrival pattern option (1, 2, 3)")
Properties.ARRIVAL_PATTERN = int(input())

print("Choose broker option (1, 2, 3) "
      "1=Broker(CriticalUserPercent) "
      "2=PrepareWhenZero "
      "3=NoPreparing")
Properties.BROKER_TYPE = int(input())

print("Is initial wave known (y/N)")
y_n = input()
if y_n == "y" or y_n == "Y":
    Properties.INITIAL_WAVE_KNOWN = True
else:
    Properties.INITIAL_WAVE_KNOWN = False


## option 1
##Properties.USER_COUNT = 300
##Properties.NEXT_LOGIN_MEAN = rnd((90,120))
##Properties.USERS_PER_LOGIN_MEAN = rnd((20,35))

## option 2
Properties.USER_COUNT = 300
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

database = DatabaseUtils()
database.clear()

def create_clock(environment):
    while True:
        yield environment.timeout(1)
        if ui and graph:
            graph.tick(environment.now)


def start_simulation(env: RealtimeEnvironment, broker, user_scheduler):
    Properties.SIMULATION_UUID = str(uuid.uuid4())
    print(Properties.SIMULATION_UUID)

    user_id = 1
    next_person_id = 0

    database.WriteImportant(Properties.SLA,"SLA ")
    database.WriteImportant(Properties.ARRIVAL_PATTERN,"ARRIVAL_PATTERN ")
    database.WriteImportant(Properties.INITIAL_WAVE_KNOWN,"INITIAL_WAVE_KNOWN ")
    database.WriteImportant(Properties.BROKER_TYPE,"BROKER_TYPE ")
    database.WriteImportant(Properties.READY_COUNT,"READY_COUNT ")
    database.WriteImportant(Properties.MAX_AVAILABLE_RESOURCES,"MAX_AVAILABLE_RESOURCES ")
    database.WriteImportant(Properties.CRITICAL_UTILISATION_PERCENT,"CRITICAL_UTILISATION_PERCENT ")
    database.WriteImportant(Properties.RESOURCE_ADD_NUMBER,"RESOURCE_ADD_NUMBER ")
    database.WriteImportant(Properties.SET_RASPOREDA,"SET_RASPOREDA ")
    database.WriteImportant(Properties.RESOURCE_PREPARE_TIME_MEAN,"RESOURCE_PREPARE_TIME_MEAN ")
    database.WriteImportant(Properties.RESOURCE_PREPARE_TIME_MEAN,"RESOURCE_PREPARE_TIME_MEAN ")
    database.WriteImportant(Properties.RESOURCE_PREPARE_TIME_STD,"RESOURCE_PREPARE_TIME_STD ")
    database.WriteImportant(Properties.USERS_PER_LOGIN_MEAN,"USERS_PER_LOGIN_MEAN ")
    database.WriteImportant(Properties.NEXT_LOGIN_MEAN,"NEXT_LOGIN_MEAN ")
    database.WriteImportant(Properties.NEXT_LOGIN_STD,"NEXT_LOGIN_STD ")
    database.WriteImportant(Properties.USER_COUNT,"USER_COUNT ")
    database.WriteImportant(user_scheduler.INTER_ARRIVAL_TIMES,"INTER_ARRIVAL_TIMES ")
    database.WriteImportant(user_scheduler.USERS_NUMBER,"USERS_NUMBER ")
    database.WriteImportant(user_scheduler.USAGE_TIME,"USAGE_TIME ")
    database.WriteImportant(user_scheduler.TIME_BETWEEN_LOGINS,"TIME_BETWEEN_LOGINS ")

    ## ako je poznato T = 0 i intenzitet inicijalnog udara

    if Properties.INITIAL_WAVE_KNOWN:
        broker.prepare_more_resources(env, user_scheduler.USERS_NUMBER[-1])


    while len(user_scheduler.INTER_ARRIVAL_TIMES) > 0 and len(user_scheduler.USERS_NUMBER) > 0:

        print("XXXXXXXXXXXXXXX")
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
            print("USER_--------------------")

            yield env.timeout(user_scheduler.TIME_BETWEEN_LOGINS.pop())

    print("DONE111 !!!!!!!!!!!!!!!!!")
    database.WriteImportant(graph.avg_wait(graph.utilization),"avg_utilization ")
    database.WriteImportant(graph.avg_wait(graph.wait_for_resource),"avg_wait ")
    database.WriteImportant(broker.analytics.SLA_broke,"SLA_broke ")

    env.process(broker.end_process())
    database.writeAll()
    database.clear()
    print("DONE !!!!!!!!!!!!!!!!!")

    if ui:
        create_window()
        input()
        main.destroy()
    #else:
    sys.exit()


def create_window(broker):
    t = tk.Toplevel(main)
    t.wm_title("Finished")
    l = tk.Label(t, text=f"Simulation uuid: {Properties.SIMULATION_UUID} \n"
    # f"Total users: {sum(user_scheduler.USERS_NUMBER)} \n"
                         f"Utilization: {broker.analytics.utilization} \n"
                         f"Resource count: {broker.resource_provider.get_resource_count()}\n"
                         f"SLA brakes: {broker.analytics.SLA_broke}")
    l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
    button = tk.Button(t, text="Close", command=close)
    button.pack(side="top", padx=10, pady=10)


def close():
    main.destroy()


def test_option():
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

    process = env.process(start_simulation(env, broker, user_scheduler))
    env.process(create_clock(env))

    if Properties.CONSTANT_USER_COUNT_ENABLED:
        env.run()
    else:
        env.run(until=Properties.SIMULATION_DURATION_MINUTES)

    if ui:
        main.mainloop()

pocetne_vrednosti = [0, 0, 0, 0, 0, 0, True]

for tp_mean_opt in Options.RESOURCE_PREPARE_TIME_MEAN_OPTS[pocetne_vrednosti[0]:]:
    for tp_std_opt in Options.RESOURCE_PREPARE_TIME_STD_OPTS[pocetne_vrednosti[1]:]:
        for sla_opt in Options.SLA_OPTS[pocetne_vrednosti[2]:]:
            for arrival_pat in range(pocetne_vrednosti[3], 3):
                Properties.ARRIVAL_PATTERN = arrival_pat
                for broker_type in range(pocetne_vrednosti[4], 3):
                    Properties.BROKER_TYPE = broker_type
                    for set_raspodela in range(pocetne_vrednosti[5], 9):
                        Properties.SET_RASPOREDA = set_raspodela
                        if Properties.ARRIVAL_PATTERN == 2:
                            if pocetne_vrednosti[6]:
                                Properties.INITIAL_WAVE_KNOWN = True
                                test_option()
                            Properties.INITIAL_WAVE_KNOWN = False
                            test_option()
                        else:
                            test_option()
                        pocetne_vrednosti[6] = True
                    pocetne_vrednosti[5] = 0
                pocetne_vrednosti[4] = 0
            pocetne_vrednosti[3] = 0
        pocetne_vrednosti[2] = 0
    pocetne_vrednosti[1] = 0





