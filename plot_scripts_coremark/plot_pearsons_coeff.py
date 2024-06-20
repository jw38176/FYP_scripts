#!/bin/python3

import os 
import re 
import numpy as np
from helper import *
from prefetcher_def import *

results_folder = "/home/jw38176/gem5/jw38176/results/coremark"
# output_folder = "/home/jw38176/gem5/jw38176/graphs"

ipc_pattern = r"system.cpu.ipc\s+(\d+\.\d+).*"
coverage_pattern = r"system.cpu.dcache.prefetcher.coverage\s+(\d+\.\d+).*"
accuracy_pattern = r"system.cpu.dcache.prefetcher.accuracy\s+(\d+\.\d+).*"
useful_pattern = r"system.cpu.dcache.prefetcher.pfUseful\s+(\d+).*"
issued_pattern = r"system.cpu.dcache.prefetcher.pfIssued\s+(\d+).*"
unused_pattern = r"system.cpu.dcache.prefetcher.pfUnused\s+(\d+).*"
late_pattern = r"system.cpu.dcache.prefetcher.pfLate\s+(\d+).*"
verbose = False
enable_sort = True
    
def pearson_correlation(x, y):
    return np.corrcoef(np.array(x), np.array(y))[0, 1]

def strength_of_correlation(x, y):
    return np.abs(np.corrcoef(np.array(x), np.array(y))[0, 1])

# Create output folder if it does not exist
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# Get all folders in the results folder
folders = [
    f
    for f in os.listdir(results_folder)
    if os.path.isdir(os.path.join(results_folder, f))
]

global_dataframe = dict()
global_dataframe["ipc"] = list()
global_dataframe["Coverage"] = list()
global_dataframe["Accuracy"] = list()
global_dataframe["Useful"] = list()
global_dataframe["Issued"] = list()
global_dataframe["Unused"] = list()
global_dataframe["Late"] = list()


dat_file_data = ""

for result in folders:

    result_path = os.path.join(results_folder, result)

    prefetcher_folders= [
        f
        for f in os.listdir(result_path)
        if os.path.isdir(os.path.join(result_path, f))
    ]

    for prefetcher_folder in prefetcher_folders: 

        if os.path.exists(prefetcher_folder + '/run.done'):
            with open(prefetcher_folder + '/run.done', 'r') as exitcode:
                if int(exitcode.read().strip()) != 0:
                    print(f'Skipped {prefetcher_folder} (Null exit code)')
                    continue 

        ipc = 0
        coverage = 0
        accuracy = 0
        useful = 0
        issued = 0
        unused = 0
        late = 0

        with open(os.path.join(result_path, prefetcher_folder, "stats.txt"), "r") as file:

            for line in file:

                match_ipc = re.search(ipc_pattern, line)
                match_coverage = re.search(coverage_pattern, line)
                match_accuracy = re.search(accuracy_pattern, line)
                match_useful = re.search(useful_pattern, line)
                match_issued = re.search(issued_pattern, line)
                match_unused = re.search(unused_pattern, line)
                match_late = re.search(late_pattern, line)

                if match_ipc:
                    ipc = float(match_ipc.group(1))
                    if verbose: print(f"IPC: {ipc}")
                    
                if match_coverage:
                    coverage = float(match_coverage.group(1))
                    if verbose: print(f"Coverage: {coverage}")
                
                if match_accuracy:
                    accuracy = float(match_accuracy.group(1))
                    if verbose: print(f"Accuracy: {accuracy}")
                
                if match_useful:
                    useful = int(match_useful.group(1))
                    if verbose: print(f"Useful: {useful}")
                
                if match_issued:
                    issued = int(match_issued.group(1))
                    if verbose: print(f"Issued: {issued}")
                
                if match_unused:
                    unused = int(match_unused.group(1))
                    if verbose: print(f"Unused: {unused}")
                
                if match_late:
                    late = int(match_late.group(1))
                    if verbose: print(f"Late: {late}")

        # Warn if any of the metrics are missing
        if ipc == 0:
            print(f"Warning: IPC not found for {prefetcher_folder}")
        
        if coverage == 0:
            print(f"Warning: Coverage not found for {prefetcher_folder}")
        
        if accuracy == 0:
            print(f"Warning: Accuracy not found for {prefetcher_folder}")
        
        if useful == 0:
            print(f"Warning: Useful not found for {prefetcher_folder}")
        
        if issued == 0:
            print(f"Warning: Issued not found for {prefetcher_folder}")

        if unused == 0:
            print(f"Warning: Unused not found for {prefetcher_folder}")
        
        if late == 0:
            print(f"Warning: Late not found for {prefetcher_folder}")
        
        # proceed only if all metrics are found
        if ipc != 0 and coverage != 0 and accuracy != 0 and useful != 0 and issued != 0 and unused != 0 and late != 0:
            global_dataframe["ipc"].append(ipc)
            global_dataframe["Coverage"].append(coverage)
            global_dataframe["Accuracy"].append(accuracy)
            global_dataframe["Useful"].append(useful)
            global_dataframe["Issued"].append(issued)
            global_dataframe["Unused"].append(unused)
            global_dataframe["Late"].append(late)
    
sorted_coefficients = dict()

# Get the Pearson correlation coefficients for each metric
for metric in global_dataframe.keys():

    if metric == "ipc":
        continue

    coefficients = pearson_correlation(
        global_dataframe[metric], global_dataframe["ipc"]
    )

    print(f"Correlation between {metric} and IPC: {coefficients}")

    sorted_coefficients[metric] = coefficients

# Sort the coefficients
sorted_coefficients = dict(sorted(sorted_coefficients.items(), key=lambda item: item[1], reverse=True))

for metric, coefficient in sorted_coefficients.items():
    dat_file_data += f"{metric} {coefficient}\n"

# Save data to file
with open(f"{results_folder}/pearson_coeff.dat", "w+") as file:
    file.write(dat_file_data)

# Generate plot script
plot_script = f"""

set terminal pngcairo size 800,600
set output '{results_folder}/pearsons_coeff.png'
        
set style data histograms
set style histogram cluster gap 1
set style fill solid border -1

# set xtics rotate by -45
set boxwidth 0.9
set key off
set ytics nomirror
set xtics nomirror

set yrange [*:*]
set xzeroaxis lt -1

set ylabel "Correlation Coefficient"
set xlabel "Metrics"

plot '{results_folder}/pearson_coeff.dat' using 2:xtic(1) linecolor rgb "#8cded4" 
""" 

# Save plot script to file
with open(f"{results_folder}/plot_pearsons_coeff.gp", "w+") as file:
    file.write(plot_script)

# Call gnuplot
os.system(f"gnuplot {results_folder}/plot_pearsons_coeff.gp")

dat_file_data = ""
sorted_coefficients = dict()

# Get the Strength of the Pearson correlation coefficients for each metric
for metric in global_dataframe.keys():

    if metric == "ipc":
        continue
    
    coefficients = strength_of_correlation(
        global_dataframe[metric], global_dataframe["ipc"]
    )

    sorted_coefficients[metric] = coefficients

    print(f"Correlation Strength between {metric} and IPC: {coefficients}")

# Sort the coefficients
sorted_coefficients = dict(sorted(sorted_coefficients.items(), key=lambda item: item[1], reverse=True))

for metric, coefficient in sorted_coefficients.items():
    dat_file_data += f"{metric} {coefficient}\n"


# Save data to file
with open(f"{results_folder}/pearson_coeff_strength.dat", "w+") as file:
    file.write(dat_file_data)

# Generate plot script
plot_script = f"""

set terminal pngcairo size 800,600
set output '{results_folder}/pearsons_coeff_strength.png'

set style data histograms
set style histogram cluster gap 1
set style fill solid border -1

# set xtics rotate by -45
set boxwidth 0.9
set key off
set ytics nomirror
set xtics nomirror

set yrange [0:*]
set xzeroaxis lt -1

set ylabel "Strength of Correlation Coefficient"
set xlabel "Metrics"

plot '{results_folder}/pearson_coeff_strength.dat' using 2:xtic(1) linecolor rgb "#8cded4"

"""

# Save plot script to file
with open(f"{results_folder}/plot_pearsons_coeff_strength.gp", "w+") as file:
    file.write(plot_script)

# Call gnuplot
os.system(f"gnuplot {results_folder}/plot_pearsons_coeff_strength.gp")

print("Done")


