#!/usr/bin/env python
#
# RADICAL-DREAMER (RD) is a successor of WLMS-Emulator (aka RADICAL-Calculator),
# which was designed and implemented by Vivek Balasubramanian, and later
# supported and used by Ioannis Paraskevakos, Kartik Rattan, Aydin Saribudak.
#
# NOTE: RD is a new implementation of the original concept.
#
# [ DREAMER: Dynamic Resource and Adaptive Mapping EmulatoR ]
#

__author__ = 'RADICAL Team'
__email__ = 'radical@rutgers.edu'
__copyright__ = 'Copyright 2020, RADICAL Research, Rutgers University'
__license__ = 'MIT'

""" Setup script. Used by easy_install and pip. """

import sys

_PKG_NAME = 'radical.dreamer'

try:
    from setuptools import setup, Command, find_packages
except ImportError as e:
    print('%s needs setuptools to install' % _PKG_NAME)
    sys.exit(1)


if sys.hexversion < 0x03050000:
    raise RuntimeError(
        '[ERROR]: %s requires Python 3.5 or higher' % _PKG_NAME)


setup_args = {
    'name': _PKG_NAME,
    'namespace_packages': ['radical'],
    'version': 0.1,
    'description': 'Dynamic Resource and Adaptive Mapping EmulatoR',
    # 'long_description' : (read('README.md') + '\n\n' + read('CHANGES.md')),
    'author': __author__,
    'author_email': __email__,
    'maintainer': __author__,
    'maintainer_email': __email__,
    # 'url': 'https://github.com/radical-cybertools/%s' % _PKG_NAME,
    'license': 'MIT',
    'keywords': 'radical workload resource execution emulator',
    'classifiers':  [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
        'Topic :: System :: Distributed Computing',
        'Topic :: Scientific/Engineering',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],
    'scripts': ['bin/radical-dreamer-start-manager'],
    'packages': find_packages('src'),
    'package_dir': {'': 'src'},
    'package_data': {'': ['*.sh', '*.json', 'VERSION', 'SDIST']},
    'install_requires': ['radical.utils>=1.4.1',
                         'numpy',
                         'pika'],
    'tests_require': ['pytest',
                      'pylint',
                      'flake8',
                      'coverage'],
    'zip_safe': False
}

setup(**setup_args)


"""
To publish to pypi:
python setup.py sdist
twine upload --skip-existing dist/<tarball name>
"""
