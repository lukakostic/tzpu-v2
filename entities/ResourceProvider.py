import random

import simpy
from simpy import RealtimeEnvironment

from entities.Resource import Resource
from entities.ResourceType import ResourceType
from utils.Analytics import Analytics
from utils.Proprerties import Properties


class ResourceProvider:
    def __init__(self, env):
        print("Starting simulation")
        self.env = env
        self.ready_resources = [Resource(env, 1, ResourceType.LICENCE) for _ in range(Properties.READY_COUNT)]

        self.worker = simpy.Resource(self.env,Properties.NUMBER_OF_WORKERS)

    def get_resource_count(self):
        return len(self.ready_resources)

    def is_all_resource_free(self):
        for resource in self.ready_resources:
            if not resource.is_ready():
                return False
        return True

    def get_resource_used_count(self):
        used_count = 0
        for resource in self.ready_resources:
            if not resource.is_ready():
                used_count += 1
        return used_count

    def get_users_waiting_count(self):
        used_count = 0
        for resource in self.ready_resources:
            used_count += resource.get_queue_size()
        return used_count

    def is_worker_busy(self):
        return self.worker.count == 0

    def get_resource_ready_count(self):
        count = 0
        for resource in self.ready_resources:
            if resource.is_ready():
                count += 1
        return count

    def add_resources(self, count):
        self.ready_resources.extend([Resource(self.env, 1, ResourceType.LICENCE) for _ in range(count)])

    def prepare_new_resource(self) -> Resource:
        if len(self.ready_resources) >= Properties.MAX_AVAILABLE_RESOURCES:
            return None

        new_resource = Resource(self.env, len(self.ready_resources) + 1, ResourceType.LICENCE)
        self.ready_resources.append(new_resource)

        return new_resource

    def get_resource(self) -> Resource:

        for resource in self.ready_resources:
            if resource.is_ready():
                return resource

        tuples = list(zip(range(len(self.ready_resources)), self.ready_resources))  # tuples of (i, line)
        shortest = tuples[0][0]
        for i, resource in tuples:
            if len(resource.simpy_resource.queue) < len(self.ready_resources[shortest].simpy_resource.queue):
                shortest = i
                break
        return self.ready_resources[shortest]

        # return self.ready_resources[random.randrange(len(self.ready_resources))]
