###############################################################################################################
#                                                                                                             #
# This Python generates an Abaqus model of the heat conduction problem in a checkerboard made                   #
# out of the repetition of N_cells*N_cells unit cells Y.                                                      #
#                                                                                                             #
# The required inputs are as listed below:                                                                    #
#   - N_cells: number of repeated cells in each direction (line 25)                                           #
#   - kappa_ratio: thermal conductivity ratio kappa2/kappa1 (line 28)                                         #
#   - nelements_tile: number of finite elements per tile side (line 31)                                       #
#   - element_order: finite element order (line 34)                                                           #
#   - periodic: impose periodicity constraints (line 37)                                                      #
#                                                                                                             #
# DISCLAIMER: This code is intended for educational purposes only. Usage for                                  #
#             any other purpose is done at the user's own risks.                                              #
#                                                                                                             #
###############################################################################################################

from abaqus import *
from assembly import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup

# number of repeated cells in each direction
N_cells=8

# thermal conductivity ratio kappa2/kappa1
kappa_ratio=4

# number of finite elements per tile side
nelements_tile=40

# finite element order
element_order=1

# periodicity constraint
periodic=False

###############################################################################################################
#                                      DO NOT CHANGE ANYTHING BELOW HERE                                      #
###############################################################################################################

nelements_side=2*N_cells*nelements_tile

if element_order==1:
    n_nodes = (nelements_side+1)**2
elif element_order==2:
    n_nodes = 3*nelements_side**2+4*nelements_side+1
else:
    raise ValueError, 'The element order is '+ str(element_order) + '. It can only be 1 or 2.'
    print (error)

# if n_nodes>250000:
#     raise ValueError, 'Total number of nodes is '+ str(n_nodes) + '. It must be below 250,000.'
#     print (error)

namefile=str(N_cells) +"_cells_" + str(nelements_tile) + "_elements_tile"

mesh_size = 1./nelements_side;

# Some shortcuts
executeOnCaeStartup()
mdb.Model(modelType=STANDARD_EXPLICIT, name=namefile)
s = mdb.models[namefile].ConstrainedSketch(name='__profile__', sheetSize=5.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)

# Create rectangle
s.rectangle(point1=(0.0, 0.0), point2=(1, 1))
p = mdb.models[namefile].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
    type=DEFORMABLE_BODY)
p = mdb.models[namefile].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models[namefile].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models[namefile].sketches['__profile__']

# Partition in between different regions
p = mdb.models[namefile].parts['Part-1']
f, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(
    0.0, 0.0, 0.0))
s1 = mdb.models[namefile].ConstrainedSketch(name='__profile__',
	sheetSize=5, gridSpacing=1, transform=t)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models[namefile].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
for k in range(1,2*N_cells):
    s1.Line(point1=(0, k/(2.*N_cells)), point2=(1., k/(2.*N_cells)))
    s1.Line(point1=(k/(2.*N_cells),0.), point2=(k/(2.*N_cells),1.))
p = mdb.models[namefile].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models[namefile].sketches['__profile__']

# Sets
p = mdb.models[namefile].parts['Part-1']
ph1=(((-1, -1, 0.0),),)
ph2=(((-1, -1, 0.0),),)
bdry=(((-1, -1, 0.0),),)
for i in range(0,2*N_cells):
    bdry=bdry+((((i+0.5)/(2*N_cells), 0.0, 0.0),),)+((((i+0.5)/(2*N_cells), 1.0, 0.0),),)
    bdry=bdry+(((0.0,(i+0.5)/(2*N_cells),  0.0),),)+(((1.0, (i+0.5)/(2*N_cells),  0.0),),)
    for j in range(0,2*N_cells):
        if (i+j)%2==1:
            ph1=ph1+((((i+0.5)/(2*N_cells), (j+0.5)/(2*N_cells), 0.0),),)
        else:
            ph2=ph2+((((i+0.5)/(2*N_cells), (j+0.5)/(2*N_cells), 0.0),),)

p.Set(faces=p.faces.findAt(*ph1),name='phase1')
p.Set(faces=p.faces.findAt(*ph2),name='phase2')
p.Set(edges=p.edges.findAt(*bdry),name='boundary')

# Material -- Section
mdb.models[namefile].Material(name='Material-1')
mdb.models[namefile].materials['Material-1'].Conductivity(table=((1.0, ), ))
mdb.models[namefile].HomogeneousSolidSection(material='Material-1', name='Material-1', thickness=None)
p = mdb.models[namefile].parts['Part-1']
pickedRegions =(p.sets['phase1'].faces, )
p.SectionAssignment(region=pickedRegions, sectionName='Material-1')

mdb.models[namefile].Material(name='Material-2')
mdb.models[namefile].materials['Material-2'].Conductivity(table=((kappa_ratio, ), ))
mdb.models[namefile].HomogeneousSolidSection(material='Material-2', name='Material-2', thickness=None)
p = mdb.models[namefile].parts['Part-1']
pickedRegions =(p.sets['phase2'].faces, )
p.SectionAssignment(region=pickedRegions, sectionName='Material-2')

# Mesh
# Seed edges
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
	meshTechnique=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
	referenceRepresentation=OFF)
p = mdb.models[namefile].parts['Part-1']
e = p.edges
p.seedEdgeBySize(edges=e, size=mesh_size, deviationFactor=0.1, constraint=FIXED)

# Set elements particle controls
p = mdb.models[namefile].parts['Part-1']
f = p.faces
p.setMeshControls(regions=f, elemShape=QUAD, technique=STRUCTURED)

#elements type
if element_order==1:
    elemType = mesh.ElemType(elemCode=DC2D4, elemLibrary=STANDARD)
elif element_order==2:
    elemType = mesh.ElemType(elemCode=DC2D8, elemLibrary=STANDARD)
else:
    raise ValueError, 'The element order is '+ str(element_order) + '. It can only be 1 or 2.'
    print (error)

# Set elements
pickedRegions =(p.sets['phase1'].faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType, elemType))

pickedRegions =(p.sets['phase2'].faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType, elemType))

# Mesh
p = mdb.models[namefile].parts['Part-1']
p.generateMesh(regions=p.faces)

session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON,
	engineeringFeatures=ON, mesh=OFF)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
	meshTechnique=OFF)

# Assembly/part
a = mdb.models[namefile].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
a = mdb.models[namefile].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models[namefile].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=ON)

if periodic:
    if element_order==1:
        nn=nelements_side+1
        sz=1./(nn-1)
    else:
        nn=2*nelements_side+1
        sz=1./(nn-1)

    p.Set(nodes=p.nodes.getByBoundingBox(xMin=-sz/3.,yMin=-sz/3.,zMin=0.,xMax=sz/3.,yMax=sz/3.,zMax=0.),name='bottom_left_corner')
    p.Set(nodes=p.nodes.getByBoundingBox(xMin=1-sz/3.,yMin=-sz/3.,zMin=0.,xMax=1+sz/3.,yMax=sz/3.,zMax=0.),name='bottom_right_corner')
    p.Set(nodes=p.nodes.getByBoundingBox(xMin=-sz/3.,yMin=1-sz/3.,zMin=0.,xMax=sz/3.,yMax=1+sz/3.,zMax=0.),name='top_left_corner')

    for k in range(1,nn):
        p.Set(nodes=p.nodes.getByBoundingBox(xMin=sz*(k-1./4.),yMin=1.-sz/4.,zMin=0.,xMax=sz*(k+1./4),yMax=1.+sz/4.,zMax=0.),name='Set-top-'+str(k))
        p.Set(nodes=p.nodes.getByBoundingBox(xMin=sz*(k-1./4.),yMin=-sz/4.,zMin=0.,xMax=sz*(k+1./4.),yMax=sz/4.,zMax=0.),name='Set-bot-'+str(k))
        mdb.models[namefile].Equation(name='Constraint-top-bot-'+str(k), terms=((
            1.0, 'Part-1-1.Set-top-'+str(k), 11), (-1.0, 'Part-1-1.Set-bot-'+str(k), 11), (-1.0, 'Part-1-1.top_left_corner', 11), (1.0, 'Part-1-1.bottom_left_corner', 11)))
        if k< nn-1:
            p.Set(nodes=p.nodes.getByBoundingBox(yMin=sz*(k-1./4.),xMin=1.-sz/4.,zMin=0.,yMax=sz*(k+1./4.),xMax=1.+sz/4.,zMax=0.),name='Set-right-'+str(k))
            p.Set(nodes=p.nodes.getByBoundingBox(yMin=sz*(k-1./4.),xMin=-sz/4.,zMin=0.,yMax=sz*(k+1./4.),xMax=sz/4.,zMax=0.),name='Set-left-'+str(k))
            mdb.models[namefile].Equation(name='Constraint-right-left-'+str(k), terms=((
                1.0, 'Part-1-1.Set-right-'+str(k), 11), (-1.0, 'Part-1-1.Set-left-'+str(k), 11), (-1.0, 'Part-1-1.bottom_right_corner', 11), (1.0, 'Part-1-1.bottom_left_corner', 11)))


mdb.models[namefile].HeatTransferStep(amplitude=RAMP, minInc=1.0, name=
    'Step-1', previous='Initial', response=STEADY_STATE)
