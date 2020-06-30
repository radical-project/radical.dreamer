# RADICAL-DREAMER: Dynamic Resource and Adaptive Mapping EmulatoR

## Requirements

* Python 3.5 and higher with the following libraries:
  * [radical.utils](https://github.com/radical-cybertools/radical.utils) 1.4.1 and higher (temporary should be used a brunch that is under development: `pip install git+https://github.com/radical-cybertools/radical.utils.git@feature/config_inheritance`)
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
