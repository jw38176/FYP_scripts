#!/bin/python3

import os 
import re 
from helper import *
from prefetcher_def import *

results_folder = "/home/jw38176/gem5/jw38176/results/coremark_logs"
# output_folder = "/home/jw38176/gem5/jw38176/graphs"

ipc_pattern = r"system.cpu.ipc\s+(\d+\.\d+).*"
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

    if result == ".git":
        continue

    result_path = os.path.join(results_folder, result)

    prefetcher_folders= [
        f
        for f in os.listdir(result_path)
        if os.path.isdir(os.path.join(result_path, f))
    ]

    dat_file_data = ""
    ipc_list = []

    for prefetcher_folder in prefetcher_folders: 

        ipc = 0

        with open(os.path.join(result_path, prefetcher_folder, "stats.txt"), "r") as file:

            for line in file:

                match = re.search(ipc_pattern, line)

                if match:
                    ipc = float(match.group(1))
                    if verbose: print(f"IPC: {ipc}")
                    break

            else:
                print("IPC not found for" + os.path.join(result_path, prefetcher_folder, "stats.txt"))
                continue
        
        ipc_list.append((prefetcher_folder, ipc))
    
    if enable_sort:
        ipc_list.sort(key=lambda x: x[1], reverse=False)
        sorted_ipc_list_string = ""
        for prefetcher, ipc in ipc_list:
            sorted_ipc_list_string += f"{prefetcher_shorthand[prefetcher]}(), "
        print(f"Sorted IPC list: {sorted_ipc_list_string}")

    for prefetcher, ipc in ipc_list:
        dat_file_data += f"{prefetcher_shorthand[prefetcher]} {ipc}\n"
        
    # Generate dat file  
    with open(os.path.join(result_path, f"{result}.dat"), "w+") as file:
        file.write(dat_file_data)

# Generate plot script
plot_script = f"""
set terminal pngcairo size 1600,1200
set output '{results_folder}/ipc.png'

set multiplot layout 3, 3 title "Coremark IPC" 
        
set style data histograms
set style histogram cluster gap 1
set style fill solid border -1

set ytics nomirror
set xtics nomirror

set xtics rotate by -45
set boxwidth 0.9
set key off
set yrange [*:*]

set ylabel "IPC"
set xlabel "Prefetchers"

""" 

for result in folders:
    plot_script += f"""
set title "{result}"
plot '{results_folder}/{result}/{result}.dat' using 2:xtic(1) linecolor rgb "#5397d4"
\n"""

plot_script += "unset multiplot"

# Save plot script to file
with open(f"{results_folder}/plot_ipc.gp", "w+") as file:
    file.write(plot_script)

# Call gnuplot
os.system(f"gnuplot {results_folder}/plot_ipc.gp")

print("Done")


