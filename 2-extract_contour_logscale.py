###############################################################################################################
#                                                                                                             #
# This Python extracts heat flux contours from Abaqus .odb files.		   						              #
#                                                                                                             #
###############################################################################################################

import animation
from odbAccess import *
# from types import IntType
from abaqusConstants import *
import numpy as np
from numpy import *
import sys
import odbAccess
import os
from abaqus import session
import visualization
import xyPlot
from abaqusConstants import PNG, AVI, CONTOURS_ON_DEF, INTEGRATION_POINT, COMPONENT, OFF, ON, FEATURE, DISCRETE, CONTINUOUS, \
ALL_FRAMES, TIME_HISTORY, UNLIMITED, UNDEFORMED, SCALE_FACTOR, NODAL, LARGE

# meshnum = 10
for meshnum in [10, 20, 30, 40, 50, 60]:

	for k2 in range(1,101):
		# load odb file
		odbsetpath = 'mesh{0}_odb'.format(meshnum)
		odbfile = '{0}/mesh{1}_ktwo{2}-u.odb'.format(odbsetpath,meshnum, k2)
		path_filename = 'pics/scaled/mesh{1}_ktwo{2}'.format(odbsetpath,meshnum, k2)
		# set viewport
		myViewport = session.Viewport(name='myViewport', origin=(0, 0), width=63, height=63)		#pixel:248x224
		myOdb = visualization.openOdb(path=odbfile)
		myViewport.setValues(displayedObject=myOdb)
		myViewport.odbDisplay.contourOptions.setValues(numIntervals=24, intervalType=LOG) # DISCRETE CONTINUOUS
		firstStep = myOdb.steps['Step-1']
		frame1 = firstStep.frames[-1]
		plotHFLmag = frame1.fieldOutputs['HFL']
		myViewport.odbDisplay.setPrimaryVariable(field=plotHFLmag, outputPosition=INTEGRATION_POINT, refinement=(INVARIANT, 'Magnitude'))
		myViewport.odbDisplay.commonOptions.setValues(visibleEdges=NONE)
		myViewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))
		myViewport.odbDisplay.contourOptions.setValues(maxAutoCompute=OFF, maxValue=1530, minAutoCompute=OFF, minValue=0.000001,)		#check max and min (all data)  
		myViewport.viewportAnnotationOptions.setValues(triad=OFF, title=OFF, state=OFF, compass=OFF, legend=OFF, legendBox=OFF)
		myViewport.view.fitView()
		session.printOptions.setValues(rendition=COLOR, vpDecorations=OFF, vpBackground=ON)
		session.printToFile(fileName=path_filename+'.png', format=PNG, canvasObjects=(myViewport,))
		print('saved %s' % path_filename)
		myOdb.close()

print("all done!")