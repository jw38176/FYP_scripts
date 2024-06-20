import os 
import re 
from helper import *
from prefetcher_def import *

# Requires the plot scripts of all the metrics to be run first!!

results_folder = "/home/jw38176/gem5/jw38176/results/coremark_logs"

# Get all folders in the results folder
folders = [
    f
    for f in os.listdir(results_folder)
    if os.path.isdir(os.path.join(results_folder, f))
]

coverage_imp = []
issued_imp = [] 
late_imp = [] 
accuracy_imp = [] 
unused_imp = [] 
useful_imp = [] 

coverage_worst_imp = []
issued_worst_imp = []
late_worst_imp = []
accuracy_worst_imp = []
unused_worst_imp = []
useful_worst_imp = []

count = 0

for result in folders: 
    
        if result == ".git": 
            continue 
    
        result_path = os.path.join(results_folder, result)
    
        prefetcher_folders= [
            f
            for f in os.listdir(result_path)
            if os.path.isdir(os.path.join(result_path, f))
        ]

        count += 1

        with open(os.path.join(result_path, f"{result}_cov.dat"), 'r') as file: 

            baseline_ipc = 0
            cov_list = [] 
            ipc_list = []

            for line in file: 

                cols = line.split()
                if len(cols) == 3: 

                    # Ignore Multi
                    if cols[0] == "Multi": 
                        continue

                    if cols[0] == "Baseline": 
                        baseline_ipc = float(cols[1])
                        continue

                    ipc_list.append(float(cols[1]))
                    cov_list.append(float(cols[2]))

                else: 
                    print(f"Error: {line} in {result}_cov.dat")
                    continue
            
            max_cov = max(cov_list)
            max_ipc = ipc_list[cov_list.index(max_cov)]

            coverage_imp.append(max_ipc - baseline_ipc)

            worst_ipc = min(ipc_list)
            coverage_worst_imp.append(max_ipc - worst_ipc)

        
        with open(os.path.join(result_path, f"{result}_issued.dat"), 'r') as file:
             
            baseline_ipc = 0
            issued_list = [] 
            ipc_list = []

            for line in file: 

                cols = line.split()
                if len(cols) == 3: 

                    # Ignore Multi
                    if cols[0] == "Multi": 
                        continue

                    if cols[0] == "Baseline": 
                        baseline_ipc = float(cols[1])
                        continue

                    ipc_list.append(float(cols[1]))
                    issued_list.append(float(cols[2]))

                else: 
                    print(f"Error: {line} in {result}_issued.dat")
                    continue
            
            min_issued = min(issued_list)
            min_ipc = ipc_list[issued_list.index(min_issued)]

            issued_imp.append(min_ipc - baseline_ipc)

            worst_ipc = min(ipc_list)
            issued_worst_imp.append(min_ipc - worst_ipc)
        
        with open(os.path.join(result_path, f"{result}_late.dat"), 'r') as file:

            baseline_ipc = 0
            late_list = [] 
            ipc_list = []

            for line in file: 

                cols = line.split()
                if len(cols) == 3: 

                    # Ignore Multi
                    if cols[0] == "Multi": 
                        continue

                    if cols[0] == "Baseline": 
                        baseline_ipc = float(cols[1])
                        continue

                    ipc_list.append(float(cols[1]))
                    late_list.append(float(cols[2]))

                else: 
                    print(f"Error: {line} in {result}_late.dat")
                    continue
            
            min_late = min(late_list)
            min_ipc = ipc_list[late_list.index(min_late)]

            late_imp.append(min_ipc - baseline_ipc)

            worst_ipc = min(ipc_list)
            late_worst_imp.append(min_ipc - worst_ipc)
        
        with open(os.path.join(result_path, f"{result}_acc.dat"), 'r') as file:

            baseline_ipc = 0
            accuracy_list = [] 
            ipc_list = []

            for line in file: 

                cols = line.split()
                if len(cols) == 3: 

                    # Ignore Multi
                    if cols[0] == "Multi": 
                        continue

                    if cols[0] == "Baseline": 
                        baseline_ipc = float(cols[1])
                        continue

                    ipc_list.append(float(cols[1]))
                    accuracy_list.append(float(cols[2]))

                else: 
                    print(f"Error: {line} in {result}_acc.dat")
                    continue
            
            max_accuracy = max(accuracy_list)
            max_ipc = ipc_list[accuracy_list.index(max_accuracy)]

            accuracy_imp.append(max_ipc - baseline_ipc)

            worst_ipc = min(ipc_list)
            accuracy_worst_imp.append(max_ipc - worst_ipc)

        with open(os.path.join(result_path, f"{result}_useful.dat"), 'r') as file:

            baseline_ipc = 0
            useful_list = [] 
            ipc_list = []

            for line in file: 

                cols = line.split()
                if len(cols) == 3: 

                    # Ignore Multi
                    if cols[0] == "Multi": 
                        continue

                    if cols[0] == "Baseline": 
                        baseline_ipc = float(cols[1])
                        continue

                    ipc_list.append(float(cols[1]))
                    useful_list.append(float(cols[2]))

                else: 
                    print(f"Error: {line} in {result}_useful.dat")
                    continue
            
            max_useful = max(useful_list)
            max_ipc = ipc_list[useful_list.index(max_useful)]

            useful_imp.append(max_ipc - baseline_ipc)

            worst_ipc = min(ipc_list)
            useful_worst_imp.append(max_ipc - worst_ipc)
            
        
        with open(os.path.join(result_path, f"{result}_unused.dat"), 'r') as file:

            baseline_ipc = 0
            unused_list = [] 
            ipc_list = []

            for line in file: 

                cols = line.split()
                if len(cols) == 3: 

                    # Ignore Multi
                    if cols[0] == "Multi": 
                        continue

                    if cols[0] == "Baseline": 
                        baseline_ipc = float(cols[1])
                        continue

                    ipc_list.append(float(cols[1]))
                    unused_list.append(float(cols[2]))

                else: 
                    print(f"Error: {line} in {result}_unused.dat")
                    continue
            
            min_unused = min(unused_list)
            min_ipc = ipc_list[unused_list.index(min_unused)]

            unused_imp.append(min_ipc - baseline_ipc)

            worst_ipc = min(ipc_list)
            unused_worst_imp.append(min_ipc - worst_ipc)

print(f"Average coverage improvement: {sum(coverage_imp) / count}")
print(f"Average issued improvement: {sum(issued_imp) / count}")
print(f"Average late improvement: {sum(late_imp) / count}")
print(f"Average accuracy improvement: {sum(accuracy_imp) / count}")
print(f"Average useful improvement: {sum(useful_imp) / count}")
print(f"Average unused improvement: {sum(unused_imp) / count}")
print('')
print(f"Average coverage worst improvement: {sum(coverage_worst_imp) / count}")
print(f"Average issued worst improvement: {sum(issued_worst_imp) / count}")
print(f"Average late worst improvement: {sum(late_worst_imp) / count}")
print(f"Average accuracy worst improvement: {sum(accuracy_worst_imp) / count}")
print(f"Average useful worst improvement: {sum(useful_worst_imp) / count}")
print(f"Average unused worst improvement: {sum(unused_worst_imp) / count}")
