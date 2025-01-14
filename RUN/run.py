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
from helper_functions import run_job
from joblib import Parallel, delayed, cpu_count

job_name = sys.argv[1]
print('JOB: ',job_name)

# loading job config information
base = f'./jobs/{job_name}/'
sys.path.append(f'./jobs/{job_name}')
from JOB_CONFIG import *
remesh = None
try:
	from JOB_CONFIG import remesh
except Exception as e:
	print('No remeshing function found in JOB_CONFIG')

# in Savio mode, plot showing is turned off and the -r flag is activated
if '-s' in sys.argv:
	print('Running in Savio mode.')
	show_plots = False
	use_multiprocessing = True
	sys.argv.append('-r')


print('RUNNING JOB ', base)

# load stl file
from bem.formats import stl
try:
	s_nta = stl.read_stl(open(base+STL_file, "rb"))
	print(f'LOADED {STL_file}')
except Exception as e:
	print('Error loading file')
	print(e)
	sys.exit()

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
	plot_mesh(x0,y0,z0,mesh,mesh_units,title=STL_file, fout=base+'fig1.png', save=save_plots, dpi=save_plots_dpi, three_d=plot_three_d)

# remeshing
# if a remeshing function is defined in JOB_CONFIG, then remesh
if remesh:
	remesh(mesh)
	if show_plots:
		plot_mesh(x0,y0,z0,mesh,mesh_units, title=f'{STL_file} remeshed', fout=base+'fig2.png', save=save_plots, dpi=save_plots_dpi, three_d=plot_three_d)

# setting up the grid
nx, ny, nz = [2*np.ceil(L/2.0/s).astype('int') for L in (Lx,Ly,Lz)]
print("GRID SIZE:", Lx, Ly, Lz)
print("GRID STEP:", sx, sy, sz)
print("GRID SHAPE:", nx, ny, nz)
grid = Grid(center=(x0,y0,z0), step=(sx,sy,sz), shape=(nx, ny, nz))
# Grid center (nx, ny ,nz)/2 is shifted to origin
print("GRID ORIGIN:", grid.get_origin())
print(f'x0,y0,z0 = {x0},{y0},{z0}')

# the default behavior of this script is to NOT RUN the electrostatics simulation
# this is so that you can adjust the configuration file to your liking without worrying about a long script running each time
# when you are happy with the configuration, run this script with the commad line flag -r
if not '-r' in sys.argv:
	print('EXITING: to run the BEM simulation, execute this script with the -r flag')
	sys.exit()

if not os.path.exists(base + "pkls"):
	os.mkdir(base + "pkls")
prefix = base + "pkls/" + STL_file.split('.')[0]
print('PREFIX: ', prefix)

jobs = list(Configuration.select(mesh,"DC.*","RF"))   

# resume mode
# search for existing electrode pkls, if they are found, those electrodes are skipped
if '-R' in sys.argv:
	print('Running in resume mode')
	dirs = os.listdir(base+'/pkls')
	names = []
	for d in dirs:
		try:
			electrode = d.split('_')[-1].split('.')[0]
			if electrode=='info':
				break
			print('Skipping electrode: ', electrode)
			names.append(electrode)
		except Exception as e:
			break
	if names:
		new_jobs = []
		for j in jobs:
			if not j.name in names:
				new_jobs.append(j)
		jobs = new_jobs
print('Running electrodes:')
for j in jobs:
	print(j.name)

t0 = time()
if use_multiprocessing:
    n_jobs = cpu_count()
    for a in sys.argv:
	    if '-n='in a:
	    	n_jobs = min(n_jobs, int(a[3:]))	    		  	

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