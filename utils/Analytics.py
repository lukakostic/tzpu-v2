import math
from collections import defaultdict

from entities.EventType import EventType
from entities.User import User
from utils.DatabaseUtils import DatabaseUtils
from utils.Proprerties import Properties

class Analytics:

    def __init__(self):
        self.database = DatabaseUtils()
        self.log_to_database = True
        self.total_user_count = 0
        self.users_served_count = 0
        self.utilization = 0
        #self.SLA_broke = 0
        self.SLA1_broke = 0
        self.SLA2_broke = 0
        self.SLA3_broke = 0
        self.SLA4_broke = 0

    arrivals = defaultdict(lambda: 0)
    utilization_percent = defaultdict(lambda: [])
    waits_for_getting = defaultdict(lambda: [])

    def register_arrivals(self, time):
        self.arrivals[int(time)] += 1

    def system_utilization(self, time, wait):
        self.utilization_percent[int(time)].append(wait)

    def register_utilization(self, time, max_num, current_num):
        self.utilization = current_num / max_num
        self.system_utilization(time, self.utilization * 100)
        if self.log_to_database:
            self.database.log_event(EventType.SYSTEM_UTILIZATION.value, None, time, round(self.utilization*100))

    def register_user_login(self, time, user: User):
        self.register_arrivals(time)
        self.total_user_count += 1
        print(f"User({user.user_id}) login at {time}")

    def register_usage_time(self, begin, end, user: User):
        usage_time = end - begin

        print(f"User {user.name}({user.user_id}) used resource for {usage_time} minutes")

        self.users_served_count += 1
        print(f"Users finished: {self.users_served_count} of total {self.total_user_count} users; Utilization: {self.utilization}")
        if self.log_to_database:
            self.database.log_event(EventType.RESOURCE_USAGE.value, user.user_id, end, usage_time * 1000)

    def register_user_waiting(self, queue_begin, queue_end, user: User):
        wait = queue_end - queue_begin
        print(f"USER WAIT [{wait}]")
        print(wait)
        self.register_wait_for_getting(queue_end, wait)
        if wait > Properties.SLA1:
            self.SLA1_broke += 1
            if wait > Properties.SLA2:
                self.SLA2_broke += 1
                if wait > Properties.SLA3:
                    self.SLA3_broke += 1
                    if wait > Properties.SLA4:
                        self.SLA4_broke += 1
                        print(f"User({user.user_id}) waited {wait} minutes and broke SLA: {Properties.SLA4}!")
                        print(f"SLA was broken {self.SLA4_broke} times during this simulation")
                        self.database.log_event(EventType.SLA_BROKE.value, user.user_id, queue_end, Properties.SLA4)
                    else:
                        print(f"User({user.user_id}) waited {wait} minutes and broke SLA: {Properties.SLA3}!")
                        print(f"SLA was broken {self.SLA3_broke} times during this simulation")
                        self.database.log_event(EventType.SLA_BROKE.value, user.user_id, queue_end, Properties.SLA3)
                else:
                    print(f"User({user.user_id}) waited {wait} minutes and broke SLA: {Properties.SLA2}!")
                    print(f"SLA was broken {self.SLA2_broke} times during this simulation")
                    self.database.log_event(EventType.SLA_BROKE.value, user.user_id, queue_end, Properties.SLA2)
            else:
                print(f"User({user.user_id}) waited {wait} minutes and broke SLA: {Properties.SLA1}!")
                print(f"SLA was broken {self.SLA1_broke} times during this simulation")
                self.database.log_event(EventType.SLA_BROKE.value, user.user_id, queue_end, Properties.SLA1)
        print(f"User({user.user_id}) waited {wait} minutes")
        if self.log_to_database:
            self.database.log_event(EventType.USER_WAIT.value, user.user_id, queue_end, wait)

    def register_wait_for_getting(self, time, wait):
        self.waits_for_getting[int(time)].append(wait)

    def register_new_resource_prepared(self, resource_count, time):
        print(f"RESOURCE COUNT {resource_count}")
        if self.log_to_database:
            self.database.log_event(EventType.RESOURCE_COUNT.value, None, time, resource_count)