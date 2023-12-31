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

main = tk.Tk()
main.title("Simulation")
main.config(bg="#fff")
top_frame = tk.Frame(main)
top_frame.pack(side=tk.TOP, expand=False)
canvas = tk.Canvas(main, width=1300, height=350, bg="white")
canvas.pack(side=tk.TOP, expand=False)


def create_clock(environment):
    while True:
        yield environment.timeout(1)
        graph.tick(environment.now)


def start_simulation(env: RealtimeEnvironment, broker, user_scheduler):
    user_id = 1
    next_person_id = 0
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
