# RADICAL-DREAMER: Dynamic REsource and Adaptive Mapping EmulatoR

## Requirements

* Python 3.6 and higher with the following libraries:
  * [radical.utils](https://github.com/radical-cybertools/radical.utils) 1.4.1 
  and higher (temporary should be used a branch that is under development: 
  `pip install git+https://github.com/radical-cybertools/radical.utils.git@feature/config_inheritance`)
  * numpy
  * pika
* RabbitMQ

## Executing of provided example
Setup RabbitMQ URL at each terminal where executable runs (NOTE: this env 
variable is not needed if the corresponding URL is set in the config using 
either Config class or JSON file)
```shell script
export RADICAL_DREAMER_RMQ_URL="amqp://localhost:5672/"
```
Run ResourceManager (1st terminal)
```shell script
bin/radical-dreamer-start-manager resource
```
Run WorkloadManager (2nd terminal)
```shell script
bin/radical-dreamer-start-manager workload
```
Run Session (3rd terminal), set Resource and Workload descriptions
```shell script
examples/run_session.py
```

## Config parameters
Configuration parameters could be set by using the corresponding class:
```python
from radical.dreamer import Config, Session

cfg_data = {
    'rabbitmq': {
        'url': 'amqp://localhost:5672/',
        'exchange': 'rd_rdcl_857',
        'queues': {
            'allocation': 'allocation_rdcl_857',
            'request': 'request_rdcl_857',
            'resource': 'resource_rdcl_857',
            'schedule': 'schedule_rdcl_857',
            'session': 'session_rdcl_857',
            'workload': 'workload_rdcl_857'
        }
    },
    'session': {
        'output_profile': './profile.json',
        'schedule_options': ['smallest_to_fastest'],
        'early_binding': True,
        'dynamic_resource': True
    }
}
session = Session(cfg=Config(cfg_data))
```
Another option is to have all that parameters in the dedicated JSON file (e.g
., `examples/config_data.json`). And below, there are examples of using
 such JSON file as config.
```shell script
# run ResourceManager
bin/radical-dreamer-start-manager resource --cfg_path examples/config_data.json
# run WorkloadManager
bin/radical-dreamer-start-manager workload --cfg_path examples/config_data.json
```
```python
from radical.dreamer import Config, Session

session_1 = Session(cfg_path='./config_data.json')
session_2 = Session(cfg=Config(cfg_path='./config_data.json'))
```

## Examples of Resource and Workflow definition
The following examples of values distributions are applied for both, `Resource` 
and `Workload`, the same way. More important is the meaning, which user put into
these descriptions.

### Resource
1) Cores performance follows a "general" distribution (`number: 36, perf: 
normal distr {mean: 10., var: 2.}`)
```python
resource = Resource(num_cores=36,
                    perf_dist={'name': 'normal',
                               'mean': 10.,
                               'var': 2.})
```
2) Each core performance follows its own version of distribution (`number: 36, 
perf: normal distr {mean: 10., var: 2.}`)
```python
resource = Resource(num_cores=36,
                    perf_dist={'name': 'normal',
                               'mean': 10.,
                               'var_local': 2.})
```
3) Mean value for each core performance follows a "general" distribution and 
each core performance follows its own version of distribution (`number: 36, 
perf: normal distr {mean: 10., var: general -> 2., personal -> 3.}`)
```python
resource = Resource(num_cores=36,
                    perf_dist={'name': 'normal',
                               'mean': 10.,
                               'var': 2.,
                               'var_local': 3.})
```
NOTE: For `poisson` distribution, parameters `var` and `var_local` are used 
as flags only, their values are not taken into account:
```
var=1. -> True: poisson distribution produces mean values for cores performance
var_local=1. -> True: poisson distribution produces values as a personal 
distribution (each core has its own version of distribution)
```
4) Heterogeneous resource or resource with multiple distributions (`total
 number: 25, perf: 20 cores with normal distr and 5 cores with uniform distr`)
```python
resource = MultiResource(resources=[
        {'num_cores': 20,
         'perf_dist': {'name': 'normal',
                       'mean': 5.,
                       'var': 2.,
                       'var_local': 1.}},
        {'num_cores': 5,
         'perf_dist': {'name': 'uniform',
                       'mean': 10.}}
    ])
```

### Workload
1) Homogeneous tasks (`number: 128, ops: 10.`)
```python
workload = Workload(num_tasks=128,
                    ops_dist={'name': 'uniform',
                              'mean': 10.})
```
2) Heterogeneous tasks (`number: 128, ops: normal distr {mean: 5., var: 2.}`)
```python
workload = Workload(num_tasks=128,
                    ops_dist={'name': 'normal',
                              'mean': 5.,
                              'var': 2.})
```
