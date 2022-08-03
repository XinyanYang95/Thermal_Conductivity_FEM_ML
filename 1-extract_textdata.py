###############################################################################################################
#                                                                                                             #
# This Python extracts txt data from Abaqus .odb files.										                  #
#                                                                                                             #
###############################################################################################################

from odbAccess import *
# from types import IntType
from abaqusConstants import *
import numpy as np
from numpy import *
import sys
import odbAccess
import os

meshnum = 50
odbsetpath = 'mesh{0}_odb'.format(meshnum)

for k2 in range(1, 101):
	# Update .odb obtained from Hercules run (local Abaqus has a higer version)
	odbAccess.upgradeOdb(existingOdbPath='{0}/mesh{1}_ktwo{2}.odb'.format(odbsetpath,meshnum, k2), upgradedOdbPath='{0}/mesh{1}_ktwo{2}-u.odb'.format(odbsetpath,meshnum, k2))
	os.remove('{0}/mesh{1}_ktwo{2}.odb'.format(odbsetpath,meshnum, k2))
	os.remove('mesh{0}_ktwo{1}-upgrade.log'.format(meshnum, k2))
	odb = openOdb('{0}/mesh{1}_ktwo{2}-u.odb'.format(odbsetpath,meshnum, k2))
	file_name_to_save='extract/mesh{0}_ktwo{1}.txt'.format(meshnum, k2)

	steplast=odb.steps['Step-1'].frames[-1]
	HFL_outputs_number=len(steplast.fieldOutputs['HFL'].getSubset(position=CENTROID).values)
	nodes_number=len(steplast.fieldOutputs['HFL'].getSubset(position=CENTROID).values[0].instance.nodes)
	elements_number=len(steplast.fieldOutputs['HFL'].getSubset(position=CENTROID).values[0].instance.elements)

	HFLmag = np.zeros(elements_number)
	temp = steplast.fieldOutputs['HFL'].getSubset(position=CENTROID)
	for i in range(elements_number):
	    HFLmag[i] = temp.values[i].magnitude
	HFLmag=np.array(HFLmag)
	HFLmag=np.reshape(HFLmag,[HFLmag.size,1])

	nodes=np.arange(1,elements_number+1)
	nodes=nodes.reshape([elements_number,1])

	mag=np.append(nodes,HFLmag,axis=1)

	form='%d\t%11.7e'
	np.savetxt(file_name_to_save, mag, fmt=form)

	print 'File',file_name_to_save,'was generated with success.'

	# -------------------------------------------------------------------------------------------------------------------
	# calculate effective thermal conductivity

	BDRY=odb.rootAssembly.instances['PART-1-1'].nodeSets['BOUNDARY']

	react = odb.steps['Step-1'].frames[-1].fieldOutputs['RFL11'].getSubset(region=BDRY)
	HF1=0.
	HF2=0.
	for k in range(0,len(BDRY.nodes)):
	    HF1=HF1+react.values[k].data*BDRY.nodes[k].coordinates[0]
	    HF2=HF2+react.values[k].data*BDRY.nodes[k].coordinates[1]

	text_file = open('extract/effk_mesh{0}.txt'.format(meshnum), "a")
	text_file.write('{0}\t{1}\t{2:.6f}\t{3:.6f}\t{4:.6f}\n'.format(meshnum, k2, -HF1, -HF2, -HF1-HF2))
	text_file.close()

	odb.close()