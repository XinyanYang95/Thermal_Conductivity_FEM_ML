###############################################################################################################
#                                                                                                             #
# This Python randomly divides txt data into training and testing subsets for model 1.		                  #
#                                                                                                             #
###############################################################################################################

import numpy as np
import shutil
import glob
import os
import sys

# change the number of training data points as needed
n_train = 70

# shuffle data
n_list = np.arange(1,101)
np.random.shuffle(n_list)

# if traning/testing folder exist, delete 
check_path = "mesh20_training"
if len(glob.glob(check_path)) != 0:
	shutil.rmtree("mesh20_training")
	shutil.rmtree("mesh20_testing")

# make directory for training/testing
os.mkdir("mesh20_training")
os.mkdir("mesh20_testing")

for i in range(1, n_train+1):
	shutil.copyfile("mesh20/mesh20_ktwo{0}.txt".format(n_list[i-1]), "mesh20_training/mesh20_ktwo{0}.txt".format(n_list[i-1]))

for i in range(n_train+1, 101):
	shutil.copyfile("mesh20/mesh20_ktwo{0}.txt".format(n_list[i-1]), "mesh20_testing/mesh20_ktwo{0}.txt".format(n_list[i-1]))