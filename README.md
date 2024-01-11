This is a fork of a repo by Debsankha Manik.
It contains all relevant code for replicating the simulations and analyses done in my master-thesis titled "Complex Street-Network Topologies and the Emergence of Cyclic Routes in On-Demand Ride-Sharing".

HOWTO
-----
1. Install the software

```bash
# Create a new virtualenv and activate it
python3.6 -m venv venv
source venv/bin/activate
# install depndencies
pip install -r requirements.txt
pip install -e ./
```

2. Make sure the folder `data` exists. This is where all data will be stored. It must contain the following subfolders: `01_simulations`, `02_stats`, `03_casestudy`, `03_optimalities`.

3. Set the simulation parameters. This can be done by editing the file `utils/env_parameters.py`

4. Run the simulations. This can be done by running `_01_multiprocessing_data_generation`. 

5. Run the analysis. This can be done by running `_02_multiprocessing_stats_generation`.

6. Calculate the Route-Optimality Values. This can be done by running `_03_routespace_analysis`.

7. Generate the plots. This can be done by running the files in `_06_graphics_thesis`.
