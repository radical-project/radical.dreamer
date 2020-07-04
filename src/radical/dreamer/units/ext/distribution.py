
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
        'var': float,
        'var_local': float,
        'size': int
    }

    _defaults = {
        'name': NAMES.Uniform,
        'mean': 1.,
        'var': 0.,
        'var_local': 0.,
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

        if self.name == self.NAMES.Uniform:

            # distribution among all elements
            output = list(np.random.uniform(self.mean - self.var,
                                            self.mean + self.var,
                                            self.size))
            # distribution of each element (local distribution)
            if self.var_local:
                for i in range(self.size):
                    output[i] = np.random.uniform(output[i] - self.var_local,
                                                  output[i] + self.var_local)

        elif self.name == self.NAMES.Normal:

            # distribution among all elements
            output = list(np.random.normal(self.mean, self.var, self.size))
            # distribution of each element (local distribution)
            if self.var_local:
                for i in range(self.size):
                    output[i] = np.random.normal(output[i], self.var_local)

        elif self.name == self.NAMES.Poisson:

            if self.var:  # used as a flag to generate samples
                # distribution among all elements
                output = list(np.random.poisson(self.mean, self.size))
                # convert <class 'numpy.int64'> into <class 'float'>
                # (numpy types are not JSON serializable)
                for i in range(self.size):
                    output[i] = float(output[i])
            else:
                output = [self.mean] * self.size

            if self.var_local:  # used as a flag to generate samples
                # distribution of each element (local distribution)
                for i in range(self.size):
                    output[i] = float(np.random.poisson(output[i]))

        return output
