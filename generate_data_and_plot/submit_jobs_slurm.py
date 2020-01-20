"""
Runs all the simulations necessary for the manuscript. This script
uses hardcoded paths etc and needs to be adapted to whichever HPC
system one wants to use.

Afther all the jobs have run, the directory ../data will contain the simulation
outputs. For each topology, there will be 100 separate pickles, for each request
rate. They need to be merged together like so:

```bash
cd ../data/
for dir in $(ls -d */); do python merge_pickles_with_single_req_rates.py $dir; done
```

"""
import numpy as np
from subprocess import run
import numpy as np

def submit_slurm(topology, req_rate):
    sbatch = '/opt/slurm/bin/sbatch'
    pyscript = '/usr/users/dmanik/toyridesharing/notebooks/cluster_generate_all_data.py'

    command_to_run = f"--wrap='python {pyscript} {topology} {req_rate}'"
    complete_subprocess_command = f"{sbatch} -t 12:00:00 -J {topology} {command_to_run}"
    print(complete_subprocess_command)
    run(complete_subprocess_command , shell=True)

for req_rate in np.linspace(0.1, 40, 100):
    for topology in [
        "ring_10",
        "ring_100",
        "line_100",
        "star_100",
        "grid_10",
        "trigrid_13",
        "street_goe_homogenized",
        "street_harz_homogenized",
        "street_berlin_homogenized",
        "street_berlin_homogenized_coarse_graining_meters_200_target_edge_length_400",
        "street_berlin_homogenized_coarse_graining_meters_200_target_edge_length_600",
        "street_berlin_homogenized_coarse_graining_meters_200_target_edge_length_800"
	]:
        submit_slurm(topology, req_rate)
