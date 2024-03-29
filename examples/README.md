## Examples of running RADICAL-DREAMER (RD)

There are two modes to run the emulation:
 * `peer` mode (without communication channel)
 * `client/server` mode (with RabbitMQ as a communication channel)

### (a) Peer mode
Run the example of Session, which sets Resource and Workload descriptions, and 
then starts the processing/emulation.
```shell script
# firstly activate corresponding virtualenv
wget -q https://raw.githubusercontent.com/radical-project/radical.dreamer/master/examples/run_session_peer.py
# (!) for devel branch:
# wget -q https://raw.githubusercontent.com/radical-project/radical.dreamer/devel/examples/run_session_peer.py
chmod +x run_session_peer.py

./run_session_peer.py
# or with debug messages (provided example already includes flag for debug messages):
#    RADICAL_DREAMER_LOG_LVL=DEBUG ./run_session_peer.py
```
NOTE: This mode is not set by default and should be defined explicitly during 
`Session` initialization (use corresponding flag: `is_peer=True`)

### (b) Client/server mode (default)
Export RabbitMQ URL at each terminal where executable runs
```shell script
export RADICAL_DREAMER_RMQ_URL="amqp://localhost:5672/"
```
NOTE (1): This env variable is not needed if the corresponding URL is set in 
the config using either the class `Config` or JSON file

NOTE (2): Provided RabbitMQ URL is a default value, and it is for the local 
installation of RabbitMQ. If remotely installed RabbitMQ is used, then, please, 
set the URL of the following format (username/password are optional)
`"amqp://<username>:<password>@<host>:<port>/"` 
([official docs](https://www.rabbitmq.com/uri-spec.html))

Run ResourceManager (1st terminal)
```shell script
# firstly activate corresponding virtualenv
radical-dreamer-start-manager
# or with debug messages:
#    RADICAL_DREAMER_LOG_LVL=DEBUG radical-dreamer-start-manager
```
Run the example of Session (2nd terminal), which sets Resource and Workload 
descriptions
```shell script
# firstly activate corresponding virtualenv
wget -q https://raw.githubusercontent.com/radical-project/radical.dreamer/master/examples/run_session.py
# (!) for devel branch:
# wget -q https://raw.githubusercontent.com/radical-project/radical.dreamer/devel/examples/run_session.py
chmod +x run_session.py

./run_session.py
# or with debug messages (provided example already includes flag for debug messages):
#    RADICAL_DREAMER_LOG_LVL=DEBUG ./run_session.py
```

## Config parameters
Configuration parameters could be set by using the corresponding class:
```python
from radical.dreamer import Config, Session

cfg_data = {
    'rabbitmq': {
        'url': 'amqp://localhost:5672/'
    },
    'session': {
        'profile_base_name': 'rd.profile'
    },
    'schedule': {
        'strategy': 'smallest_to_fastest',
        'early_binding': True
    }
}
session = Session(cfg=Config(cfg_data))
```
Another option is to have all that parameters in the dedicated JSON file (e.g., 
`examples/config_data.json`). And below, there are examples of using such JSON 
file as config.
```shell script
# run ResourceManager (for client/server mode)
radical-dreamer-start-manager --cfg_path examples/config_data.json
```
```python
from radical.dreamer import Config, Session

session_1 = Session(cfg_path='./config_data.json')
session_2 = Session(cfg=Config(cfg_path='./config_data.json'))
```

## Examples of Resource and Workload definition
The following examples of values distributions are applied for both, `Resource` 
and `Workload`, the same way. More important is the meaning, which user put into
these descriptions.

### Resource
1) Homogeneous resource/cores (`number: 36, perf: 16.`)
```python
resource = Resource(num_cores=36,
                    perf_dist={'mean': 16.})
```
2) Heterogeneous resource with normal distribution of cores performance 
(`number: 36, perf: normal distr {mean: 16., spatial variance: 4.}`)
```python
resource = Resource(num_cores=36,
                    perf_dist={'name': 'normal',
                               'mean': 16.,
                               'var_spatial': 4.})
```
3) Homogeneous resource with dynamism, i.e., dynamic resource (`number: 36, 
perf: normal distr {mean: 16., temporal variance: 2.}`)
```python
resource = Resource(num_cores=36,
                    perf_dist={'name': 'normal',
                               'mean': 16.,
                               'var_temporal': 2.})
```
4) Heterogeneous dynamic resource with normal distribution of cores performance 
(`number: 36, perf: normal distr {mean: 16., spatial variance: 4., temporal 
variance: 2.}`)
```python
resource = Resource(num_cores=36,
                    perf_dist={'name': 'normal',
                               'mean': 16.,
                               'var_spatial': 4.,
                               'var_temporal': 2.})
```
5) Multiple resources or resource with multiple distributions (`total number: 
25, 20 heterogeneous dynamic cores with normal distr and 5 homogeneous cores`)
```python
resource = MultiResource(resources=[{'num_cores': 20,
                                     'perf_dist': {'name': 'normal',
                                                   'mean': 8.,
                                                   'var_spatial': 2.,
                                                   'var_temporal': 1.}},
                                    {'num_cores': 5,
                                     'perf_dist': {'mean': 10.}}])
```
6) Additional parameter(s) for resource definition
 - `io_rate` (`float`) - I/O abstraction to add time for task spent on I/O
  processes (assume that I/O includes data transfers and network throughput)

NOTE: There are 3 types of distributions used: `uniform`, `normal` and
`poisson`. For `poisson` distribution, parameters `var_spatial` and 
`var_temporal` are used as flags only, their actual values are not taken into 
account (`var_spatial=1. -> True`, `var_temporal=1. -> True`)

### Workload
1) Homogeneous tasks (`number: 128, ops: 10.`)
```python
workload = Workload(num_tasks=128,
                    ops_dist={'mean': 10.})
```
2) Heterogeneous tasks (`number: 128, ops: normal distr {mean: 32., 
spatial variance: 8.}`)
```python
workload = Workload(num_tasks=128,
                    ops_dist={'name': 'normal',
                              'mean': 32.,
                              'var_spatial': 8.})
```
