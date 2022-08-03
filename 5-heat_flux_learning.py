###############################################################################################################
#                                                                                                             #
# This Python performs PCA and trains NN for the first model (element centroid heat flux).                    #
#                                                                                                             #
###############################################################################################################

import glob
import numpy
import os
import sys
import shutil
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse import csr_matrix
from sklearn import datasets
from sklearn import multioutput
from sklearn import svm
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.image import grid_to_graph
from subprocess import call
from time import time
from sklearn import preprocessing
from sklearn.neural_network import MLPRegressor
from matplotlib.colors import LogNorm

# get the arguments
training_data_path = "mesh20_training/mesh20_ktwo*.txt"
K = int(sys.argv[1]) # number of components for PCA
ndim = 2 #number of dimensions, 2
mesh_dims = numpy.zeros(ndim, dtype = int) # grid dimensions, 320 320
for idim in numpy.arange(0,ndim):
    mesh_dims[idim] = 16*20
testing_data_path = None  #"mesh20_testing/mesh20_ktwo*.txt"
if len(sys.argv) > 2:
    testing_data_path = sys.argv[2]

if len(glob.glob(training_data_path)) == 0:
	print("No file matches path %s" % training_data_path)
	exit(0)

#read training data
data = None
kappa_training = []
for data_file in glob.glob(training_data_path):
    kappa_training.append(int(data_file[27:-4]))
    data_file_data = numpy.loadtxt(data_file)
    data_file_data = data_file_data[:,1]  #local heat flux
    if data is None:
        data = data_file_data
    else:
        data = numpy.vstack((data,data_file_data))
print("shape of training data: {0}".format(numpy.shape(data)))   # 70x102400

# PCA compression
PCA_compresser = PCA(n_components=K)
data_heat_flux = data
PCA_compresser = PCA_compresser.fit(data_heat_flux)
#compute and display approximation error on the training set
data_heat_flux_projected = PCA_compresser.transform(data_heat_flux)
for k in numpy.arange(0,K):
    print("Explained variance ratio by weight vector %ld in training %lf" % (k, PCA_compresser.explained_variance_ratio_[k]))
print("Relative approximation error in training %lf" % (numpy.linalg.norm(PCA_compresser.inverse_transform(data_heat_flux_projected)-data_heat_flux) / numpy.linalg.norm(data_heat_flux)))

#reading testing data
if testing_data_path is not None:
    testing_data = None
    kappa_testing = []
    for data_file in glob.glob(testing_data_path):
        kappa_testing.append(int(data_file[26:-4]))
        data_file_data = numpy.loadtxt(data_file)
        data_file_data = data_file_data[:,1]  #local heat flux
        if testing_data is None:
            testing_data = data_file_data
        else:
            testing_data = numpy.vstack((testing_data,data_file_data))
    kappa_original = kappa_testing.copy()
    testing_data_heat_flux = testing_data
    testing_data_heat_flux_projected = PCA_compresser.transform(testing_data_heat_flux)

    print("shape of testing_data_heat_flux_projected: {0}".format(numpy.shape(testing_data_heat_flux_projected)))   # 30xK

    print("Relative approximation error in testing %lf" % (numpy.linalg.norm(PCA_compresser.inverse_transform(testing_data_heat_flux_projected)-testing_data_heat_flux) / numpy.linalg.norm(testing_data_heat_flux)))

    #set the input kappa for regression
    kappa_training = numpy.array(kappa_training).reshape(-1,1)
    kappa_testing = numpy.array(kappa_testing).reshape(-1,1)

    #scale the data
    Xscaler = preprocessing.StandardScaler().fit(kappa_training)
    kappa_training = Xscaler.transform(kappa_training)    # Xtrain
    kappa_testing = Xscaler.transform(kappa_testing)    # Xtest
    Yscaler = preprocessing.StandardScaler().fit(data_heat_flux_projected)
    data_heat_flux_projected = Yscaler.transform(data_heat_flux_projected)    # Ytrain
    testing_data_heat_flux_projected = Yscaler.transform(testing_data_heat_flux_projected)  #Ytest

    print("shape of kappa_training: {0}".format(numpy.shape(kappa_training)))   # 70x1
    print("shape of data_heat_flux_projected: {0}".format(numpy.shape(data_heat_flux_projected)))   # 70xK

    #predict from kappa to heat data_heat_flux
    heat_flux_regresser = multioutput.MultiOutputRegressor(MLPRegressor(hidden_layer_sizes=(50,20,10,10,), activation='relu', solver='adam', max_iter=20000, alpha=0.001, random_state=1))
    heat_flux_regresser.fit(kappa_training,data_heat_flux_projected)
    kappa_testing_heat_flux_projected = heat_flux_regresser.predict(kappa_testing)

    print("shape of kappa_testing_heat_flux_projected: {0}".format(numpy.shape(kappa_testing_heat_flux_projected)))  # 30xK

    print("Relative regression projection error in testing %lf" % (numpy.linalg.norm(kappa_testing_heat_flux_projected-testing_data_heat_flux_projected) / numpy.linalg.norm(testing_data_heat_flux_projected)))
    kappa_testing_heat_flux_projected = Yscaler.inverse_transform(kappa_testing_heat_flux_projected)
    print("Relative regression approximation error in testing %lf" % (numpy.linalg.norm(PCA_compresser.inverse_transform(kappa_testing_heat_flux_projected)-testing_data_heat_flux) / numpy.linalg.norm(testing_data_heat_flux)))

    regressed_data = PCA_compresser.inverse_transform(kappa_testing_heat_flux_projected)

    if len(glob.glob("im_testing")) != 0:
        shutil.rmtree("im_testing")
        os.mkdir("im_testing")

    #plot the testing results
    f = plt.figure(figsize=[12,0.5*testing_data_heat_flux.shape[0]])
    ax = [0] * testing_data_heat_flux.shape[0]
    for i in numpy.arange(0,testing_data_heat_flux.shape[0]):
        ax[i] = f.add_subplot(testing_data_heat_flux.shape[0],1,i+1)
        joint = numpy.vstack([testing_data_heat_flux[i,:], regressed_data[i,:]])
        joint = joint.reshape([2, mesh_dims[0]*mesh_dims[1]])
        # print("kappa: {0}".format(kappa_original[i]))
        # print(joint)
        plt.imshow(joint, cmap='gray_r', aspect='auto', norm=LogNorm())
        plt.xticks([], [])
        plt.yticks([0,1], ["FEM", "NN"], fontsize=12)
        plt.text(102400+12800/2.5, 0.5, '$\kappa_2$/$\kappa_1$={0}'.format(kappa_original[i]), horizontalalignment='center',verticalalignment='center',fontsize=12)
        if i==testing_data_heat_flux.shape[0]-1:
            plt.xticks(numpy.append(0, numpy.arange(1,9)*12800-1), numpy.append(1, numpy.arange(1,9)*12800), fontsize=12)
            plt.xlabel("Element Number", fontsize=13)
        i += 1
    plt.savefig("NNtesting.png")
    plt.close(f)