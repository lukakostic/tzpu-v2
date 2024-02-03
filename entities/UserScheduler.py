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

        '''self.values = [4.5772, 0.1835,
                       2.7327, 0.586,
                       5.1684, 2.2204,
                       9.5069, 2.4728]
        self.prob = [0.6724, 0.1137, 0.1345, 0.0794]'''

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
        '''self.USAGE_TIME = self.mixdis.rvs(prob=self.prob, size=math.ceil(sum(self.USERS_NUMBER)),
                                dist=[stats.lognorm, stats.weibull_min, stats.norm, stats.norm],
                                kwargs=(
                                    dict(loc=0, scale=np.exp(self.values[0]), args=(np.sqrt(self.values[1]),)),
                                    dict(loc=0, scale=np.exp(self.values[2]), args=(1 / self.values[3],)),
                                    dict(loc=self.values[4], scale=np.sqrt(self.values[5])),
                                    dict(loc=self.values[6], scale=np.sqrt(self.values[7]))
                                )
                                )'''

        def getSet(setIdx):
            ##"set","weight","distribution","alpha","beta"
            xlsx = [
                ("duration_C1_N", [
                    (0.6724, "Lognormal", 4.5772, 0.1835),
                    (0.1137, "Weibull", 2.7327, 0.586),
                    (0.1345, "Normal", 5.1684, 2.2204),
                    (0.0794, "Normal", 9.5069, 2.4728)]),
                ("duration_C1_pc_D", [
                    (0.1985, "Lognormal", 2.1667, 0.2421),
                    (0.4922, "Weibull", 4.54, 0.3426),
                    (0.2982, "Weibull", 4.9432, 0.3223),
                    (0.0015, "Normal", 5.09E-13, 1.00E-08),
                    (0.0096, "Normal", 1.6392, 1.3063)]),
                ("duration_C2_N", [
                    (0.2254, "Lognormal", 2.4633, 0.2729),
                    (0.7746, "Normal", 158.26, 2435.91)]),
                ("duration_C2_pc_D", [
                    (0.5483, "Lognormal", 2.224, 0.2871),
                    (0.4517, "Weibull", 4.9303, 0.4792)]),
                ("duration_C4_N", [
                    (0.2369, "Weibull", 4.5073, 0.0576),
                    (0.6087, "Weibull", 4.2193, 0.1981),
                    (0.1544, "Weibull", 2.7446, 0.6235)]),
                ("duration_C4_pc_D", [
                    (0.0156, "Weibull", -1.2222, 0.6612),
                    (0.7057, "Weibull", 4.4412, 0.1878),
                    (0.1999, "Weibull", 3.7023, 0.5288),
                    (0.0788, "_", 0, 0)]),
                ("duration_C1_1_N", [
                    (0.2445, "Weibull", 2.3179, 0.3894),
                    (0.3329, "Weibull", 4.6501, 0.1962),
                    (0.4226, "Weibull", 4.6419, 0.44)]),
                ("duration_C1_3_N", [
                    (0.2879, "Lognormal", 1.9648, 0.2977),
                    (0.7121, "Weibull", 4.7319, 0.3754)]),
                ("duration_C1_4_N", [
                    (0.3202, "Weibull", 2.0401, 0.3978),
                    (0.6798, "Weibull", 4.8025, 0.527)])
            ]
            modeli = dict(Lognormal = stats.lognorm,Weibull = stats.weibull_min,_ = stats.norm,Normal = stats.norm)

            def model2dict(tupl):
                m = tupl[1][0].lower()
                if m == "n" or m == "_":
                    return dict(loc=tupl[2], scale=np.sqrt(tupl[3]))
                if m == "l":
                    return dict(loc=0, scale=np.exp(tupl[2]), args=(np.sqrt(tupl[3]),))
                if m == "w":
                    return dict(loc=0, scale=np.exp(tupl[2]), args=(1.0 / tupl[3],))

            set_ = xlsx[setIdx][1]
            return dict(
                prob=list(map(lambda x: x[0], set_)),
                size=math.ceil(sum(self.USERS_NUMBER)),
                dist=list(map(lambda x: modeli[x[1]], set_)),
                kwargs=tuple(map(model2dict, set_))
            )

        self.USAGE_TIME = self.mixdis.rvs(**getSet(1))

        self.USAGE_TIME = [x + Properties.MINIMUM_USAGE_TIME for x in self.USAGE_TIME]
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
