# RADICAL-DREAMER: Dynamic Runtime and Execution Adaptive Middleware EmulatoR (RD)

[![Build](https://github.com/radical-project/radical.dreamer/actions/workflows/ci.yml/badge.svg)](https://github.com/radical-project/radical.dreamer/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/radical-project/radical.dreamer/branch/devel/graph/badge.svg)](https://codecov.io/gh/radical-project/radical.dreamer)


## Requirements

* Python 3.6+ with the following libraries:
  * [radical.utils](https://github.com/radical-cybertools/radical.utils)
  * `numpy`
  * `pika` **[optional]**
    * it would be necessary if processes of input setup and actual emulation 
      process are separated either within a local machine or between different 
      machines and RabbitMQ is used as a communication channel, thus RabbitMQ 
      instance should be installed and *running* either locally or remotely

## Installation

1) Virtual environment
```shell script
# python3 virtualenv
python3 -m venv ./dreamer
source ./dreamer/bin/activate
```
OR
```shell script
# conda virtualenv
conda create -n dreamer python=3.7 -y
conda activate dreamer
```
2) `radical.dreamer` package
```shell script
pip install git+https://github.com/radical-project/radical.dreamer.git
```
NOTE: For test purposes to have the latest (**unstable**) version please use 
the `devel` branch
```shell script
pip install git+https://github.com/radical-project/radical.dreamer.git@devel
```

## Examples

Please check the corresponding directory ([examples/](examples/)) 
