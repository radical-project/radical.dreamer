
from numpy.random import RandomState

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
        'var_spatial': float,
        'var_temporal': float,
        'size': int
    }

    _defaults = {
        'name': NAMES.Uniform,
        'mean': 1.,
        'var_spatial': 0.,
        'var_temporal': 0.,
        'size': 1
    }

    @property
    def samples(self):
        rs = RandomState()

        if not self.var_spatial:
            output = [self.mean] * self.size

        elif self.name not in self.NAMES.values:
            raise ValueError('Possible distributions are following: %s' %
                             ', '.join(self.NAMES.values))

        else:
            output = []
            if self.name == self.NAMES.Uniform:
                output = list(rs.uniform(self.mean - self.var_spatial,
                                         self.mean + self.var_spatial,
                                         self.size))

            elif self.name == self.NAMES.Normal:
                output = list(rs.normal(self.mean, self.var_spatial, self.size))

            elif self.name == self.NAMES.Poisson:
                output = list(rs.poisson(self.mean, self.size))
                # convert <class 'numpy.int64'> into <class 'float'>
                # (numpy types are not JSON serializable)
                for i in range(self.size):
                    output[i] = float(output[i])

        return output

    def sample_temporal(self, mean):
        output = mean

        if self.var_temporal:
            rs = RandomState()

            if self.name == self.NAMES.Uniform:
                output = rs.uniform(mean - self.var_temporal,
                                    mean + self.var_temporal)

            elif self.name == self.NAMES.Normal:
                output = rs.normal(mean, self.var_temporal)

            elif self.name == self.NAMES.Poisson:
                # convert <class 'numpy.int64'> into <class 'float'>
                # (numpy types are not JSON serializable)
                output = float(rs.poisson(mean))

        return output
