import os 
import re 
from helper import *
from prefetcher_def import *

results_folder = "/home/jw38176/gem5/jw38176/results/microbench_ctour_delay"
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

    ext_folders = [
        f
        for f in os.listdir(result_path)
        if os.path.isdir(os.path.join(result_path, f))
    ]

    for i, ext_folder in enumerate(ext_folders): 

        ipc = 0

        with open(os.path.join(result_path, ext_folder, "stats.txt"), "r") as file:

            for line in file:

                match = re.search(ipc_pattern, line)

                if match:
                    ipc = float(match.group(1))
                    if verbose: print(f"IPC: {ipc}")
                    break

            else:
                print("IPC not found for" + os.path.join(result_path, ext_folder, "stats.txt"))
                continue
        
        ext = int(ext_folder.split("_")[1])

        if ext not in ipc_dict:
            ipc_dict[ext] = ipc
        else:
            ipc_dict[ext] += ipc

for ext in sorted(ipc_dict.keys()):
    ipc_dict[ext] /= len(folders)
    dat_file_data += f"{ext} {ipc_dict[ext]}\n"

# Generate dat file
with open(os.path.join(results_folder, f"delay.dat"), "w+") as file:
    file.write(dat_file_data)

# Generate plot script
plot_script = f"""
set terminal pngcairo size 500, 500
set output '{results_folder}/delay.png'
        
set style data histogram 
set style fill solid border -1

set ytics {0.001} nomirror
set xtics nomirror

set xtics rotate by -45
set boxwidth 1.4
set key off
set yrange [*:*]

set ylabel "IPC"
set xlabel "Delay Window Size"

plot '{results_folder}/delay.dat' using 2:xtic(1) linecolor rgb "#0080ff"

"""

# Save plot script to file
with open(f"{results_folder}/plot_delay.gp", "w+") as file:
    file.write(plot_script)

# Call gnuplot
os.system(f"gnuplot {results_folder}/plot_delay.gp")

print("Done")

    
