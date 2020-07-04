#!/usr/bin/env python
#
# Resource- and Workload-Managers should be run first:
#   bin/radical-dreamer-start-manager resource [--cfg_path config_data.json]
#   bin/radical-dreamer-start-manager workload [--cfg_path config_data.json]
#
# Config "cfg_default" is used as an example and should be overwritten by user
# (should be consistent with managers - to use ONLY one configuration) to
# fulfill user's requirements (or JSON config should be used instead). If user
# is satisfied with default config values (from "cfg_default") then only
# RabbitMQ URL should be changed or set by the environment variable:
#
#   export RADICAL_DREAMER_RMQ_URL="amqp://localhost:5672/"
#
# NOTE: In case env variable is used then it should be set for every executable
#       (it has the highest priority over other URL definitions)
#

__author__ = 'RADICAL Team'
__email__ = 'radical@rutgers.edu'
__copyright__ = 'Copyright 2020, RADICAL Research, Rutgers University'
__license__ = 'MIT'

# import os
# os.environ['RADICAL_DREAMER_RMQ_URL'] = 'amqp://localhost:5672/'

from radical.dreamer import Session, Resource, Workload
from radical.dreamer.configs import cfg_default


if __name__ == '__main__':
    # Create a Resource with a specific number of cores,
    # with performance of each core drawn from a distribution
    resource = Resource(num_cores=128,
                        perf_dist={'name': 'uniform',
                                   'mean': 32.,
                                   'var': 2.,
                                   'var_local': 1.})
    # Create a Workload with a specific number of tasks,
    # with number of operations per task drawn from a distribution
    workload = Workload(num_tasks=128,
                        ops_dist={'name': 'uniform',
                                  'mean': 1024.})

    # Create a Session to publish descriptions of Resource and Workload to RMQ
    session = Session(cfg=cfg_default)
    session.set_resource(resource)
    session.set_workload(workload)

"""
### Config example:

from radical.dreamer import Config, Session

cfg_data = {
    'rabbitmq': {
        'url': 'amqp://localhost:5672/',
        'exchange': 'rd_rdcl_857',
        'queues': {
            'execute': 'execute_rdcl_857',
            'resource': 'resource_rdcl_857',
            'schedule': 'schedule_rdcl_857',
            'session': 'session_rdcl_857',
            'workload': 'workload_rdcl_857'
        }
    },
    'session': {
        'output_profile': './profile.json',
        'schedule_options': ['largest_first', 'smallest_to_fastest'],
        'early_binding': True,
        'dynamic_resource': True
    }
}
session = Session(cfg=Config(cfg_data))

#   Also, "cfg_data" can be stored in JSON file and corresponding path used to 
#   initialize the config for Session and Resource/WorkloadManager(s):
#      session = Session(cfg=Config(cfg_path='./config_data.json'))
#   or
#      session = Session(cfg_path='./config_data.json')
"""
