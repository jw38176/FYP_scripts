#!/bin/python3

import os 
import re 
import numpy as np
import pandas as pd
from helper import *
from prefetcher_def import *
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.metrics import mean_squared_error, r2_score


results_folder = "/home/jw38176/gem5/jw38176/results/microbench"
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

def standardize(data):
    return (data - np.mean(data)) / np.std(data)

# Create output folder if it does not exist
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# Get all folders in the results folder
folders = [
    f
    for f in os.listdir(results_folder)
    if os.path.isdir(os.path.join(results_folder, f)) and f != ".git"
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

# # Standardize the data using z-score
for key in global_dataframe.keys():
    global_dataframe[key] = standardize(global_dataframe[key])

# Find suitable coefficients for each metric
df = pd.DataFrame(global_dataframe)

y = df["ipc"]
X = df.drop(columns=["ipc"])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=56
)

# model = LinearRegression()
model = Lasso(alpha=0.1)
model.fit(X_train, y_train)

predictions = model.predict(X_test)

mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

coefficients = model.coef_

# Process coefficients
# coefficients = np.round(coefficients)

print("Coefficients:")
for column, coefficient in zip(X.columns, coefficients):
    print(f"{column}: {coefficient}")
print("Mean Squared Error:", mse)
print("R-squared:", r2)




