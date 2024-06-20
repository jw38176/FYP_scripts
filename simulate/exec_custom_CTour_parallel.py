#!/bin/python3

# This script runs all the prefetchers in parallel for a single test in coremark 

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
    default="/home/jw38176/gem5/jw38176/results/microbench_ctour_delay",
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


prefetcher = "CoverageTournamentPrefetcher"

for workload in workload_paths:

    workload_path = os.path.join(MICROBENCH_PATH, workload)

    result_dir = f"{args.resultdir}/{workload}/CTour_{args.ext}"

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

    if args.log:
        run_command.extend(['--debug-flags=CoverageDebug'])

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

    run_commands.append((run_command, result_dir))

def exec_gem5_kernel(run_command):

    command, result_dir = run_command

    with open(result_dir + "/run.log", 'w+') as log:
        log.write(' '.join(command))
        process = subprocess.Popen(command, stdout=log, stderr=log)
        (output, err) = process.communicate()  
        p_status = process.wait()
    
    with open(result_dir + "/run.done", 'w+') as statusf:
        statusf.write(str(p_status))
    
    print(f"Finished {result_dir} with exit code {p_status}")

# exec_gem5_kernel(run_commands[0])

#Execute commands in parallel with pool
pool = multiprocessing.Pool(args.jobs)

with pool:
    pool.map(exec_gem5_kernel, run_commands)

print("Done")

