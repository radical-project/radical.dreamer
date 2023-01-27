
0.4.0 Release                                                        202x-xx-xx
--------------------------------------------------------------------------------


0.3.0 Release                                                        2021-04-29
--------------------------------------------------------------------------------

  - Added possibility to run emulator without RMQ (peer mode: 
    `session = Session(.., is_peer=True)`)
    - Reorganized run procedure (`run` method) for `ResourceManager`
  - Improved procedure of collecting `Core` performance history
  - Reworked processes of task binding and handling
  - Added possibility to control when `Core`/`Task` objects are generated 
    within `Resource`/`Workload` respectively
  - Added possibility to re-set (re-generate) `Core`/`Task` objects
  - New attribute `size` that reflects the size of `Resource`/`Workload`, 
    while `num_cores`/`num_tasks` either `0` (if no objects) or equal to `size` 
    (if objects are generated)
  - Updated procedure of defining `Resource` and `Workload` objects at `Session`
  - Moved profile collection from `ResourceManager` to `Session`
  - Fixed logging
  - Updated wrapper for RabbitMQ
  - Support the latest version of `radical.utils` package (`Munch` module)
  - Dynamic resource is defined with temporal variation (parameter 
    `var_temporal`), same approach can be extended to workload
  - Updated and extended methods for all key classes
  - Updated name of the project
  - Updated and extended examples and readme
  - Added tests and code coverage estimation


0.2.0 Release                                                        2020-12-24
--------------------------------------------------------------------------------

  - new module `Schedule`, which is responsible for the selection and ordering 
    of `Core` and `Task` objects, and for the binding process (assigning 
    `Core` to `Task`)
  - new approach of defining heterogeneity and dynamism (dynamism is applied to 
    `Resource` objects only): spatial variance `var_spatial` is used to 
    calculate `task.ops` and `core.perf` in case of heterogeneity, temporal 
    variance `var_temporal` is used to calculate `core.perf_dynamic` right 
    before task processing
  - added tracking for the core availability (with `resource.next_idle_cores`)
  - profile data collection is moved to the `Session`
  - class `WorkloadManager` is obsolete
  - updated config schemas accordingly and added support of the version of 
    `radical.utils` v1.5.7 (`Munch` module)
