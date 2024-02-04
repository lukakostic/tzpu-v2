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

import simpy
import json
import tkinter as tk

import random

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
Properties.RESOURCE_PREPARE_TIME_STD = random.uniform(0.5,8)
# SLA kriterijumi
maxVremeSLA = rnd((0.1, 0.5, 1.5))
# arrival pattern

print("Choose arrival pattern option (1, 2, 3)")
Properties.ARRIVAL_PATTERN = int(input())

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

def create_clock(environment):
    while True:
        yield environment.timeout(1)
        graph.tick(environment.now)


def start_simulation(env: RealtimeEnvironment, broker, user_scheduler):
    user_id = 1
    next_person_id = 0

    ## ako je poznato T = 0 i intenzitet inicijalnog udara

    if Properties.INITIAL_WAVE_KNOWN:
        broker.prepare_more_resources(env, user_scheduler.USERS_NUMBER[-1])


    while len(user_scheduler.INTER_ARRIVAL_TIMES) > 0 and len(user_scheduler.USERS_NUMBER) > 0:

        # unapred lreirati vektor sa vremenma dolaska, zadrzavanja i broja ljudi koji dodju
        next_arrival = user_scheduler.INTER_ARRIVAL_TIMES.pop()
        users_number = user_scheduler.USERS_NUMBER.pop()


        # Wait for the bus
        log.next_arrival(next_arrival)
        yield env.timeout(next_arrival)
        log.arrived(users_number)

        # self.analytics.register_user_login() below is for reporting purposes only
        database.log_event(EventType.USER_LOGIN.value, None, env.now, users_number)
        for user in range(users_number):
            user = User("user", user_id)
            user_id += 1
            env.process(broker.user_login(user))

            yield env.timeout(user_scheduler.TIME_BETWEEN_LOGINS.pop())

    env.process(broker.end_process())

    create_window()
    database.writeAll()
    database.clear()
    # main.destroy()


def create_window():
    t = tk.Toplevel(main)
    t.wm_title("Finished")
    l = tk.Label(t, text=f"Simulation uuid: {Properties.SIMULATION_UUID} \n"
    # f"Total users: {sum(user_scheduler.USERS_NUMBER)} \n"
                         f"Utilization: {broker.analytics.utilization} \n"
                         f"Resource count: {broker.resource_provider.get_resource_count()}")
    l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
    button = tk.Button(t, text="Close", command=close)
    button.pack(side="top", padx=10, pady=10)


def close():
    main.destroy()


env = simpy.rt.RealtimeEnvironment(factor=(1.0 / Properties.TIME_SPEEDUP), strict=False)
Properties.SIMULATION_UUID = str(uuid.uuid4())
print(Properties.SIMULATION_UUID)

analytics = Analytics()
database = DatabaseUtils()
database.clear()
user_scheduler = UserScheduler()

user_scheduler.real_mod()
database.log_simulation_start()

log = DisplayLog(canvas, 5, 20)
graph = Graphs(canvas, main, analytics.utilization_percent, analytics.waits_for_getting,
               analytics.arrivals)
resource_provider = ResourceProvider(env)

broker = BrokerPrepareWhenZero(log, resource_provider, user_scheduler, env)
# broker = BrokerNoPreparing(log, resource_provider, user_scheduler, env)
# broker = Broker(log, resource_provider, user_scheduler, env)

process = env.process(start_simulation(env, broker, user_scheduler))
env.process(create_clock(env))

if Properties.CONSTANT_USER_COUNT_ENABLED:
    env.run()
else:
    env.run(until=Properties.SIMULATION_DURATION_MINUTES)

main.mainloop()
