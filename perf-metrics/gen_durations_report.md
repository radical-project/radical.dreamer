# Duration metrics (with focus on `rd.units`)

---

## Using `radical.utils.v.1.9.1` and comparison of `ru.Munch` vs `TypedDict`
(*) `TypedDict` is a new module (alpha-version.20220107) to replace `ru.Munch`

- RADICAL-DREAMER v.0.3.1-devel (74bb2a9)
- CPUx1: 2.3GHz 8-Core Intel Core i9; MEM: 32GB
- Metric values are AVG from 5 runs for each experiment setup

### Resource creation with N cores

| N cores, x1000 | Duration (M vs TD), sec | Duration (M vs TD), min |
|---------------:|------------------------:|------------------------:|
|             10 |           0.34 /   0.32 |             0.01 / 0.01 |
|            100 |           3.70 /   3.46 |             0.06 / 0.06 |
|           1000 |          36.52 /  32.91 |             0.61 / 0.55 |
|         10,000 |         396.55 / 321.80 |             6.61 / 5.36 |

### Workload creation with N tasks

| N tasks, x1000 | Duration (M vs TD), sec | Duration (M vs TD), min |
|---------------:|------------------------:|------------------------:|
|             10 |           0.24 /   0.18 |             0.00 / 0.00 |
|            100 |           2.61 /   1.72 |             0.04 / 0.03 |
|           1000 |          25.49 /  18.23 |             0.42 / 0.30 |
|         10,000 |         255.73 / 187.22 |             4.26 / 3.12 |

### Session run (peer mode) with N generations of tasks
(*) For `32` (`2^5`) cores there are `32 x N` tasks,
and only `session.run()` method call is measured 
(`cores` and `tasks` are generated before the call)

| N generations | Duration (M vs TD), sec | Duration (M vs TD), min |
|--------------:|------------------------:|------------------------:|
|          1000 |          7.77 /    6.38 |            0.13 /  0.11 |
|        10,000 |         79.61 /   72.40 |            1.33 /  1.21 |
|       100,000 |       2662.88 / 2536.61 |           44.38 / 42.28 |

---

## Using `radical.utils.v.1.6.5` and `ru.Munch`

- RADICAL-DREAMER v.0.3.0
- CPUx1: 2.3GHz 4-Core Intel Core i5; MEM: 16GB
- Metric values are AVG from 5 runs for each experiment setup

### Resource creation with N cores

| N cores, x1000 | Duration, sec | Duration, min |
|---------------:|--------------:|--------------:|
|             10 |          0.45 |          0.01 |
|            100 |          4.11 |          0.07 |
|           1000 |         43.29 |          0.72 |

### Workload creation with N tasks

| N tasks, x1000 | Duration, sec | Duration, min |
|---------------:|--------------:|--------------:|
|             10 |          0.29 |             0 |
|            100 |          2.96 |          0.05 |
|           1000 |         29.91 |          0.50 |
|         10,000 |        328.91 |          5.48 |

### Session run (peer mode) with N generations of tasks
(*) For `32` (`2^5`) cores there are `32 x N` tasks,
and only `session.run()` method call is measured 
(`cores` and `tasks` are generated before the call)

| N generations | Duration, sec | Duration, min |
|--------------:|--------------:|--------------:|
|          1000 |         10.61 |          0.18 |
|        10,000 |        117.26 |          1.95 |
|       100,000 |       3038.17 |         50.64 |

---
