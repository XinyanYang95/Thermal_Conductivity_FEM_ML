###############################################################################################################
#                                                                                                             #
# This Python script computes the average heat flux.                                                          #
#                                                                                                             #
# The required input is as listed below:                                                                      #
#   - job_name: name of the ABAQUS Job (line 18)                                                              #
#                                                                                                             #
# DISCLAIMER: This script is intended for educational purposes only. Usage for                                #
#             any other purpose is done at the user's own risks.                                              #
#                                                                                                             #
###############################################################################################################

from odbAccess import *
from numpy import *
import sys

for job_name in ['Job-1', 'Job-2']:
	# name of the ABAQUS Job
	# job_name='Job-1'

	###############################################################################################################
	#                                      DO NOT CHANGE ANYTHING BELOW HERE                                      #
	###############################################################################################################

	odb = openOdb('%s.odb' % job_name)

	BDRY=odb.rootAssembly.instances['PART-1-1'].nodeSets['BOUNDARY']

	react = odb.steps['Step-1'].frames[-1].fieldOutputs['RFL11'].getSubset(region=BDRY)
	HF1=0.
	HF2=0.
	for k in range(0,len(BDRY.nodes)):
	    HF1=HF1+react.values[k].data*BDRY.nodes[k].coordinates[0]
	    HF2=HF2+react.values[k].data*BDRY.nodes[k].coordinates[1]

	print('*********************************')
	print('Average heat flux for Job:'+job_name)
	print(repr(-HF1), repr(-HF2))
	print('*********************************')
	odb.close()
