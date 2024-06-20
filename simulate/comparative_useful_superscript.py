#!/bin/python3

# =============================================================================
# =========== COMPARING PREFETCHER RESULTS FOR MICROBENCH =====================
# =============================================================================

import os 

test = "DP1d"

result_path = f"/home/jw38176/gem5/jw38176/results/microbench_logs_new/{test}"

prefetcher1 = "DCPTPrefetcher"
prefetcher2 = "StridePrefetcher"

prefetcher_folders= [
    f
    for f in os.listdir(result_path)
    if os.path.isdir(os.path.join(result_path, f))
]

unused = []
useful = []
issued = []
unused_tick = []
useful_tick = []
issued_tick = []

prefetcher_unused = dict()
prefetcher_useful = dict()
prefetcher_issued = dict()
prefetcher_unused_tick = dict()
prefetcher_useful_tick = dict()
prefetcher_issued_tick = dict()

for prefetcher_folder in prefetcher_folders: 

    if prefetcher_folder != prefetcher1 and prefetcher_folder != prefetcher2:
        continue

    if os.path.exists(prefetcher_folder + '/run.done'):
        with open(prefetcher_folder + '/run.done', 'r') as exitcode:
            if int(exitcode.read().strip()) != 0:
                print(f'Skipped {prefetcher_folder} (Null exit code)')
                continue 
    
    with open(os.path.join(result_path, prefetcher_folder, "issued.txt"), "r") as file:
        issued = [int(line) for line in file.read().splitlines()]

    with open(os.path.join(result_path, prefetcher_folder, "unused.txt"), "r") as file:
        unused = [int(line) for line in file.read().splitlines()]
    
    with open(os.path.join(result_path, prefetcher_folder, "hit.txt"), "r") as file:
        useful =  [int(line) for line in file.read().splitlines()]
    
    with open(os.path.join(result_path, prefetcher_folder, "issued_tick.txt"), "r") as file:
        issued_tick = [int(line) for line in file.read().splitlines()]

    with open(os.path.join(result_path, prefetcher_folder, "unused_tick.txt"), "r") as file:
        unused_tick = [int(line) for line in file.read().splitlines()]
    
    with open(os.path.join(result_path, prefetcher_folder, "hit_tick.txt"), "r") as file:
        useful_tick = [int(line) for line in file.read().splitlines()]
    
    prefetcher_unused[prefetcher_folder] = unused
    prefetcher_useful[prefetcher_folder] = useful
    prefetcher_issued[prefetcher_folder] = issued
    prefetcher_unused_tick[prefetcher_folder] = unused_tick
    prefetcher_useful_tick[prefetcher_folder] = useful_tick
    prefetcher_issued_tick[prefetcher_folder] = issued_tick

print("Completed reading files")

prefetcher_list = list(prefetcher_unused.keys())

unique_useful1 = [] 
unique_useful2 = []

unique_useful1_final = []
unique_useful2_final = []

unique_useful1_tick = []
unique_useful2_tick = []
unique_useful1_timeliness = []
unique_useful2_timeliness = []

# Get the unique hits between the two prefetchers
for i in range(len(prefetcher_useful[prefetcher1])):
    for j in range(len(prefetcher_useful[prefetcher2])):
        if prefetcher_useful[prefetcher1][i] == prefetcher_useful[prefetcher2][j]:
            prefetcher_useful[prefetcher2][j] = None
            prefetcher_useful[prefetcher1][i] = None

for i in range(len(prefetcher_useful[prefetcher1])):
    if prefetcher_useful[prefetcher1][i] != None:
        unique_useful1.append(int(prefetcher_useful[prefetcher1][i]))
        unique_useful1_tick.append(int(prefetcher_useful_tick[prefetcher1][i]))

for i in range(len(prefetcher_useful[prefetcher2])):
    if prefetcher_useful[prefetcher2][i] != None:
        unique_useful2.append(int(prefetcher_useful[prefetcher2][i]))
        unique_useful2_tick.append(int(prefetcher_useful_tick[prefetcher2][i]))

print("Completed unique extraction")

for i in range(len(unique_useful1)):
    for j in range(len(prefetcher_issued[prefetcher1])):
        if prefetcher_issued[prefetcher1][j] <= unique_useful1[i] and prefetcher_issued[prefetcher1][j] + 8 > unique_useful1[i]:
            timeliness = unique_useful1_tick[i] - int(prefetcher_issued_tick[prefetcher1][j])
            if timeliness > 0:
                unique_useful1_timeliness.append(timeliness)
                unique_useful1_final.append(unique_useful1[i])

            break

print("Completed first prefetcher comparison")

for i in range(len(unique_useful2)):
    for j in range(len(prefetcher_issued[prefetcher2])):
        if prefetcher_issued[prefetcher2][j] <= unique_useful2[i] and prefetcher_issued[prefetcher2][j] + 8 > unique_useful2[i]:
            timeliness = unique_useful2_tick[i] - int(prefetcher_issued_tick[prefetcher2][j])
            if timeliness > 0:
                unique_useful2_timeliness.append(timeliness)
                unique_useful2_final.append(unique_useful2[i])
            break

print("Completed second prefetcher comparison")


# =============================================================================
# =========== RUNNING EXPERIMENT TO REMOVE INDIVIDUAL PREFETCHES ==============
# =============================================================================

import argparse
import os
import sys
import glob
from microbench_def import *
from prefetcher_def import *
import multiprocessing
import subprocess

parser = argparse.ArgumentParser(
    prog='Kernel for launching gem5 simulations',
    description='Runs sub-benchmarks in parallel through gem5 O3')

parser.add_argument('--gem5dir',
    type=str,
    default="/home/jw38176/gem5/",
    help='Path to gem5 executable to be used')

parser.add_argument('--benchmark',
    type=str,
    default="cjpeg",
    help='Name of benchamrk to run')

parser.add_argument('--ext',
    type=str,
    default="none",
    help='Name of file extension to the output')

parser.add_argument('--resultdir',
    type=str,
    default="/home/jw38176/gem5/jw38176/results/microbench_useful",
    help='Path to results directory')

parser.add_argument('-j', '--jobs',
    type=int,
    default=multiprocessing.cpu_count() - 2,
    help='Number of jobs to run in parallel')

parser.add_argument('--log',
    action='store_true',
    default=False,
    help='Enable logging of gem5 output')

args = parser.parse_args()

#Ensure absolute paths
args.gem5dir = os.path.abspath(args.gem5dir)

run_commands = []

workload_paths = [
    f for f in os.listdir(MICROBENCH_PATH) 
    if os.path.isdir(os.path.join(MICROBENCH_PATH, f))
]

run_commands = []


prefetcher = prefetcher2 if (len(unique_useful1_final) == 0) else prefetcher1
comp_prefetcher = prefetcher1 if (len(unique_useful1_final) == 0) else prefetcher2
removed_prefetch_targets = unique_useful1_final if (len(unique_useful1_final) != 0) else unique_useful2_final
removed_prefetch_targets_tick = unique_useful1_timeliness if (len(unique_useful1_final) != 0) else unique_useful2_timeliness

for workload in workload_paths:

    if workload != test:
        continue

    for i, removed_prefetch_target in enumerate(removed_prefetch_targets):

        workload_path = os.path.join(MICROBENCH_PATH, workload)

        result_dir = f"{args.resultdir}/{test}/{prefetcher}/comp_{comp_prefetcher}_{i}"

        if os.path.exists(result_dir + '/run.done'):
            with open(result_dir + '/run.done', 'r') as exitcode:
                if int(exitcode.read().strip()) == 0:
                    print(f'Skipped {result_dir} (run.done with code 0)')
                    continue 

        if not os.path.exists(result_dir):
            os.makedirs(result_dir)


        run_command = []
        run_command.extend([
            f'{args.gem5dir}/build/X86/gem5.opt'])

        # run_command.extend(['--debug-flags=CoverageDebug,PrefetchAddr'])

        run_command.extend([

            # gem5 options
            f'--outdir={result_dir}',

            f'{args.gem5dir}/configs/example/se.py',
            '-c', f'{workload_path}/bench.X86',
            f'--mem-size=8GB',

            '--cpu-type=X86O3CPU',
            '--caches',
            '--l2cache',
            '--l1d_size=64KiB',
            '--l1i_size=64KiB',
            '--l2_size=1MB'
        ])

        if prefetcher != "None":
            run_command.append(f'--l1d-hwp-type={prefetcher}')

        run_commands.append((run_command, result_dir, removed_prefetch_target, removed_prefetch_targets_tick[i]))

def list_to_str(l):
    return ','.join(str(x) for x in l)


def exec_gem5_kernel(run_command):

    command, result_dir, removed_prefetch_target, removed_prefetch_target_tick = run_command

    # Export env variables
    os.environ['REMOVED_PREFETCH_TARGET'] = str(removed_prefetch_target)

    with open(result_dir + "/run.log", 'w+') as log:
        log.write(' '.join(command))
        process = subprocess.Popen(command, stdout=log, stderr=log)
        (output, err) = process.communicate()  
        p_status = process.wait()
    
    with open(result_dir + "/run.done", 'w+') as statusf:
        statusf.write(str(p_status))
    
    with open(result_dir + "/target.txt", 'w+') as targetf:
        targetf.write(str(removed_prefetch_target))

    with open(result_dir + "/timeliness.txt", 'w+') as timelinessf:
        timelinessf.write(str(removed_prefetch_target_tick))
    
    print(f"Finished {result_dir} with exit code {p_status}")

# exec_gem5_kernel(run_commands[0])

#Execute commands in parallel with pool
pool = multiprocessing.Pool(args.jobs)

with pool:
    pool.map(exec_gem5_kernel, run_commands)

print("Done")

# =============================================================================
# =========== ANALYZING RESULTS AND PLOTTING ==================================
# =============================================================================

import re

result_path = f"{args.resultdir}/{test}/{prefetcher}"

ipc_pattern = r"system.cpu.ipc\s+(\d+\.\d+).*"

test_folders= [
    f
    for f in os.listdir(result_path)
    if os.path.isdir(os.path.join(result_path, f))
]

dat_file_data = ""

ipc_list = []

for test in test_folders: 

    test = os.path.join(result_path, test)

    if os.path.exists(test + '/run.done'):
        with open(test + '/run.done', 'r') as exitcode:
            if int(exitcode.read().strip()) != 0:
                print(f'Skipped {test} (Null exit code)')
                continue

    if os.path.exists(test + '/target.txt'):
        with open(test + '/target.txt', 'r') as removed_prefetch_target:
            removed_prefetch_target = int(removed_prefetch_target.read().strip())
    else:
        print(f'Skipped {test} (No target.txt)')
        continue

    if os.path.exists(test + '/timeliness.txt'):
        with open(test + '/timeliness.txt', 'r') as removed_prefetch_target_tick:
            removed_prefetch_target_tick = int(removed_prefetch_target_tick.read().strip())
    else:
        print(f'Skipped {test} (No timeliness.txt)')
        continue

    with open(os.path.join(result_path, test, "stats.txt"), "r") as file:

        for line in file:

            match = re.search(ipc_pattern, line)

            if match:
                ipc = float(match.group(1))
                break

        else:
            print("IPC not found for" + os.path.join(result_path, prefetcher_folder, "stats.txt"))
            continue
    
    ipc_list.append((removed_prefetch_target_tick, ipc))
    
ipc_list.sort(key=lambda x: x[0])

# Generate dat file data
for tick, ipc in ipc_list:
    dat_file_data += f"{tick} {ipc}\n"

# Write to dat file
with open(f"{result_path}/useful_timeliness.dat", 'w+') as dat_file:
    dat_file.write(dat_file_data)

# Generate plot script
plot_script = f"""
set terminal pngcairo size 1000, 500
set output '{result_path}/useful_timeliness.png'
        
set style data histogram 
set style fill solid border -1

set ytics nomirror
set xtics nomirror

set xtics rotate by -45
set boxwidth 1.4
set key off
set yrange [*:*]

set ylabel "IPC Improvement (%)"
set xlabel "Timeliness (Ticks/Count)"

plot '{result_path}/useful_timeliness.dat' using 2:xtic(1) linecolor rgb "#0080ff"

"""

# Save plot script to file
with open(f"{result_path}/useful_timeliness.gp", "w+") as file:
    file.write(plot_script)

# Call gnuplot
os.system(f"gnuplot {result_path}/useful_timeliness.gp")

print("Done")
