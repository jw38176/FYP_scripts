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

    dat_file_data = ""
    ipc_list = []
    prefetcher_list = []

    for prefetcher_folder in prefetcher_folders: 

        # if prefetcher_folder == "CoverageTournamentPrefetcher":
        #     continue

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

    
# Get the average IPC improvement of best v.s. baseline 
ipc_improvement = 0
for result, best_ipc in best_ipc_list:
    baseline_ipc = [ipc for r, ipc in baseline_ipc_list if r == result][0]
    ipc_improvement += best_ipc - baseline_ipc

ipc_improvement /= len(best_ipc_list)

print(f"Average IPC improvement of best prefetcher over baseline: {ipc_improvement}")   

# Get the average IPC improvement of best v.s. worst
ipc_improvement = 0
for result, best_ipc in best_ipc_list:
    worst_ipc = [ipc for r, ipc in worst_ipc_list if r == result][0]
    ipc_improvement += best_ipc - worst_ipc

ipc_improvement /= len(best_ipc_list)

print(f"Average IPC improvement of best prefetcher over worst: {ipc_improvement}")

# Get the average IPC improvement of baseline v.s. worst
ipc_improvement = 0
for result, baseline_ipc in baseline_ipc_list:
    worst_ipc = [ipc for r, ipc in worst_ipc_list if r == result][0]
    ipc_improvement += baseline_ipc - worst_ipc

ipc_improvement /= len(best_ipc_list)

print(f"Average IPC improvement of baseline over worst: {ipc_improvement}")

# Get the average IPC improvement of worst v.s. baseline
ipc_improvement = 0
for result, worst_ipc in worst_ipc_list:
    baseline_ipc = [ipc for r, ipc in baseline_ipc_list if r == result][0]
    ipc_improvement += worst_ipc - baseline_ipc

ipc_improvement /= len(best_ipc_list)

print(f"Average IPC improvement of worst over baseline: {ipc_improvement}")

# Get the average IPC improvement of using a specific prefetcher over baseline
prefetcher_improvement = {pref: 0 for pref in prefetcher_list if pref != "None"}

for prefetcher in prefetcher_improvement.keys():
    improvement = 0
    count = 0
    for result, (ipc_list, prefetcher_list) in ipc_dict.items():
        if prefetcher in prefetcher_list:
            prefetcher_ipc = ipc_list[prefetcher_list.index(prefetcher)]
            baseline_ipc = ipc_list[prefetcher_list.index("None")]
            improvement += prefetcher_ipc - baseline_ipc
            count += 1
    prefetcher_improvement[prefetcher] = improvement / count

print(f"Average IPC improvement of each prefetcher over baseline: {prefetcher_improvement}")

# Get the average IPC improvement of using a specific prefetcher over worst
for prefetcher in prefetcher_improvement.keys():
    improvement = 0
    count = 0
    for result, (ipc_list, prefetcher_list) in ipc_dict.items():
        if prefetcher in prefetcher_list:
            prefetcher_ipc = ipc_list[prefetcher_list.index(prefetcher)]
            worst_ipc = min([ipc for i, ipc in enumerate(ipc_list) if prefetcher_list[i] != "None"])
            improvement += prefetcher_ipc - worst_ipc
            count += 1
    prefetcher_improvement[prefetcher] = improvement / count

print(f"Average IPC improvement of each prefetcher over worst: {prefetcher_improvement}")
