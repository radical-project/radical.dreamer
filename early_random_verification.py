# this code is to verify radical.dreamer results 
# for early binding random selection


import scipy.stats as stats
from scipy.stats import skewnorm
import numpy as np

# set the distribution type (default: Uniform) 
distType = "Uniform"

# configuration
res_size = 128
core_perf_mean = 32
core_perf_var = 0
core_perf_dyn_var = 8

wl_size = 8192
task_length_mean = 1024
task_length_var = 0

number_of_trial = 64


task_exec_time_mean = task_length_mean/core_perf_mean
gen = int(wl_size/res_size)


ttx = []
for i in range(number_of_trial):
    if task_length_var == 0:
        task_length_list = np.linspace(task_length_mean, task_length_mean, num=wl_size)
    else:
        task_length_list = []
        if distType == "Normal":
            X = stats.truncnorm(-1.28, 1.28, loc=task_length_mean, scale=task_length_var)
            task_length_list = list(X.rvs(wl_size))
        else:
            task_length_list = list(np.random.uniform(task_length_mean - task_length_var,
                                        task_length_mean + task_length_var,
                                        wl_size))
    #print(task_length_list)

    if core_perf_var == 0:
        core_perf_list = np.linspace(core_perf_mean, core_perf_mean, num=res_size)
    else:
        core_perf_list = []
        if distType == "Normal":
            X = stats.truncnorm(-1.28, 1.28, loc=core_perf_mean, scale=core_perf_var)
            core_perf_list = list(X.rvs(res_size))
        else:
            core_perf_list = list(np.random.uniform(core_perf_mean - core_perf_var,
                                         core_perf_mean + core_perf_var,
                                         res_size))
    #print(core_perf_list)

    exec_time = []
    for core_id in range(res_size):
        gen_id = 0 
        core_exec_time = 0
        for gen_id in range(gen):
            task_id = core_id + gen_id * res_size
            if core_perf_dyn_var > 0:
                if distType == "Normal":
                    X = stats.truncnorm(-1.28, 1.28, loc=core_perf_list[core_id], scale=core_perf_dyn_var)
                    current_core_perf = list(X.rvs(1))[0]
                else:
                    current_core_perf = np.random.uniform(core_perf_list[core_id] - core_perf_dyn_var,
                                                 core_perf_list[core_id] + core_perf_dyn_var,1)[0]  
                #print('current_core_perf', current_core_perf)
                core_exec_time = core_exec_time + task_length_list[task_id]/current_core_perf
            else:
                core_exec_time = core_exec_time + task_length_list[task_id]/core_perf_list[core_id]    
            #print(core_exec_time)
            gen_id = gen_id+1
        exec_time.append(core_exec_time)
        
    ttx.append(np.max(exec_time))


print(ttx)
print(np.mean(ttx))
print(np.std(ttx))
