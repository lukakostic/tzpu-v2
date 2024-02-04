from abc import abstractmethod

from simpy import RealtimeEnvironment

from entities.Resource import Resource
from entities.ResourceProvider import ResourceProvider
from entities.User import User
from entities.UserScheduler import UserScheduler
from utils.Analytics import Analytics
from utils.Proprerties import Properties
import random
import numpy as np


class BrokerCore:

    def __init__(self, log, resource_provider: ResourceProvider, user_scheduler: UserScheduler, env: RealtimeEnvironment):
        self.log = log
        self.analytics = Analytics()
        self.resource_provider = resource_provider
        self.user_scheduler = user_scheduler
        self.env = env
        self.simulation_end = env.event()

    def user_login(self, user: User):
        self.analytics.register_user_login(self.env.now, user)

        print(f"Users waiting: {self.resource_provider.get_users_waiting_count()}")
        queue_begin = self.env.now
        resource = None
        if self.resource_provider.get_resource_count() == Properties.MAX_AVAILABLE_RESOURCES:
            # nema slobodnih i ne mogu da se kreirati novi
            resource = self.resource_provider.get_resource()

        elif self.resource_provider.get_resource_ready_count() == 0:
            # nema slobodnih i pristupa se kreiranju novih
            yield self.env.timeout(self.get_normal(Properties.RESOURCE_PREPARE_TIME_MEAN,
                                              Properties.RESOURCE_PREPARE_TIME_STD))
            '''self.get_positive_value_gauss(Properties.RESOURCE_PREPARE_TIME_MEAN,
                                              Properties.RESOURCE_PREPARE_TIME_STD))'''

            self.prepare_new_resources(self.env)
            resource = self.resource_provider.get_resource()

        else:
            # ako ima slobodnih resursa
            # self.prepare_new_resources(self.env)
            resource = self.resource_provider.get_resource()

        with resource.simpy_resource.request() as req:
            yield req
            queue_end = self.env.now

            self.analytics.register_utilization(self.env.now, self.resource_provider.get_resource_count(),
                                                self.resource_provider.get_resource_used_count())
            self.analytics.register_user_waiting(queue_begin, queue_end, user)
            usage_begin = self.env.now

            # koristi resur
            yield self.env.timeout(self.user_scheduler.USAGE_TIME.pop())

            usage_end = self.env.now

            self.analytics.register_usage_time(usage_begin, usage_end, user)




    @abstractmethod
    def prepare_new_resources(self, env: RealtimeEnvironment):
        # priprema nove reurse
        # odredjuje kad se krece sa kreiranjem novih
        return

    @staticmethod
    def get_positive_value_gauss(mean, std):
        value = int(random.gauss(mean, std))
        if value <= 0:
            value = mean
        return value

    @staticmethod
    def get_normal(mean, std):
        value = int(np.random.normal(mean, std))
        if value <= 0:
            value = mean
        return value


    def prepare_one_resource(self, env):
        with self.resource_provider.worker.request() as worker:
            yield worker

            yield env.timeout(self.get_normal(Properties.RESOURCE_PREPARE_TIME_MEAN,
                                              Properties.RESOURCE_PREPARE_TIME_STD))
            '''self.get_positive_value_gauss(Properties.RESOURCE_PREPARE_TIME_MEAN,
                                                            Properties.RESOURCE_PREPARE_TIME_STD))'''

            self.resource_provider.prepare_new_resource()
            self.analytics.register_new_resource_prepared(self.resource_provider.get_resource_count(), env.now)

    def end_process(self):
        if self.resource_provider.is_all_resource_free():
            yield self.simulation_end

    def prepare_more_resources(self, env: RealtimeEnvironment, count: int):
        resource_count = self.resource_provider.get_resource_count()
        number_to_add = count - resource_count
        for _ in range(number_to_add):
            env.process(self.prepare_one_resource(env))