
import numpy as np

from radical.utils import Munch

from ...utils import EnumTypes


class SampleDistribution(Munch):

    NAMES = EnumTypes(
        ('Normal', 'normal'),
        ('Poisson', 'poisson'),
        ('Uniform', 'uniform')
    )

    _schema = {
        'name': str,
        'mean': float,
        'sd': float,
        'sd_init': float,
        'size': int
    }

    _defaults = {
        'name': NAMES.Uniform,
        'mean': 1.,
        'sd': 0.,
        'sd_init': 0.,
        'size': 1
    }

    def __init__(self, from_dict=None):
        super().__init__(from_dict=self._defaults)

        if from_dict:
            self.update(from_dict)

        if self.name not in self.NAMES.values:
            raise ValueError('Possible distributions are following: %s' %
                             ', '.join(self.NAMES.values))

    def generate(self):
        output = []

        if self.name == self.NAMES.Normal:

            if self.sd_init:
                dist_mean = np.random.normal(self.mean, self.sd_init)
            else:
                dist_mean = self.mean

            if self.sd:
                output = list(np.random.normal(dist_mean, self.sd, self.size))
            else:
                output = [dist_mean] * self.size

        elif self.name == self.NAMES.Uniform:

            dist_mean = np.random.uniform(self.mean - self.sd_init,
                                          self.mean + self.sd_init)
            output = list(np.random.uniform(dist_mean - self.sd,
                                            dist_mean + self.sd,
                                            self.size))

        elif self.name == self.NAMES.Poisson:

            dist_mean = np.random.poisson(self.mean)
            output = list(np.random.poisson(dist_mean, self.size))

        return output
