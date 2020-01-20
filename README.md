This contains all the necessary resources to generate the figures in the manuscript
"Topology dependence of on-demand ride-sharing, Molkenthin and Manik, 2020". This is
also available at:
https://github.com/PhysicsOfMobility/ridesharing_topology_dependence

HOWTO
-----

1. Install the software
```bash
# Create a new virtualend and activate it
python 3.6 -m venv venv
source venv/bin/activate
# install depndencies
pip install -r requirements.txt
pip install -e ./
```

2. Download streetnetworks using OSMnx for figures 5-6. Execute generate_data_and_plot/gen_streetnetworks_for_simulations.ipynb.

3. Run the simulations. This can be done by running generate_data_and_plot/generate_all_data.py. This is a time and resource
intensive step, which is best done parallely in an HPC cluster. Ways to do so are described in generate_data_and_plot/cluster_generate_all_data.py

4. Now the figures can be generated. Execute the notebooks generate_data_and_plot/fig_.*.ipynb
