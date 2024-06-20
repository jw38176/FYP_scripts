#!/bin/python3

import os 
import re 
from helper import *
from prefetcher_def import *

results_folder = "/home/jw38176/gem5/jw38176/results/coremark"
# output_folder = "/home/jw38176/gem5/jw38176/graphs"

ipc_pattern = r"system.cpu.ipc\s+(\d+\.\d+).*"
hit_pattern = r"system.cpu.dcache.prefetcher.pfHitInCache\s+(\d+).*"
verbose = False
enable_sort = True
    
# Create output folder if it does not exist
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# Get all folders in the results folder
folders = [
    f
    for f in os.listdir(results_folder)
    if os.path.isdir(os.path.join(results_folder, f))
]

for result in folders:

    result_path = os.path.join(results_folder, result)

    prefetcher_folders= [
        f
        for f in os.listdir(result_path)
        if os.path.isdir(os.path.join(result_path, f))
    ]

    dat_file_data = ""
    ipc_list = []
    hit_list = []

    for prefetcher_folder in prefetcher_folders: 

        if os.path.exists(prefetcher_folder + '/run.done'):
            with open(prefetcher_folder + '/run.done', 'r') as exitcode:
                if int(exitcode.read().strip()) != 0:
                    print(f'Skipped {prefetcher_folder} (Null exit code)')
                    continue 

        ipc = 0
        coverage = 0

        with open(os.path.join(result_path, prefetcher_folder, "stats.txt"), "r") as file:

            for line in file:

                match_ipc = re.search(ipc_pattern, line)
                match_hit = re.search(hit_pattern, line)

                if match_ipc:
                    ipc = float(match_ipc.group(1))
                    if verbose: print(f"IPC: {ipc}")
                    
                if match_hit:
                    coverage = float(match_hit.group(1))
                    if verbose: print(f"Coverage: {coverage}")
        
        ipc_list.append((prefetcher_folder, ipc))
        hit_list.append((prefetcher_folder, coverage))
    
    if enable_sort:
        ipc_list.sort(key=lambda x: x[1], reverse=False)
        # Sort coverage list based on ipc_list[0]
        # coverage_list.sort(key=lambda x: x[1], reverse=False)
        sorted_ipc_list_string = ""
        for prefetcher, ipc in ipc_list:
            sorted_ipc_list_string += f"{prefetcher_shorthand[prefetcher]}(), "
        print(f"Sorted IPC list: {sorted_ipc_list_string}")

    for prefetcher, ipc in ipc_list:
        # Find coverage for the same prefetcher
        hits = 0
        for hit_prefetcher, hit in hit_list:
            if hit_prefetcher == prefetcher:
                hits = hit
                break
        dat_file_data += f"{prefetcher_shorthand[prefetcher]} {ipc} {hits}\n"
        
    # Generate dat file  
    with open(os.path.join(result_path, f"{result}.dat"), "w+") as file:
        file.write(dat_file_data)

# Generate plot script
plot_script = f"""

set terminal pngcairo size 1800,1200
set output '{results_folder}/hits_ipc.png'

set multiplot layout 3, 3 
        
set style data histograms
set style histogram cluster gap 1
set style fill solid border -1

set xtics rotate by -45
set boxwidth 0.9
# set key off
set key autotitle columnheader
set key inside top left 
set y2tics
set ytics nomirror
set xtics nomirror

set yrange [*:*]
set y2range [*:*]

set ylabel "IPC"
set y2label "Hits"
set xlabel "Prefetchers"


# set key outside center bottom horizontal

""" 

for i, result in enumerate(folders):
    plot_script += f"""
set title "{result}" 
plot '{results_folder}/{result}/{result}.dat' using 2:xtic(1) title 'IPC' axes x1y1 linecolor rgb "#5397d4", '' using 3:xtic(1) title 'Hits' axes x1y2 linecolor rgb "#d9534f"
\n"""

plot_script += "unset multiplot\n"


# Save plot script to file
with open(f"{results_folder}/plot_hits_ipc.gp", "w+") as file:
    file.write(plot_script)

# Call gnuplot
os.system(f"gnuplot {results_folder}/plot_hits_ipc.gp")

print("Done")


