# Python script using the yt package to produce the required density fields in units co-moving g/cm^3
# Make sure to change the '256' values to the required coarsened grid resolution.
# You can run this script in parallel using produce_dens.sh

import yt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os 
import re
import sys


i = int(sys.argv[1])


path = '/p/scratch/hestiaeor/runs/LG_09_18/HYDRO_256_4096_CRAL_KF_PAD_LMAX17/'

path_snap = path+'output_{:05d}' .format(i)

s1 = yt.load(path_snap)

region = s1.r[::256j, ::256j, ::256j]

dens_cgs = region['gas', 'density'].in_units("g/cmcm**3")

# obtaining redshift of snap
info_fn = path+'output_{0:05d}/info_{0:05d}.txt'.format(i)

with open(info_fn, 'r') as f:
    for l in f:
        if 'aexp' in l:
            aexp = float(l.strip().split()[-1])
            break

z = (1 / aexp) - 1
z = round(z,3)

np.save('/p/scratch/hestiaeor/david/hestia-pyc2ray/Ramses_KF_hydro/dens_256_ramses_KF_hydro/dens_cgs_{:.3f}.npy'.format(z), dens_cgs)



