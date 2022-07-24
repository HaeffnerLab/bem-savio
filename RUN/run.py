import sys, os
sys.path.append('./helper_functions')
sys.path.append('./helper_functions/bemColors_lib')
sys.path.append('../../Electrodes')

from helper_functions import plot_mesh
from bemColors import bemColors
import pickle
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from bem import *
from bem.formats import stl
from multipoles import MultipoleControl
from plottingfuncns import *
from time import time
from helper_functions import run_job, write_pickle
from joblib import Parallel, delayed, cpu_count

# loading job config information
from toggle_job_here import job_directory
base = f'./jobs/{job_directory}/'
sys.path.append(f'./jobs/{job_directory}')
from JOB_CONFIG import *
# in Savio mode, plot showing is turned off and the -r flag is activated
if '-s' in sys.argv:
	print('Running in Savio mode.')
	show_plots = False
	sys.argv.append('-r')


print('RUNNING JOB ', base)

# load stl file
from bem.formats import stl
s_nta = stl.read_stl(open(base+STL_file, "rb"))
print(f'LOADED {STL_file}')

# print the colors in the stl that need to be named
bemcolors = bemColors(np.array(list(set(s_nta[2]))),('fusion360','export_stl'))
bemcolors.print_stl_colors()

# assigning electrode names to each color
for e in electrode_colors:
    bemcolors.color_electrode(*e)

# print colors that have not been assigned an electrode name
# unnamed meshes will be neglected from here on out
bemcolors.drop_colors()

mpl.rcParams['lines.linewidth'] = 0.2 
mesh = Mesh.from_mesh(stl.stl_to_mesh(*s_nta, scale=1, rename=bemcolors.electrode_colors, quiet=True))

# plot the electrodes mesh
if show_plots:
	plot_mesh(x0,y0,mesh,mesh_units, title=STL_file, fout=base+'fig1.png', save=save_plots, dpi=save_plots_dpi)

# remeshing
remesh(mesh)
if show_plots:
	plot_mesh(x0,y0,mesh,mesh_units, title=f'{STL_file} remeshed', fout=base+'fig2.png', save=save_plots, dpi=save_plots_dpi)

# the default behavior of this script is to NOT RUN the electrostatics simulation
# this is so that you can adjust the configuration file to your liking without worrying about a long script running each time
# when you are happy with the configuration, run this script with the commad line flag -r
if not '-r' in sys.argv:
	print('Exiting...to run the BEM simulation, execute this script with the -r flag')
	sys.exit()

if not os.path.exists(base + "pkls"):
	os.mkdir(base + "pkls")
prefix = base + "pkls/" + STL_file.split('.')[0]
print('PREFIX: ', prefix)

nx, ny, nz = [2*np.ceil(L/2.0/s).astype('int') for L in (Lx,Ly,Lz)]
print("SIZE:", Lx, Ly, Lz)
print("STEP:", sx, sy, sz)
print("SHAPE:", nx, ny, nz)
grid = Grid(center=(x0,y0,z0), step=(sx,sy,sz), shape=(nx, ny, nz))
# Grid center (nx, ny ,nz)/2 is shifted to origin
print("GRID ORIGIN:", grid.get_origin())
print(f'x0,y0,z0 = {x0},{y0},{z0}')

jobs = list(Configuration.select(mesh,"DC.*","RF"))    

t0 = time()
if use_multiprocessing:
    n_jobs = cpu_count()
    print(f'Running with {n_jobs} multiprocessing jobs')
    def run_map():
        Parallel(n_jobs=n_jobs)(delayed(run_job)((job, grid, prefix)) for job in jobs)
    run_map()
else:
    for job in jobs:
    	run_job((job, grid, prefix))

print(f"COMPUTING TIME: {time()-t0} s")

fout = open(prefix + '_info.pkl', 'wb')
pickle.dump((mesh_units,x0,y0,z0,grid,prefix), fout)
fout.close()