#!/bin/python3

import os 
import re 
from helper import *
from prefetcher_def import *

results_folder = "/home/jw38176/gem5/jw38176/results/coremark_logs"
# output_folder = "/home/jw38176/gem5/jw38176/graphs"

ipc_pattern = r"system.cpu.ipc\s+(\d+\.\d+).*"
accuracy_pattern = r"system.cpu.dcache.prefetcher.accuracy\s+(\d+\.\d+).*"
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
    accuracy_list = []

    for prefetcher_folder in prefetcher_folders: 

        # Ignore CTour
        if prefetcher_folder == "CoverageTournamentPrefetcher":
            continue

        if os.path.exists(prefetcher_folder + '/run.done'):
            with open(prefetcher_folder + '/run.done', 'r') as exitcode:
                if int(exitcode.read().strip()) != 0:
                    print(f'Skipped {prefetcher_folder} (Null exit code)')
                    continue 

        ipc = 0
        accuracy = 0

        with open(os.path.join(result_path, prefetcher_folder, "stats.txt"), "r") as file:

            for line in file:

                match_ipc = re.search(ipc_pattern, line)
                match_accuracy = re.search(accuracy_pattern, line)

                if match_ipc:
                    ipc = float(match_ipc.group(1))
                    if verbose: print(f"IPC: {ipc}")
                    
                if match_accuracy:
                    accuracy = float(match_accuracy.group(1))
                    if verbose: print(f"accuracy: {accuracy}")
        
        ipc_list.append((prefetcher_folder, ipc))
        accuracy_list.append((prefetcher_folder, accuracy))
    
    if enable_sort:
        ipc_list.sort(key=lambda x: x[1], reverse=False)
        # Sort accuracy list based on ipc_list[0]
        # accuracy_list.sort(key=lambda x: x[1], reverse=False)
        sorted_ipc_list_string = ""
        for prefetcher, ipc in ipc_list:
            sorted_ipc_list_string += f"{prefetcher_shorthand[prefetcher]}(), "
        print(f"Sorted IPC list: {sorted_ipc_list_string}")

    for prefetcher, ipc in ipc_list:
        # Find accuracy for the same prefetcher
        accuracy_count = 0
        for accuracy_prefetcher, accuracy in accuracy_list:
            if accuracy_prefetcher == prefetcher:
                accuracy_count = accuracy
                break
        dat_file_data += f"{prefetcher_shorthand[prefetcher]} {ipc} {accuracy}\n"
        
    # Generate dat file  
    with open(os.path.join(result_path, f"{result}_acc.dat"), "w+") as file:
        file.write(dat_file_data)

# Generate plot script
plot_script = f"""

set terminal pngcairo size 2200,1400
set output '{results_folder}/accuracy_ipc.png'

set multiplot layout 3, 3 
        
set style data histograms
set style histogram cluster gap 1
set style fill solid border -1

set xtics rotate by -45
set boxwidth 0.9
# set key off
set key autotitle columnheader
set key outside top left  
set y2tics
set ytics 0.01 nomirror
set xtics nomirror

set yrange [*:*]
set y2range [*:*]

set ylabel "IPC"
set y2label "Accuracy"
set xlabel "Prefetchers"


# set key outside center bottom horizontal

""" 

for i, result in enumerate(folders):
    if i > 0:
        plot_script += "set key off\n"
    plot_script += f"""
set title "{result}" 
plot '{results_folder}/{result}/{result}_acc.dat' using 2:xtic(1) title 'IPC' axes x1y1 linecolor rgb "#5397d4", '' using 3:xtic(1) title 'Accuracy' axes x1y2 linecolor rgb "#ebe134"
\n"""

plot_script += "unset multiplot\n"


# Save plot script to file
with open(f"{results_folder}/plot_accuracy_ipc.gp", "w+") as file:
    file.write(plot_script)

# Call gnuplot
os.system(f"gnuplot {results_folder}/plot_accuracy_ipc.gp")

print("Done")


