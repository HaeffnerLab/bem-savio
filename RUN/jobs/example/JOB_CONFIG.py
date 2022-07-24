'''
The file specifies the configuration for this BEM job.
'''
from bem import *
import numpy as np

# name of the stl file
STL_file = 'pyramidtrap.stl'
# units of the mesh (e.g. 1e-3 for mm)
mesh_units = 1e-3

# this position defines the center of our ROI (where we believe our RF null is located)
x0 = 0*1e-3
y0 = 10*1e-3
z0 = 2 + 1*75*1e-3

save_plots = True
save_plots_dpi = 1000
show_plots = True

# assign electrode names to each color in the stl
electrode_colors = {
    ('bem1', 'DC1'),
    ('bem2', 'DC2'),
    ('bem3', 'DC3'),
    ('bem4', 'DC4'),
    ('bem5', 'DC5'),
    ('bem6', 'DC6'),
    ('bem7', 'DC7'),
    ('bem8', 'DC8'),
    ('bem9', 'DC9'),
    ('bem10', 'DC10'),
    ('bem11', 'DC11'),
    ('bem12', 'DC12'),
    ('bem13', 'DC13'),
    ('bem14', 'DC14'),
    ('bem15', 'DC15'),
    ('bem16', 'DC16'),
    ('bem17', 'DC17'),
    ('bem18', 'DC18'),
    ('bem19', 'DC19'),
    ('bem20', 'DC20'),
    ('bem21', 'DC21'),
    ('bem22', 'RF'),
    ('bem23', 'GND'),
}

# remeshing so that we have a finer mesh to run BEM
# run.py will call this function when it is time to remesh
def remesh(mesh):
	'''
	Triangulate flags: https://www.cs.cmu.edu/~quake/triangle.switch.html or in doc/Triangle_ Command line switches.pdf
	'''
	# first triangulation 
	mesh.triangulate(opts="q10Q",new = False)

	'''
	# second triangulation
	# here we define a spherical constriant zone:
	inside=1.
	outside=10
	rad = 5*75*1e-3

	# areas_from_constraints specifies sphere with finer mesh inside it.
	mesh.areas_from_constraints(Sphere(center=np.array([x0,y0,z0]),radius=rad, inside=inside, outside=outside))
	mesh.triangulate(opts="q30Q",new = False)

	# third triangulation
	inside=1e-3
	outside=1
	rad = 3*75*1e-3

	# # areas_from_constraints specifies sphere with finer mesh inside it.
	mesh.areas_from_constraints(Sphere(center=np.array([x0,y0,z0]),radius=rad, inside=inside, outside=outside))
	mesh.triangulate(opts="q30Q",new = False)
	'''

# generating the grid for BEM simulation
# the length of each side of the grid
Lx,Ly,Lz = 0.500, 0.100 ,0.200 # in the unit of scaled length mesh_unit
# the step size of gridpoints
# s = 0.010
s=0.010
sx,sy,sz = s, s, s

use_multiprocessing = True