import simpy

from entities import ResourceType


class Resource:
    def __init__(self, env, resource_id, resource_type: ResourceType):
        self.env = env
        self.simpy_resource = simpy.Resource(self.env)
        self.id = resource_id
        self.resource_type = resource_type

    def is_ready(self):
        return self.simpy_resource.count == 0

    def get_queue_size(self):
        return len(self.simpy_resource.queue)
