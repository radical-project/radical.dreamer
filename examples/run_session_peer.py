#!/usr/bin/env python

__author__    = 'RADICAL-Cybertools Team'
__email__     = 'info@radical-cybertools.org'
__copyright__ = 'Copyright 2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

from radical.dreamer import Session, Resource, Workload
from radical.dreamer.configs import cfg_default


if __name__ == '__main__':
    # Create a resource with a specific number of cores, with performance of
    # each core drawn from a distribution (provided resource is dynamic due to
    # `var_temporal` input data).
    #
    # NOTE: Core objects are not generated during the resource initialization
    #       (by default), but will be generated in the `processing` method of
    #       ResourceManager class. In case, cores should be defined before the
    #       session run, please use `set_cores` input flag or a method with the
    #       same name (e.g., `resource.set_cores()`).
    resource = Resource(num_cores=32,
                        perf_dist={'name': 'normal',
                                   'mean': 16.,
                                   'var_spatial': 4.,
                                   'var_temporal': 2.})
    # Create a workload with a specific number of tasks, with number of
    # operations per task drawn from a distribution.
    #
    # NOTE: Task objects are not generated during the workload initialization
    #       (by default), which is similar to Resource with Cores behaviour.
    #       Same as for Resource to generate task objects explicitly,
    #       corresponding input flag and method are `set_tasks`.
    workload = Workload(num_tasks=256,
                        ops_dist={'mean': 512.})

    # Create Session (peer mode) and set descriptions of Resource & Workload(s)
    session = Session(cfg=cfg_default, is_peer=True)
    session.set(resource=resource, workload=workload)
    # for multi-workloads: session.set(resource=resource, workloads=[workload])

    # Start the processing and collect output profiles
    session.run()


# ### Example of config data:
#
# from radical.dreamer import Config, Session
#
# cfg_data = {
#     'session': {
#         'profile_base_name': './rd.profile'
#     },
#     'schedule': {
#         'strategy': 'largest_to_fastest',
#         'early_binding': False
#     }
# }
#
# session = Session(cfg=cfg_data or Config(cfg_data), is_peer=True)
#
