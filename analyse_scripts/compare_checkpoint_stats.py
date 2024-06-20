import matplotlib.pyplot as plt
import numpy as np
import os
import glob

def aggregate_stat(res_dir, checkpoint_dir, statname):
    stat_dict = {}
    weight_paths = glob.glob(checkpoint_dir + "/**/simpoints.weights", recursive=True)
    weight_paths.sort()

    spec_benchmarks = list(set([weight_path.split('/')[-3] for weight_path in weight_paths]))
    spec_benchmarks.sort()

    for spec_benchmark in spec_benchmarks:

        # if spec_benchmark == "531.deepsjeng_r":
        #     continue

        # if spec_benchmark == "557.xz_r":
        #     continue

        for weight_path in weight_paths:

            if spec_benchmark not in weight_path:
                continue

            #Parse weight path
            weight_path_split = weight_path.split('/')
            benchmark_idx = weight_path_split[-2]

            #Parse out simpoints
            weights = []
            with open(weight_path, 'r') as w:
                w_lines = w.readlines()
                for line in w_lines:
                    weights.append( float(line.split(' ')[0]))
            
            for idx, weight in enumerate(weights):
                stat_path = f"{res_dir}/{spec_benchmark}/{benchmark_idx}/{idx}/stats.txt"
                stat_value = 0

                with open(stat_path, 'r') as stat_file:
                    lines = stat_file.readlines()
                    #To read the actual warmed up stat only
                    break_val = 1
                    for line in lines:
                        if statname in line:
                            if break_val == 2:
                                linesplit = line.split(' ')
                                linesplitclean = [x for x in linesplit if x != '']
                                stat_value = float(linesplitclean[1])
                                break
                            else:
                                break_val += 1
                                continue

                if spec_benchmark in stat_dict:
                    stat_dict[spec_benchmark] += weight * stat_value
                else:
                    stat_dict[spec_benchmark] = weight * stat_value

    return stat_dict


baseline_dir = "/home/jw38176/gem5/jw38176/results/spec_2017_rate_results/Baseline"
new_root_dir  = "/home/jw38176/gem5/jw38176/results/spec_2017_rate_results/"
checkpoint_dir = "/media/jw38176/WD_Drive/spec_2017/spec_2017_rate_checkpoints"

result_dir = "/home/jw38176/gem5/jw38176/results/spec_2017_rate_analysis/"

new_components = ["IndirectMemoryPrefetcher", "DCPTPrefetcher", "TaggedPrefetcher", "CoverageTournamentPrefetcher"]
new_component_names = ["IMP", "DCPT", "Tagged", "CTour"]

stat_name = "simTicks"

base_dict = aggregate_stat(
                baseline_dir,
               checkpoint_dir,
               stat_name
               )

new_dicts = {}

for component in new_components:

    new_dir = os.path.join(new_root_dir, component)

    new_dicts[component] = aggregate_stat(
                    new_dir,
                checkpoint_dir,
                stat_name
                )

labels = list(base_dict.keys())
labels.sort()

# print(new_dict)

# exit(0)

values = [] 

for component in new_components:
    new_dict = new_dicts[component]
    values.append([(base_dict[key] - new_dict[key])/base_dict[key] * 100 for key in labels])

# Print overall improvement for each component
for idx, component in enumerate(new_components):
    print(f"{component} improvement: {np.mean(values[idx])}")

# print(values)

# Use gnuplot to plot the data
dat_file_data = ""

dat_file_data += "\n"

for idx, label in enumerate(labels):
    label = label.replace("_", "\\\_")
    dat_file_data += f"{label} {values[0][idx]} {values[1][idx]} {values[2][idx]} {values[3][idx]}\n"

with open("spec_perf_improvement.dat", "w") as dat_file:
    dat_file.write(dat_file_data)

plot_script = f"""
set terminal pngcairo size 1500,600
set output '{result_dir}perf_improvement.png'

set style data histogram
set style histogram cluster gap 1
set style fill solid border -1

set xtics rotate by -45
set boxwidth 0.9
set key outside

set ylabel "Performance Improvement (%)"
set xlabel "Tests"


"""

line_styles = ""
plot_commands = []

# colors = ['khaki', 'skyblue', 'light-green', 'orange']
colors = ['salmon', 'light-green', 'web-blue', 'yellow']  


for index, component in enumerate(new_component_names):
    line_styles += f"set style line {index + 1} lc rgb '{colors[index % len(colors)]}'\n"
    if index == 0:
        plot_commands.append(f"'spec_perf_improvement.dat' using {index + 2}:xtic(1) title '{component}' ls {index + 1}")
    else:
        plot_commands.append(f"'' using {index + 2}:xtic(1) title '{component}' ls {index + 1}")

# Complete the plot command with dynamic content
plot_script += line_styles
plot_script += "plot " + ", \\\n     ".join(plot_commands)

with open("plot_perf_improvement.gp", "w") as plot_file:
    plot_file.write(plot_script)

os.system("gnuplot plot_perf_improvement.gp")


exit(0)



# Creating the bar graph
plt.figure(figsize=(14, 10))  # Set figure size
plt.bar(labels, values, color='blue', edgecolor='black')

# Adding labels and title
plt.xlabel('Benchmarks')
plt.ylabel('Percentage Improvement (%)')
#plt.title('Percentage Change from Base to New Values')

plt.xticks(rotation=90) 
plt.subplots_adjust(bottom=0.2) 

# Showing the plot
plt.savefig(f'/home/jw38176/gem5/jw38176/results/spec_2017_rate_analysis/perf_improvement1.png', dpi=300)
plt.show(block=True)

print("Got here")