# Thermal_Conductivity_FEM_ML

Project name: 
FEM and Data-driven Analysis in Investigating Thermal Conductivity of Heterogeneous Material 

Project type: 
Course project for CIV_ENV 426-2 Advanced FEA and Data-driven Materials Performance Analysis at Northwestern University 

Project description: 
In this project, a hybrid method combining finite element analysis and data-driven analysis is proposed to investigate the thermal conductivity of a simple checkerboard heterogeneous material. Finite element analysis (FEA) is first conducted with Abaqus to study the material heat flux distribution and effective thermal conductivity under different mesh refinements and material thermal conductivity ratios. With rich data produced by FEA, we built a heat flux model which can predict element-wise heat flux under a given material thermal conductivity ratio using principal component analysis (PCA) based data compression and feed-forward neural network (FFNN) regression in machine learning. Moreover, an effective thermal conductivity model with a trained convolutional neural network (CNN) is built to directly output the effective thermal conductivity using the Abaqus heat flux contour as the input. Both models display relatively high accuracy.

Script descriptions:
  0 - This Python generates an Abaqus model of the heat conduction problem in a checkerboard made out of the repetition of N_cellsxN_cells unit cells.
  1 - This Python extracts txt data from Abaqus .odb files.
  2 - This Python extracts heat flux contours from Abaqus .odb files.
  3 - This Python crops the pic into 175x175, then resize it to 176x176.
  4 - This Python randomly divides txt data into training and testing subsets for model 1.
  5 - This Python performs PCA and trains a NN for the first model (i.e., element centroid heat flux model which estimates heat flux of each element from material thermal conductivity ratio).
  6 - This Jupyter notebook trains a CNN for the second model (i.e., effective thermal conductivity model which predicts effective thermal conductivity from input heat flux image by FEM)
  7 - This Python script computes the average heat flux analytically.
