import matplotlib.pyplot as plt
import csv
import tkinter as tk
import numpy as np
import math
# import scipy.interpolate.spline

from scipy.ndimage.filters import gaussian_filter1d

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from entities.EventType import EventType
from utils.DatabaseUtils import DatabaseUtils

database = DatabaseUtils()

def bar_graph():
    labels = ['1', '2', '3', '4', '5']
    men_means = [1.7, 2, 5, 6, 40]
    women_means = [0.7, 0.5, 1, 5, 25]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, men_means, width, label='Priprema na 0')
    rects2 = ax.bar(x + width / 2, women_means, width, label='Priprema unapred')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Srednje vreme čekanja')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

def bar_graph_event():
    labels = ['1', '2', '3', '4', '5']

    list1 = ["f6acac41-fb14-4d34-9673-c8c2ca67e65c",
             "7376577a-2467-4efa-bfd2-f3027ea0976c",
             "a220d849-7c5c-4b07-b1de-ae29eb0f0469",
             "586660a5-c01d-496a-97b0-e9a738227973",
             "c4a6ec38-c1ce-43a3-b8fb-01f419a62aa2"]

    list2 = ["a9713197-9ec5-462a-9d4b-ebd517e69694",
             "38d1b7f8-34f7-4ff5-91f6-f1a47bc0a5db",
             "0a08c856-1011-497c-a431-797e3c9b3e53",
             "dc526ae3-6714-4744-92a3-9510f936a967",
             "c418a15e-26a1-4427-8a7e-b0206f7eb513"]

    men_means = []
    women_means = []

    for el in list1:
        men_means.append(calculate_avg_utiliyation(el, EventType.SYSTEM_UTILIZATION.value))

    for el in list2:
        women_means.append(calculate_avg_utiliyation(el, EventType.SYSTEM_UTILIZATION.value))

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, men_means, width, label='Priprema na 0')
    rects2 = ax.bar(x + width / 2, women_means, width, label='Priprema unapred')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Upotrebljenost sistema')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

def calculate_avg_utiliyation(simulation_uuid, event_type):
    data = database.get_data_for_simulation(simulation_uuid, event_type)

    value_array = [row[5] for row in data]

    return sum(value_array)/len(value_array)

def bar_graph_optimal_case_vs_others():
    plt.suptitle('Standardni rad sistema')
    names = ['Priprema na 0', 'Priprema unapred', 'Optimalni sistem' ]

    list1 = ["f6acac41-fb14-4d34-9673-c8c2ca67e65c",
             "a9713197-9ec5-462a-9d4b-ebd517e69694",
             "7f3e151a-f9fc-4359-a23f-b54f8dadbc09"]
    values = []

    for el in list1:
        values.append(calculate_avg_utiliyation(el, EventType.USER_WAIT.value))

    plt.ylabel('Prosečno vreme čekanja')
    plt.bar(names, values)
    plt.show()

def get_resource_usage_graph(simulation_uuid, event_type):
    data = database.get_data_for_simulation(simulation_uuid, event_type)
    for d in data:
        print(d)

    time_array = [row[4] for row in data]
    value_array = [row[5] for row in data]

    if event_type == EventType.USER_LOGIN.value:
        value_array = [row[5] for row in data]


    if event_type == EventType.USER_WAIT.value:

        time_array = [row[4] for row in data]
        value_array = [row[5] for row in data]

        prop_string = ""
        max = 0
        avg_for_waiting = 0
        avg_for_waiting_count = 0
        avg = 0
        for value in value_array:
            if value>max:
                max = value
            if value>0:
                avg_for_waiting+=value
                avg_for_waiting_count+=1
            avg += value

        avg /= len(value_array)

        if avg_for_waiting_count>0:
            avg_for_waiting/=avg_for_waiting_count

        plt.suptitle('AVERAGE WAIT')
        names = ['Users who waited', 'All users']
        values = [avg_for_waiting,avg]

        plt.ylabel('Time')
        plt.bar(names,values)
        plt.show()

        # prop_string+="Max: "+ str(max)+"\n"
        # prop_string += "min: " + str(min) + "\n"
        # prop_string += "avg: " + str(avg) + "\n"
        #
        # main = tk.Tk()
        # main.title("Simulation")
        # top_frame = tk.Frame(main)
        # top_frame.pack(side=tk.TOP, expand=False)
        # l = tk.Label(top_frame, text=prop_string)
        # l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        # main.mainloop()

    # axes = plt.gca()
    # axes.set_xlim([0, numpy.max(time_array)])

    plt.plot(time_array, value_array)

    plt.suptitle(event_type)
    # plt.title("Users count: " + str(len(data)))

    plt.xlabel('Time')
    ylabel = event_type.lower().capitalize()
    if event_type != EventType.SYSTEM_UTILIZATION.value and event_type != EventType.RESOURCE_COUNT.value:
        ylabel += " time"

    plt.ylabel(ylabel)

    plt.show()

def get_smooth_graph(simulation_uuid, event_type):
    data = database.get_data_for_simulation(simulation_uuid, event_type)
    for d in data:
        print(d)

    time_array = [row[4] for row in data]
    value_array = [row[5] for row in data]

    if event_type == EventType.USER_LOGIN.value:
        value_array = [row[5] for row in data]


    axes = plt.gca()
    # axes.set_xlim([0, numpy.max(time_array)])

    ysmoothed = gaussian_filter1d(time_array, sigma=0.5)

    plt.plot(value_array, ysmoothed)

    plt.suptitle(event_type)
    # plt.title("Users count: " + str(len(data)))

    plt.xlabel('Time')
    ylabel = event_type.lower().capitalize()
    if event_type != EventType.SYSTEM_UTILIZATION.value and event_type != EventType.RESOURCE_COUNT.value:
        ylabel += " time"

    plt.ylabel(ylabel)

    plt.show()


def pie_chart(simulation_uuid, event_type):
    data = database.get_data_for_simulation(simulation_uuid, event_type)
    for d in data:
        print(d)

    time_array = [row[4] for row in data]
    value_array = [row[5] for row in data]

    part_0_20 = 0
    part_20_40 = 0
    part_40_60 = 0
    part_60_80 = 0
    part_80_ = 0

    for value in value_array:
        value/=1000

        if value <= 20:
            part_0_20 += 1
        elif value <= 40:
            part_20_40 += 1
        elif value <= 60:
            part_40_60 += 1
        elif value <= 80:
            part_60_80 += 1
        else:
            part_80_ += 1

    part_0_20 = math.ceil((part_0_20/len(value_array))*100)
    part_20_40 = math.ceil((part_20_40/len(value_array))*100)
    part_40_60 = math.ceil((part_40_60/len(value_array))*100)
    part_60_80 = math.ceil((part_60_80/len(value_array))*100)
    part_80_ = math.ceil((part_80_/len(value_array))*100)

    labels = '<20', '20-40', '40-60', '60-80', '80+'
    sizes = [part_0_20, part_20_40, part_40_60, part_60_80, part_80_]
    explode = (0, 0, 0, 0, 0)
    fig1, ax1 = plt.subplots()
    plt.suptitle(event_type+' TIME - Minutes')
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.0f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()


def show_simulation_details(simulation_uuid):
    pie_chart(simulation_uuid, EventType.RESOURCE_USAGE.value)
    get_resource_usage_graph(simulation_uuid, EventType.RESOURCE_COUNT.value)
    get_resource_usage_graph(simulation_uuid, EventType.USER_WAIT.value)
    get_resource_usage_graph(simulation_uuid, EventType.USER_LOGIN.value)
    get_resource_usage_graph(simulation_uuid, EventType.SYSTEM_UTILIZATION.value)

    props = database.get_props_for_simulation_uuid(simulation_uuid)
    prop_string = "Properties:"
    for p in props:
        prop_string += p[2] + ": " + p[3] + "\n"

    main = tk.Tk()
    main.title("Simulation")
    top_frame = tk.Frame(main)
    top_frame.pack(side=tk.TOP, expand=False)
    l = tk.Label(top_frame, text=prop_string)
    l.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    main.mainloop()


def get_simulation_props():
    res = database.get_all_simulations_uuids()

    with open('Simulations.csv', mode='w', newline='') as file:
        writer = csv.writer(file)

        # for_header = database.get_props_for_simulation_uuid(res[0])
        # header = ["SIMULATION UUID"]

        for rec in res:
            print(f"-----------Simulation-----------")
            print(f"UUID: {rec[0]}")
            props = database.get_props_for_simulation_uuid(rec[0])
            print("Properties:")
            for p in props:
                print(p[2] + ": " + p[3])

            props_array = [rec[0]]
            props_array.extend([p[3] for p in props])
            writer.writerow(props_array)


# show_simulation_details("f6acac41-fb14-4d34-9673-c8c2ca67e65c")
# show_simulation_details("7376577a-2467-4efa-bfd2-f3027ea0976c")
# show_simulation_details("a220d849-7c5c-4b07-b1de-ae29eb0f0469")
# show_simulation_details("586660a5-c01d-496a-97b0-e9a738227973")
# show_simulation_details("c4a6ec38-c1ce-43a3-b8fb-01f419a62aa2")

# show_simulation_details("a9713197-9ec5-462a-9d4b-ebd517e69694")
# show_simulation_details("38d1b7f8-34f7-4ff5-91f6-f1a47bc0a5db")
# show_simulation_details("0a08c856-1011-497c-a431-797e3c9b3e53")
# show_simulation_details("dc526ae3-6714-4744-92a3-9510f936a967")
# show_simulation_details("c418a15e-26a1-4427-8a7e-b0206f7eb513")

# show_simulation_details("cdf4899e-5457-465d-b196-3f9e10f197b4")

# show_simulation_details("dd2189a3-ecbc-4b8e-b5da-9c220b838d99")

# show_simulation_details("7f3e151a-f9fc-4359-a23f-b54f8dadbc09")
# show_simulation_details("c5dd30ff-be3f-49c6-b710-32177a50a0ca")
# get_simulation_props()

# bar_graph()

bar_graph_optimal_case_vs_others()