import sympy
from sympy.stats import UniformSum, density, cdf

# configuration
res_size = 128
wl_size = 8192
task_length_mean = 1024
core_perf = 32
het = 0.5
sensitivity = 100

task_exec_time_mean = task_length_mean/core_perf
gen = int(wl_size/res_size)
cdf_val = np.power(0.5,1/res_size)

# calculate thr (value of x in Irwin-Hall CDF) P(max(TTX_j)<x)=0.5
range_val = sensitivity * gen
min_val = 1
thr = gen * 1.0
for x in range(range_val):
    tmp = cdf(UniformSum("x", gen), evaluate=False)(x/sensitivity).doit()
    tmp_diff = np.absolute(tmp-cdf_val)
    if(tmp_diff < min_val):
        min_val = tmp_diff
        thr = x/sensitivity
print(thr)

# transformation from a U(0,1) distribution to U(a,b) distribution
ttx = task_exec_time_mean * (1-het) * gen + task_exec_time_mean * het * 2 * thr
print(ttx)
