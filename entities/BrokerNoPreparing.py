import random

from simpy import RealtimeEnvironment

from entities.BrokerCore import BrokerCore
from entities.Resource import Resource
from entities.ResourceProvider import ResourceProvider
from entities.UserScheduler import UserScheduler
from utils.Proprerties import Properties


class BrokerNoPreparing(BrokerCore):

    def __init__(self, log, resource_provider: ResourceProvider, user_scheduler: UserScheduler, env: RealtimeEnvironment):
        BrokerCore.__init__(self, log, resource_provider, user_scheduler, env)

    def prepare_new_resources(self, env: RealtimeEnvironment):
        pass

    def prepare_one_resource(self, env):
        pass
