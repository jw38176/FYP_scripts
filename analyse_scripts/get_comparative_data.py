
import os 

result_path = "/home/jw38176/gem5/jw38176/results/microbench_logs_new/MD"

prefetcher1 = "TaggedPrefetcher"
prefetcher2 = "StridePrefetcher"

prefetcher_folders= [
    f
    for f in os.listdir(result_path)
    if os.path.isdir(os.path.join(result_path, f))
]

unused = []
useful = []
issued = []
unused_tick = []
useful_tick = []
issued_tick = []

prefetcher_unused = dict()
prefetcher_useful = dict()
prefetcher_issued = dict()
prefetcher_unused_tick = dict()
prefetcher_useful_tick = dict()
prefetcher_issued_tick = dict()

for prefetcher_folder in prefetcher_folders: 

    if prefetcher_folder != prefetcher1 and prefetcher_folder != prefetcher2:
        continue

    if os.path.exists(prefetcher_folder + '/run.done'):
        with open(prefetcher_folder + '/run.done', 'r') as exitcode:
            if int(exitcode.read().strip()) != 0:
                print(f'Skipped {prefetcher_folder} (Null exit code)')
                continue 
    
    with open(os.path.join(result_path, prefetcher_folder, "issued.txt"), "r") as file:
        issued = file.read().splitlines() 

    with open(os.path.join(result_path, prefetcher_folder, "unused.txt"), "r") as file:
        unused = file.read().splitlines() 
    
    with open(os.path.join(result_path, prefetcher_folder, "hit.txt"), "r") as file:
        useful = file.read().splitlines() 
    
    with open(os.path.join(result_path, prefetcher_folder, "issued_tick.txt"), "r") as file:
        issued_tick = file.read().splitlines() 

    with open(os.path.join(result_path, prefetcher_folder, "unused_tick.txt"), "r") as file:
        unused_tick = file.read().splitlines() 
    
    with open(os.path.join(result_path, prefetcher_folder, "hit_tick.txt"), "r") as file:
        useful_tick = file.read().splitlines() 

    print(len((useful)))
    
    prefetcher_unused[prefetcher_folder] = unused
    prefetcher_useful[prefetcher_folder] = useful
    prefetcher_issued[prefetcher_folder] = issued
    prefetcher_unused_tick[prefetcher_folder] = unused_tick
    prefetcher_useful_tick[prefetcher_folder] = useful_tick
    prefetcher_issued_tick[prefetcher_folder] = issued_tick

prefetcher_list = list(prefetcher_unused.keys())

unique_useful1 = [] 
unique_useful2 = []

unique_useful1_final = []
unique_useful2_final = []

unique_useful1_tick = []
unique_useful2_tick = []
unique_useful1_timeliness = []
unique_useful2_timeliness = []

# Get the unique hits between the two prefetchers
for i in range(len(prefetcher_useful[prefetcher1])):
    for j in range(len(prefetcher_useful[prefetcher2])):
        if prefetcher_useful[prefetcher1][i] == prefetcher_useful[prefetcher2][j]:
            prefetcher_useful[prefetcher2][j] = None
            prefetcher_useful[prefetcher1][i] = None

for i in range(len(prefetcher_useful[prefetcher1])):
    if prefetcher_useful[prefetcher1][i] != None:
        unique_useful1.append(int(prefetcher_useful[prefetcher1][i]))
        unique_useful1_tick.append(int(prefetcher_useful_tick[prefetcher1][i]))

for i in range(len(prefetcher_useful[prefetcher2])):
    if prefetcher_useful[prefetcher2][i] != None:
        unique_useful2.append(int(prefetcher_useful[prefetcher2][i]))
        unique_useful2_tick.append(int(prefetcher_useful_tick[prefetcher2][i]))

print(len(unique_useful2))

for i in range(len(unique_useful1)):
    for j in range(len(prefetcher_issued[prefetcher1])):
        if int(prefetcher_issued[prefetcher1][j]) <= unique_useful1[i] and int(prefetcher_issued[prefetcher1][j]) + 8 > unique_useful1[i]:
            timeliness = unique_useful1_tick[i] - int(prefetcher_issued_tick[prefetcher1][j])
            if timeliness > 0:
                unique_useful1_timeliness.append(timeliness)
                unique_useful1_final.append(unique_useful1[i])

            break
            
for i in range(len(unique_useful2)):
    for j in range(len(prefetcher_issued[prefetcher2])):
        if int(prefetcher_issued[prefetcher2][j]) <= unique_useful2[i] and int(prefetcher_issued[prefetcher2][j]) + 8 > unique_useful2[i]:
            timeliness = unique_useful2_tick[i] - int(prefetcher_issued_tick[prefetcher2][j])
            if timeliness > 0:
                unique_useful2_timeliness.append(timeliness)
                unique_useful2_final.append(unique_useful2[i])
            break

# print(unique_useful1_timeliness)
# print(unique_useful2_timeliness)

print(unique_useful1_final)



