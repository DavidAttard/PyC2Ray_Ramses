# Provided you have a halo catalogue produced using AHF this program will read the _halos file 
# and generate the required src_{z}.txt file where the first line of the txt file contains the 
# number of sources, the 1st-3rd column contains the x,y,z indexing (in Fortran Formar i.e. starting from 1).
# The 4th and 5th column contains the halo mass in solar mass of the HMACH halos and LMACH halos respectively
# and the 6th column contains the LMACH masses multiplied by a factor of (1/(9x10^8) -1/9) as in eqn. 3 of
# Dixon et al. (2018) which is used for the mass-dependant suppression source model. 
# This code can be run using the batch script run_source_list.sh to run this code in parallel.

import pandas as pd
import numpy as np
import sys
import glob
import re

i = int(sys.argv[1])

# Directory path and constants
AHF_directory = f'/p/scratch/hestiaeor/david/HYDRO_256_4096_CRAL_KF_PAD_LMAX17/AHF/{i:03d}/halos'

# Define the size of the mesh
N = 256
h = 0.677
HMACH = (1.43e9) / h  # in solar masses
boxsize = 100  # Mpc

AHF_directory = '/p/scratch/lgreion/david/full_box/DMO_1024_HR/AHF/{0:03d}/halos'.format(i)

# Prepare the output grid: N^3 cells, 3 fields (HMACH, LMACH, LMACH_MassDep)
HMACH_grid = np.zeros((N, N, N))
LMACH_grid = np.zeros((N, N, N))
LMACH_MassDep_grid = np.zeros((N, N, N))

# Pattern to match files ending with "_halos"
pattern = AHF_directory + "/*_halos"

# Get list of files ending with "_halos"
halos_files = glob.glob(pattern)

# Print full file paths
for AHF_file in halos_files:
    print(AHF_file)

# Regular expression pattern to match the number between 'z' and '.AHF'
pattern = r'z(\d+\.\d+)'

# Use re.search to find the match
match = re.search(pattern, AHF_file)

# Extract the number from the match
if match:
    redshift = match.group(1)
    print(redshift)
    redshift  = float(redshift)

print(redshift)

# Read the halo catalog
df = pd.read_csv(AHF_file, delim_whitespace=True)

# Extract position and mass data
x = np.array(df['Xc(6)']) / 1000.0  # Convert to Mpc
y = np.array(df['Yc(7)']) / 1000.0
z = np.array(df['Zc(8)']) / 1000.0
mass = np.array(df['Mhalo(4)']) / h  # Mass in solar masses

# Convert positions to grid indices
grid_x = np.floor((x / boxsize) * N).astype(int)
grid_y = np.floor((y / boxsize) * N).astype(int)
grid_z = np.floor((z / boxsize) * N).astype(int)

# Ensure that grid indices stay within bounds
grid_x = np.clip(grid_x, 0, N - 1)
grid_y = np.clip(grid_y, 0, N - 1)
grid_z = np.clip(grid_z, 0, N - 1)

# Update grid mass values
for j in range(len(mass)):
    if mass[j] >= HMACH:
        HMACH_grid[grid_x[j], grid_y[j], grid_z[j]] += mass[j]
    else:
        LMACH_grid[grid_x[j], grid_y[j], grid_z[j]] += mass[j]
        supp_factor = ((mass[j] / (9 * 10**8)) - 1/9)
        if supp_factor >= 0:
            LMACH_MassDep_grid[grid_x[j], grid_y[j], grid_z[j]] += supp_factor * mass[j]

# Convert grid data into DataFrame for output
src = pd.DataFrame({
    'x': np.repeat(np.arange(1, N + 1), N * N),
    'y': np.tile(np.repeat(np.arange(1, N + 1), N), N),
    'z': np.tile(np.arange(1, N + 1), N * N),
    'HMACH': HMACH_grid.flatten(),
    'LMACH': LMACH_grid.flatten(),
    'LMACH_MassDep': LMACH_MassDep_grid.flatten()
})

# Filter out cells with no halo mass
src = src[(src['HMACH'] != 0) | (src['LMACH'] != 0) | (src['LMACH_MassDep'] != 0)]

# Write output file
output_file = f'/p/scratch/lgreion/david/full_box/DMO_1024_HR/src/src_testing/new_src_{redshift:.3f}.txt'
with open(output_file, 'w') as file:
    file.write(f"{len(src)}\n")
    src.to_csv(file, sep=' ', index=False, header=False)
