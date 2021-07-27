#!/usr/bin/env python
#
# ResourceManager should be run first:
#
#   radical-dreamer-start-manager [--cfg_path config_data.json]
#
# Config "cfg_default" is used as an example and should be overwritten by user
# (should be consistent with the manager - to use ONLY one configuration) to
# fulfill user's requirements (or JSON config should be used instead). If user
# is satisfied with default config values (from "cfg_default") then only
# RabbitMQ URL should be changed or set by the environment variable:
#
#   export RADICAL_DREAMER_RMQ_URL="amqp://localhost:5672/"
#
# NOTE: In case env variable is used then it should be set for every executable
#       (it has the highest priority over other URL definitions)
#

__author__    = 'RADICAL-Cybertools Team'
__email__     = 'info@radical-cybertools.org'
__copyright__ = 'Copyright 2020-2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

import os

from radical.dreamer import Session, Resource, Workload
from radical.dreamer.configs import cfg_default


if __name__ == '__main__':
    os.environ['RADICAL_DREAMER_LOG_LVL'] = 'DEBUG'
    # set RMQ URL here if needed:
    #   os.environ['RADICAL_DREAMER_RMQ_URL'] = 'amqp://localhost:5672/'

    # Create a resource with a specific number of cores, with performance of
    # each core drawn from a distribution (provided resource is dynamic due to
    # `var_temporal` input data).
    #
    # NOTE: Core objects are not generated during the resource initialization
    #       (by default), but will be generated in the `processing` method of
    #       ResourceManager class. In case, cores should be defined before the
    #       session run, please use `set_cores` input flag or a method with the
    #       same name (e.g., `resource.set_cores()`).
    resource = Resource(num_cores=128,
                        perf_dist={'name': 'uniform',
                                   'mean': 32.,
                                   'var_spatial': 2.,
                                   'var_temporal': 1.})
    # Create a workload with a specific number of tasks, with number of
    # operations per task drawn from a distribution.
    #
    # NOTE: Task objects are not generated during the workload initialization
    #       (by default), which is similar to Resource with Cores behaviour.
    #       Same as for Resource to generate task objects explicitly,
    #       corresponding input flag and method are `set_tasks`.
    workload = Workload(num_tasks=128,
                        ops_dist={'mean': 1024.})

    # Create Session and set descriptions of Resource and Workload(s)
    session = Session(cfg=cfg_default)
    session.set(resource=resource, workload=workload)
    # for multi-workloads: session.set(resource=resource, workloads=[workload])

    # Publish objects to RMQ and collect output profiles
    session.run()


# ### Examples of config setup for the Session definition:
#
# from radical.dreamer import Config, Session
#
# cfg_data = {
#     'rabbitmq': {
#         'url': 'amqp://localhost:5672/'
#     },
#     'session': {
#         'profile_base_name': 'rd.profile'
#     },
#     'schedule': {
#         'strategy': 'smallest_to_fastest',
#         'early_binding': True
#     }
# }
#
# session_00 = Session(cfg=cfg_data)
# session_01 = Session(cfg=Config(cfg_data))
# session_02 = Session(cfg=Config(cfg_path='./config_data.json'))
# session_03 = Session(cfg_path='./config_data.json')
#
