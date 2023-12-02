import random

from simpy import RealtimeEnvironment

from entities.BrokerCore import BrokerCore
from entities.Resource import Resource
from entities.ResourceProvider import ResourceProvider
from entities.UserScheduler import UserScheduler
from utils.Proprerties import Properties


class BrokerPrepareWhenZero(BrokerCore):

    def __init__(self, log, resource_provider: ResourceProvider, user_scheduler: UserScheduler, env: RealtimeEnvironment):
        BrokerCore.__init__(self, log, resource_provider, user_scheduler, env)

    def prepare_new_resources(self, env: RealtimeEnvironment):
        if self.resource_provider.get_resource_ready_count() == 0:
            for _ in range(Properties.RESOURCE_ADD_NUMBER):
                env.process(self.prepare_one_resource(env))
            # Properties.RESOURCE_ADD_NUMBER += Properties.RESOURCE_ADD_RATE