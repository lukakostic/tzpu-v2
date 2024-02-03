import random
import numpy as np
import math


from scipy import stats
from utils.Proprerties import Properties
from statsmodels.distributions.mixture_rvs import MixtureDistribution


class UserScheduler:
    def __init__(self):
        # random.seed(42)
        self.INTER_ARRIVAL_TIMES = []
        self.USERS_NUMBER = []
        self.USAGE_TIME = []
        self.TIME_BETWEEN_LOGINS = []

        self.alpha1 = 4.5772
        self.beta1 = 0.1835
        self.alpha2 = 2.7327
        self.beta2 = 0.586
        self.prob = [0.6724, 0.3276]

        self.mixdis = MixtureDistribution()


    # stari kod, ne koristi se ovaj mod
    def basic_mod(self):
        self.INTER_ARRIVAL_TIMES = [random.expovariate(1 / Properties.NEXT_LOGIN_MEAN)
                                    for _ in range(80)]
        self.USERS_NUMBER = [Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                 Properties.USERS_PER_LOGIN_STD)
                             for _ in range(80)]
        self.USAGE_TIME = [Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                               Properties.USERS_PER_LOGIN_STD)
                           for _ in range(sum(self.USERS_NUMBER))]

    def real_mod(self):
        # inter arrival times
        if Properties.CONSTANT_USER_COUNT_ENABLED:
            self.USERS_NUMBER = []
            total_users_count = Properties.USER_COUNT
            while total_users_count > 0:
                user_count = Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                 Properties.USERS_PER_LOGIN_STD)
                if user_count>total_users_count:
                    user_count = total_users_count

                self.USERS_NUMBER.append(user_count)
                total_users_count -= user_count

        else:
            self.USERS_NUMBER = [Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                     Properties.USERS_PER_LOGIN_STD)
                                 for _ in range(80)]

        self.INTER_ARRIVAL_TIMES = [Properties.get_positive_value_gauss(Properties.NEXT_LOGIN_MEAN,
                                                                        Properties.NEXT_LOGIN_STD)
                                    for _ in range(sum(self.USERS_NUMBER))]

        '''self.USAGE_TIME = [np.random.gamma(Properties.GAMMA_25_SHAPE, Properties.GAMMA_25_SCALE)
                           for _ in range(math.ceil(sum(self.USERS_NUMBER) * 0.25))]
        self.USAGE_TIME.extend([np.random.gamma(Properties.GAMMA_75_SHAPE, Properties.GAMMA_75_SCALE)
                                for _ in range(math.ceil(sum(self.USERS_NUMBER) * 0.75))])

        self.USAGE_TIME = [(x * 268) + Properties.MINIMUM_USAGE_TIME for x in self.USAGE_TIME]'''

        ## Nas nov USAGE_TIME. Za sada hardcoded sa norm i lognorm raspodelom
        self.USAGE_TIME = self.mixdis.rvs(prob=self.prob, size=math.ceil(sum(self.USERS_NUMBER)),
                                dist=[stats.norm, stats.norm],
                                kwargs=(
                                    dict(loc=self.alpha1, scale=np.sqrt(self.beta1)),
                                    dict(loc=self.alpha2, scale=np.sqrt(self.alpha2))
                                )
                            )
        self.USAGE_TIME = [(x * 268) + Properties.MINIMUM_USAGE_TIME for x in self.USAGE_TIME]
        # povecati svaki za neku vrednost
        self.TIME_BETWEEN_LOGINS = [random.expovariate(Properties.EXPONENTIAL_LAMBDA) + 1
                                    for _ in range(sum(self.USERS_NUMBER))]

        random.shuffle(self.INTER_ARRIVAL_TIMES)
        random.shuffle(self.USERS_NUMBER)
        random.shuffle(self.USAGE_TIME)
        random.shuffle(self.TIME_BETWEEN_LOGINS)

    def examination_date_mod(self):
        # inter arrival times
        self.INTER_ARRIVAL_TIMES = [Properties.get_positive_value_gauss(Properties.NEXT_LOGIN_MEAN,
                                                                        Properties.NEXT_LOGIN_STD)
                                    for _ in range(80)]
        self.USERS_NUMBER = [Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                 Properties.USERS_PER_LOGIN_STD) + 1
                             for _ in range(80)]

        self.USAGE_TIME = [np.random.gamma(Properties.GAMMA_25_SHAPE, Properties.GAMMA_25_SCALE)
                           for _ in range(math.ceil(sum(self.USERS_NUMBER) * 0.25))]
        self.USAGE_TIME.extend([np.random.gamma(Properties.GAMMA_75_SHAPE, Properties.GAMMA_75_SCALE)
                                for _ in range(math.ceil(sum(self.USERS_NUMBER) * 0.75))])

        self.USAGE_TIME = [(x * 268) + 20 for x in self.USAGE_TIME]

        # povecati svaki za neku vrednost
        self.TIME_BETWEEN_LOGINS = [random.expovariate(5 / 3) + 1 for _ in range(sum(self.USERS_NUMBER))]
        # self.TIME_BETWEEN_LOGINS = [x+3 for x in self.TIME_BETWEEN_LOGINS]

        random.shuffle(self.INTER_ARRIVAL_TIMES)
        random.shuffle(self.USERS_NUMBER)
        random.shuffle(self.USAGE_TIME)
        random.shuffle(self.TIME_BETWEEN_LOGINS)
