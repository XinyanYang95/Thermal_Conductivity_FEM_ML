######################################################################################################################
#																													 #
# This Python crops the pic into 175x175, then resize it to 176x176.												 #
#																													 #
# https://machinelearningmastery.com/how-to-load-and-manipulate-images-for-deep-learning-in-python-with-pil-pillow/  #
# Standard resampling algorithms are used to invent or remove pixels when resizing, and you can specify a technique, #
# although default is a bicubic resampling algorithm that suits most general applications. 							 #
#																													 #
######################################################################################################################

from matplotlib import image
from matplotlib import pyplot
from PIL import Image

# scaled magnitude
for meshnum in [10,20,30,40,50]:
	for k2 in range(1,101):
		filename = 'pics/scaled/mesh{0}_ktwo{1}.png'.format(meshnum, k2)
		outname = 'pics/scaled/cropped/{0}_{1}.png'.format(meshnum, k2)
		thisimage = Image.open(filename)
# 		cropped = thisimage.crop((37, 24, 212, 199))
		cropped = thisimage.crop((35, 24, 213, 200))
		img_resized = cropped.resize((176,176))
		img_resized.save(outname)