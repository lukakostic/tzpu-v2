import math
import random

from simpy import RealtimeEnvironment

from entities.BrokerCore import BrokerCore
from entities.Resource import Resource
from entities.ResourceProvider import ResourceProvider
from entities.UserScheduler import UserScheduler
from utils.Proprerties import Properties


class Broker(BrokerCore):

    def __init__(self, log, resource_provider: ResourceProvider, user_scheduler: UserScheduler, env: RealtimeEnvironment):
        BrokerCore.__init__(self, log, resource_provider, user_scheduler, env)

    def prepare_new_resources(self, env: RealtimeEnvironment):
        if self.resource_provider.get_resource_used_count() > \
                Properties.CRITICAL_UTILISATION_PERCENT * self.resource_provider.get_resource_count():

            print(f"used cont: {self.resource_provider.get_resource_used_count()} utilization: {Properties.CRITICAL_UTILISATION_PERCENT * self.resource_provider.get_resource_count()}")
            print(f"will create:{self.calculate_resources_to_prepare_count()}")

            for _ in range(self.calculate_resources_to_prepare_count()):
                env.process(self.prepare_one_resource(env))


    # racuna koliko novih da doda, vrednost opaka kako se priblizava maksimalnom broju
    # raste ako ima vise koji cekaju

    def calculate_resources_to_prepare_count(self):
        resource_count = self.resource_provider.get_resource_count()
        max_resources_count = Properties.MAX_AVAILABLE_RESOURCES
        number_to_add = math.floor(
            (max_resources_count / resource_count)*0.2 *
            self.resource_provider.get_users_waiting_count())

        if number_to_add < 1 and max_resources_count / resource_count < 0.05 \
                and self.resource_provider.get_users_waiting_count()>10:
            number_to_add = Properties.RESOURCE_ADD_NUMBER

        return number_to_add

            # moze da se doda neki smart broker koji na osnovu usage time, queue size racuna koliko i kad da doda
            # ispitni rok -> dan kada ima vise ljudi
