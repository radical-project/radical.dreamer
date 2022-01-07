#!/usr/bin/env python3

import os
import time

from radical.dreamer import Session, Resource, Workload

CONFIG_DATA = {
    'schedule': {
        'strategy': 'largest_to_fastest',
        'early_binding': False
    },
    'session': {
        'profile_base_name': None  # profile is skipped
    }
}
NUM_RUNS = 5


def generate_resource(num, set_cores=True):
    return Resource(num_cores=num,
                    io_rate=4.,
                    perf_dist={'name': 'normal',
                               'mean': 16.,
                               'var_spatial': 4.,
                               'var_temporal': 2.},
                    set_cores=set_cores)


def generate_workload(num, set_tasks=True):
    return Workload(num_tasks=num,
                    ops_dist={'name': 'normal',
                              'mean': 128.,
                              'var_spatial': 32.},
                    set_tasks=set_tasks)


def generate_input(num_gen):
    num_cores = pow(2, 5)
    return {'resource': generate_resource(num_cores),
            'workload': generate_workload(num_cores * num_gen)}


if __name__ == '__main__':
    os.environ['RADICAL_DREAMER_LOG_LVL'] = 'OFF'

    print('Exp 1')
    for n_cores in [pow(10, 4), pow(10, 5), pow(10, 6), pow(10, 7)]:
        dur = []
        for _ in range(NUM_RUNS):
            time_0 = time.time()
            generate_resource(n_cores)
            dur.append(time.time() - time_0)
        dur = round(sum(dur) / len(dur), 2)
        print('  - # cores: %10s | duration: %g sec (%g min)' %
              (n_cores, dur, round(dur / 60., 2)))

    print('Exp 2')
    for n_tasks in [pow(10, 4), pow(10, 5), pow(10, 6), pow(10, 7)]:
        dur = []
        for _ in range(NUM_RUNS):
            time_0 = time.time()
            generate_workload(n_tasks)
            dur.append(time.time() - time_0)
        dur = round(sum(dur) / len(dur), 2)
        print('  - # tasks: %10s | duration: %g sec (%g min)' %
              (n_tasks, dur, round(dur / 60., 2)))

    print('Exp 3')
    for n_gens in [pow(10, 3), pow(10, 4), pow(10, 5)]:
        dur = []
        session = Session(cfg=CONFIG_DATA, is_peer=True)
        for _ in range(NUM_RUNS):
            # set number of tasks generation
            session.set(**generate_input(n_gens))
            time_0 = time.time()
            session.run()
            dur.append(time.time() - time_0)
        dur = round(sum(dur) / len(dur), 2)
        print('  - # gens: %10s | duration: %g sec (%g min)' %
              (n_gens, dur, round(dur / 60., 2)))

    # - measure duration of the sorting process -
    # dur = []
    # for _ in range(NUM_RUNS):
    #     w = generate_workload(pow(10, 6))
    #     tasks = w.tasks_list
    #     time_0 = time.time()
    #     tasks.sort(key=lambda t: t.ops, reverse=True)
    #     dur.append(time.time() - time_0)
    # dur = round(sum(dur) / len(dur), 2)
    # print('sorting: %g sec (%g min)' % (dur, round(dur / 60., 2)))
