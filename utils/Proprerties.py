import inspect
import random
from builtins import staticmethod


class Properties:
    SIMULATION_UUID = 0
    TIME_SPEEDUP = 200
    SIMULATION_DURATION_MINUTES = 300

    CONSTANT_USER_COUNT_ENABLED = True
    USER_COUNT = 200

    NEXT_LOGIN_MEAN = 5
    NEXT_LOGIN_STD = 3

    USERS_PER_LOGIN_MEAN = 20
    USERS_PER_LOGIN_STD = 3

    READY_COUNT = 10
    MAX_AVAILABLE_RESOURCES = 150

    RESOURCE_USAGE_TIME_MEAN = 60
    RESOURCE_USAGE_TIME_STD = 15

    NUMBER_OF_WORKERS = 3

    RESOURCE_PREPARE_TIME_MEAN = 5
    RESOURCE_PREPARE_TIME_STD = 2

    CRITICAL_UTILISATION_PERCENT = 0.6
    RESOURCE_ADD_NUMBER = 1
    RESOURCE_ADD_RATE = 3

    GAMMA_25_SHAPE = 0.181
    GAMMA_25_SCALE = 0.56
    GAMMA_75_SHAPE = 0.36
    GAMMA_75_SCALE = 0.12

    EXPONENTIAL_LAMBDA = 5/3

    MINIMUM_USAGE_TIME = 20

    # GAMMA_25_SHAPE = 7.5
    # GAMMA_25_SCALE = 0.56
    # GAMMA_75_SHAPE = 0.36
    # GAMMA_75_SCALE = 0.12

    @staticmethod
    def get_positive_value_gauss(mean, std):
        value = int(random.gauss(mean, std))
        if value < 0:
            value = 1
        return value

    @classmethod
    def get_next_users_number(cls):
        value = int(random.gauss(cls.USERS_PER_LOGIN_MEAN, cls.USERS_PER_LOGIN_STD))
        if value < 0:
            value = 1
        return value

    @classmethod
    def get_parameters(cls):
        attributes = inspect.getmembers(Properties, lambda a: not (inspect.isroutine(a)))
        return [a for a in attributes if not (a[0].startswith('__')
                                              or a[0].endswith('__')
                                              or a[0].startswith('SIMULATION')
                                              or a[0].startswith('TIME_SPEEDUP')
                                              or a[0].startswith('SIMULATION_DURATION_MINUTES'))]
