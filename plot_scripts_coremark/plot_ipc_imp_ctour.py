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

included_prefetchers = ["DCPTPrefetcher", "IndirectMemoryPrefetcher", "TaggedPrefetcher", "CoverageTournamentPrefetcher"]
included_prefetchers_display = ["DCPT", "IMP", "Tagged", "CTour"]

for result in ipc_dict:

    ipc_list, prefetcher_list = ipc_dict[result]

    # Find the IPC of the baseline
    baseline_ipc = ipc_list[prefetcher_list.index("None")]

    # Find the IPc for the included prefetchers
    included_ipc_list = [ipc_list[prefetcher_list.index(prefetcher)] for prefetcher in included_prefetchers]

    # Find the improvement for each prefetcher
    improvement_list = [(ipc - baseline_ipc) / baseline_ipc * 100 for ipc in included_ipc_list]

    result = result.replace("_", "\\\_")

    dat_file_data += f"{result} {' '.join([str(improvement) for improvement in improvement_list])}\n"

with open(f"{results_folder}/ipc_improvement.dat", "w") as dat_file:
    dat_file.write(dat_file_data)



plot_script = f"""
set terminal pngcairo size 1200,500
set output '{results_folder}/ipc_improvement.png'

set style data histogram
set style histogram cluster gap 1
set style fill solid border -1

set xtics rotate by -45
set boxwidth 0.9
set key outside

set ylabel "IPC Improvement (%)"
set xlabel "Tests"

"""

line_styles = ""
plot_commands = []

# colors = ['khaki', 'skyblue', 'light-green', 'orange']  
colors = ['salmon', 'light-green', 'web-blue', 'yellow']  


for index, component in enumerate(included_prefetchers_display):
    line_styles += f"set style line {index + 1} lc rgb '{colors[index % len(colors)]}'\n"
    if index == 0:
        plot_commands.append(f"'{results_folder}/ipc_improvement.dat' using {index + 2}:xtic(1) title '{component}' ls {index + 1}")
    else:
        plot_commands.append(f"'' using {index + 2}:xtic(1) title '{component}' ls {index + 1}")

# Complete the plot command with dynamic content
plot_script += line_styles
plot_script += "plot " + ", \\\n     ".join(plot_commands)

with open(f"{results_folder}/ipc_improvement.gp", "w") as plot_file:
    plot_file.write(plot_script)

os.system(f"gnuplot {results_folder}/ipc_improvement.gp")



