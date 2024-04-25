# Provided you have a halo catalogue produced using AHF this program will read the _halos file 
# and generate the required src_{z}.txt file where the first line of the txt file contains the 
# number of sources, the 1st-3rd column contains the x,y,z indexing (in Fortran Formar i.e. starting from 1).
# The 4th and 5th column contains the halo mass in solar mass/h of the HMACH halos and LMACH halos respectively
# and the 6th column contains the LMACH masses multiplied by a factor of (1/(9x10^8) -1/9) as in eqn. 3 of
# Dixon et al. (2018) which is used for the mass-dependant suppression source model. 
# This code can be run using the batch script run_source_list.sh to run this code in parallel.

import pandas as pd
import numpy as np
import sys
import glob
import re

import glob

i = int(sys.argv[1])


AHF_directory = '/p/scratch/hestiaeor/david/HYDRO_256_4096_CRAL_KF_PAD_LMAX17/AHF/{0:03d}/halos'.format(i)


# Define the size of the mesh
N = 256
h = 0.677
HMACH = (1.43e9)/h # in solar masses

boxsize = 100 #Mpc

# Loading list of redshifts
redshifts = np.loadtxt('/p/scratch/hestiaeor/david/hestia-pyc2ray/z_list.txt')

# Create meshgrid
x, y, z = np.meshgrid(range(N), range(N), range(N))

# Flatten the meshgrid arrays
x_flat = x.flatten()
y_flat = y.flatten()
z_flat = z.flatten()

# Create DataFrame
src = pd.DataFrame({'x': x_flat+1, 'y': y_flat+1, 'z': z_flat+1, 'HMACH': np.zeros(len(x_flat)), 'LMACH': np.zeros(len(x_flat)), 'LMACH_MassDep': np.zeros(len(x_flat))})

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

df = pd.read_csv(AHF_file, delim_whitespace=True)

x = np.array(df['Xc(6)'])
y = np.array(df['Yc(7)'])
z = np.array(df['Zc(8)'])

mass = np.array(df['Mhalo(4)'])/h # Mass in solar masses


for i in range(len(x)):
    
    # First we check if Halos is an HMACH
    if mass[i] >= HMACH:
        # Calculate grid cell indices for the halo
        grid_x = int((x[i]/1000) / (boxsize / N)) +1
        grid_y = int((y[i]/1000) / (boxsize / N)) +1
        grid_z = int((z[i]/1000) / (boxsize / N)) +1
        
        src.loc[(src['x']== grid_x) & (src['y']== grid_y) & (src['z']== grid_z), 'HMACH'] = mass[i] + src.loc[(src['x']== grid_x) & (src['y']== grid_y) & (src['z']== grid_z), 'HMACH']

    if mass[i] < HMACH:
        # Calculate grid cell indices for the halo
        grid_x = int((x[i]/1000) / (boxsize / N)) +1
        grid_y = int((y[i]/1000) / (boxsize / N)) +1
        grid_z = int((z[i]/1000) / (boxsize / N)) +1
        
        src.loc[(src['x']== grid_x) & (src['y']== grid_y) & (src['z']== grid_z), 'LMACH'] = mass[i] + src.loc[(src['x']== grid_x) & (src['y']== grid_y) & (src['z']== grid_z), 'LMACH']
        
        # We use equation (3) in Dixon et al. (2018)
        src.loc[(src['x']== grid_x) & (src['y']== grid_y) & (src['z']== grid_z), 'LMACH_MassDep'] = ((mass[i]/9*10**8)-1/9) + src.loc[(src['x']== grid_x) & (src['y']== grid_y) & (src['z']== grid_z), 'LMACH_MassDep']

src = src[(src['HMACH']!=0) | (src['LMACH']!=0) | (src['LMACH_MassDep']!=0)]

with open('/p/scratch/hestiaeor/david/hestia-pyc2ray/Ramses_KF_hydro/src/src_{:.3f}.txt'.format(redshift), 'w') as file:
            # Write the number of grid cells
            file.write(f"{len(src)}\n")
            src.to_csv(file, sep=' ', index=False, header=False)

