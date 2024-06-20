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

dat_file_data = ""

ipc_dict = dict()

best_ipc_list = []
worst_ipc_list = []
baseline_ipc_list = []

for result in folders:

    # skip the .git folder
    if result == ".git":
        continue

    result_path = os.path.join(results_folder, result)

    prefetcher_folders = [
        f
        for f in os.listdir(result_path)
        if os.path.isdir(os.path.join(result_path, f))
    ]

    ipc_list = []
    prefetcher_list = []

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
        
        ipc_list.append(ipc)
        prefetcher_list.append(prefetcher_folder)
    
    ipc_dict[result] = (ipc_list, prefetcher_list)
    
    # Get the best IPC
    best_ipc = max(ipc_list)
    best_prefetcher = prefetcher_list[ipc_list.index(best_ipc)]

    # Get the baseline IPC
    no_prefetcher_index = prefetcher_list.index("None")
    baseline_ipc = ipc_list[no_prefetcher_index]

    # Get the worst IPC from the list that is not None 
    worst_ipc = min([ipc for i, ipc in enumerate(ipc_list) if i != no_prefetcher_index])

    best_ipc_list.append((result, best_ipc))
    worst_ipc_list.append((result, worst_ipc))
    baseline_ipc_list.append((result, baseline_ipc))

for i, best_ipc_element in enumerate(best_ipc_list):
    best_ipc = best_ipc_element[1]
    result = best_ipc_element[0]
    improvement = (best_ipc - baseline_ipc_list[i][1]) / baseline_ipc_list[i][1] * 100
    # replace _ with \\\_
    result = result.replace("_", "\\\_")
    dat_file_data += f"{result} {improvement}\n"

# Generate dat file
with open(f"{results_folder}/best_ipc_imp.dat", "w+") as file:
    file.write(dat_file_data)

# Generate plot script
plot_script = f"""
set terminal pngcairo size 1000, 500
set output '{results_folder}/best_ipc_imp.png'
        
set style data histogram 
set style fill solid border -1

set ytics nomirror
set xtics nomirror

set xtics rotate by -45
set boxwidth 1.4
set key off
set yrange [*:*]

set ylabel "IPC Improvement (%)"
set xlabel "Tests"

plot '{results_folder}/best_ipc_imp.dat' using 2:xtic(1) linecolor rgb "#0080ff"

"""

# Save plot script to file
with open(f"{results_folder}/plot_best_ipc_imp.gp", "w+") as file:
    file.write(plot_script)

# Call gnuplot
os.system(f"gnuplot {results_folder}/plot_best_ipc_imp.gp")

print("Done")


