This repo contains the scripts used to simulate gem5 under CoreMark Pro, Microbench, and SPEC2017. 

The support of Michal Palic is gratefully acknowledged in the development of these scripts, with all SPEC2017 related scripts being derivative of his scripts.

All plotting scripts use python to write a `.dat` data file, write a `.gp` script for `gnuplot`, then invokes `gnuplot`. 

# `simulate`

scripts used for SPEC2017: 
- simulate/run_spec.py
- simulate/fix_checkpoints.py

script used for simulating CTour parameters: 
- simulate/exec_custom_CTour_parallel.py

script used for CoreMark Pro: 
- simulate/exec_coremark_parallel.py

script used for Microbench: 
- simulate/exec_microbench_parallel.py

script used for removing single prefetches: 
- simulate/comparative_useful_superscript.py

# `plot_scripts_coremark` & `plot_scripts_microbench` 

Scripts used to gather / plot data from simulation runs. Some scripts only appear in one of the two, since it is agnostic to either coremark, microbench, or SPEC2017. The duplicated scripts in the folders are due to formatting the different number of tests in the benchmarks. 

# `analysis_scripts` 

General analysis scripts. 

scripts used to generate and visualise the bitmaps for calculating overlap: 
- analysis_sctipts/parse_output.cpp
- analysis_sctipts/generate_bitmap.cpp
- analysis_sctipts/generate_image.py

scripts used to gather and plot data from SPEC2017: 
- analysis_sctipts/compare_checkpoint_stats.py

