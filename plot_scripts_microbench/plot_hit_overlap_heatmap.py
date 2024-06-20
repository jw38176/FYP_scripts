import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from prefetcher_def import * 
from helper import *
# Path to the benchmark folder
benchmark_folder = '/home/jw38176/gem5/jw38176/results/coremark_logs'

# Dictionary to store the cumulative percentages and counts
data = {}
categories = set()

# Traverse each test folder
for test_folder in os.listdir(benchmark_folder):
    test_folder_path = os.path.join(benchmark_folder, test_folder)
    if os.path.isdir(test_folder_path):
        # Traverse each percentage file
        for file_name in os.listdir(test_folder_path):
            if file_name.endswith('_hit_percentage.txt'):
                target1, target2 = file_name.split('_')[:2]

                # Use prefetcher shorthand
                if target1 in prefetcher_shorthand:
                    target1 = prefetcher_shorthand[target1]
                if target2 in prefetcher_shorthand:
                    target2 = prefetcher_shorthand[target2]

                categories.add(target1)
                categories.add(target2)
                file_path = os.path.join(test_folder_path, file_name)
                with open(file_path, 'r') as file:
                    percentage = float(file.read().strip())
                    if (target1, target2) not in data:
                        data[(target1, target2)] = []
                    data[(target1, target2)].append(percentage)

# Calculate the average percentages
avg_data = {k: np.mean(v) for k, v in data.items()}

# for key, value in avg_data.items():
#     print(f'{key}: {value}')

# Create a DataFrame from the average data
categories = sorted(categories)
df = pd.DataFrame(index=categories, columns=categories)

for (target1, target2), avg in avg_data.items():
    df.loc[target1, target2] = avg * 100
    df.loc[target2, target1] = avg * 100

# Replace NaNs with zeros for missing values
df.fillna(100, inplace=True)

# Save the DataFrame to a file for Gnuplot
df.to_csv(os.path.join(benchmark_folder, "hit_overlap.dat"), sep='\t')

plt.figure(figsize=(10, 4))
ax = sns.heatmap(df, annot=True, fmt=".1f", cmap='summer', cbar=False, linewidths=0.5, linecolor='black')
for t in ax.texts: 
    t.set_text(t.get_text() + " %")
    t.set_fontsize(22)
ax.set(xlabel="", ylabel="")
ax.xaxis.tick_top()
ax.tick_params(left=False, top=False)
ax.tick_params(axis='x', size=6, pad=1)
ax.tick_params(axis='y', size=6, pad=1, rotation=0)
# ax.axhline(y=0, color='k',linewidth=2)
ax.axhline(y=df.shape[0], color='k',linewidth=2)
# ax.axvline(x=0, color='k',linewidth=2)
ax.axvline(x=df.shape[1], color='k',linewidth=2)
plt.xticks(fontsize=22, style='oblique')
plt.yticks(fontsize=22, style='oblique')

# Save the heatmap to a file
plt.savefig(os.path.join(benchmark_folder, "hit_overlap_heatmap.png"))


