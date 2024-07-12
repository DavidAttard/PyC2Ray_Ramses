# Program whihh provided a cube_*.dat file from a DMO sim converts it to a 
# baryonic denisty field

import numpy as np

path_to_cube = '/p/scratch/lgreion/david/full_box/DMO_512/dens_256/'
path_to_snap = '/p/scratch/lgreion/conaboy1/runs/LG_09_18/full_box/DMO_512_HR/'
save_path = './baryonic_dens/'
start_snap = 10
end_snap = 49
Ngrid = 256**3 # size of the mesh

# Cosmology
h = 0.677
OmegaB = 0.048

for i in range(start_snap,end_snap+1):
    
    with open(path_to_cube+f'cube_{i:05d}.dat', 'r') as f:
        # Read first block
        count = 3
        blksize = count * 4 # 3 32-bit (4-byte) integers
        blk = np.fromfile(f, dtype=np.int32, count=1)
        print(blk)
        nn = np.fromfile(f, dtype=np.int32, count=count)
        print(nn)
        blk = np.fromfile(f, dtype=np.int32, count=1)
        print(blk)

        count = nn[0] * nn[1] * nn[2]
        blksize = count * 4
        blk = np.fromfile(f, dtype=np.int32, count=1)
        assert(blk == blksize) # we can check we're reading in the right amount of data
        cube = np.fromfile(f, dtype=np.float32, count=count).reshape((nn[1], nn[0], nn[2]))
        
        
        pc=  3.086e18 #1 pc in cm
        Mpc = 1e6*pc
        G_grav = 6.6732e-8

        H0 = 100.0*h
        H0cgs = H0*1e5/Mpc
        

        rho_crit_0 = 3.0*H0cgs*H0cgs/(8.0*np.pi*G_grav)

        # baryonic density field in (comoving) g/cm^3
        baryonic_dens = cube*rho_crit_0*OmegaB*Ngrid 

    # Obtaining the redshift
    info_fn = path_to_snap+'output_{0:05d}/info_{0:05d}.txt'.format(i)
    with open(info_fn, 'r') as f:
        for l in f:
            if 'aexp' in l:
                aexp = float(l.strip().split()[-1])
                break

    z = (1 / aexp) - 1
    z = round(z,3)

    np.save(save_path+'dens_cgs_{:.3f}.npy'.format(z), baryonic_dens)

    
