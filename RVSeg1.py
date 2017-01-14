# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 11:16:58 2016

@author: sxd7257
"""

import sys
sys.path.append("C://Users//sxd7257//Dropbox//Python Scripts")
sys.path.append("C://Users//sxd7257//Dropbox//Python Scripts//gco_python-win")
from pygco import cut_from_graph
import numpy as np
#import matplotlib.pyplot as plt
import myFunctions as func
import pickle
import scipy.io as sio
import SimpleITK as sitk
import matplotlib.pyplot as plt
#import myFunctions as func
import scipy.ndimage.morphology as morph
import scipy.ndimage as ndi
from tables import *
#import copy
import skimage.util as skutil
import time
#import scipy.ndimage.filters as filt
from vtk import *
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import interpn
from skimage import exposure
import smallestCircle as sc
import cv2
from scipy.stats import gaussian_kde
from sklearn import mixture
import skimage.measure as measure
import skimage.morphology as skmorph
from skimage import transform as tf
import skimage.segmentation as segment
from skimage.draw import polygon
import skimage.filters as filt
import scipy.spatial as spatial
from scipy import interpolate
from skimage.draw import line
import csv
import math
from sklearn.cluster import KMeans


#IOP = sio.loadmat('N:\\ShusilDangi\\MICCAI_Segmentation_Challenge\\MatFiles\\ImageOrientations.mat')

#exec("fileName = 'LVMasks.mat'")
#matContents = sio.loadmat('N:\\ShusilDangi\\MICCAI_Segmentation_Challenge\\MatFiles\\'+fileName)
#keys = matContents.keys()
#for i in keys:
#    exec(i+"= matContents['"+i+"']")

def command_iteration(method):
    print("{0:3} = {1:10.5f} : {2}".format(method.GetOptimizerIteration(),
                                   method.GetMetricValue(),
                                   method.GetOptimizerPosition()))

    
def findOptimumTform(moving_image,fixed_image,movingMask=[],fixedMask=[],verbose=True,initializeCenteredTform=True):

    if initializeCenteredTform==True:
        initial_transform = sitk.CenteredTransformInitializer(fixed_image,moving_image,sitk.Euler3DTransform(),sitk.CenteredTransformInitializerFilter.MOMENTS)
    else:
        initial_transform = sitk.CenteredTransformInitializer(fixed_image,moving_image,sitk.Euler3DTransform(),sitk.CenteredTransformInitializerFilter.GEOMETRY)

    optimized_transform = sitk.AffineTransform(3)

    registration_method = sitk.ImageRegistrationMethod()
    
    if(len(movingMask)>0):
        registration_method.SetMetricMovingMask(movingMask)

    if(len(fixedMask)>0):
        registration_method.SetMetricFixedMask(fixedMask)

    #similarity metric settings
#    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=20)
    registration_method.SetMetricAsMeanSquares()
#    registration_method.SetMetricAsCorrelation()
#    registration_method.SetMetricAsANTSNeighborhoodCorrelation(5)
    registration_method.SetMetricSamplingStrategy(registration_method.NONE)
#    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
#    registration_method.SetMetricSamplingPercentage(0.3)
    
    registration_method.SetInterpolator(sitk.sitkLinear)
    
    #optimizer settings
#    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, convergenceMinimumValue=1e-6, convergenceWindowSize=10, estimateLearningRate=registration_method.EachIteration, maximumStepSizeInPhysicalUnits=1.0)
#    registration_method.SetOptimizerAsRegularStepGradientDescent(learningRate=1.0,minStep=1e-4,numberOfIterations=1000,relaxationFactor=0.5,gradientMagnitudeTolerance=1e-4,estimateLearningRate=registration_method.EachIteration,maximumStepSizeInPhysicalUnits=0.0)
    registration_method.SetOptimizerAsAmoeba(simplexDelta=1.0, numberOfIterations=1000, parametersConvergenceTolerance = 1e-8, functionConvergenceTolerance = 1e-4, withRestarts = True)
#    registration_method.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=0.05,maximumNumberOfCorrections=5,maximumNumberOfFunctionEvaluations=2000,costFunctionConvergenceFactor=1e+7,lowerBound=0.0,upperBound=0.0,trace=True)
    registration_method.SetOptimizerScalesFromPhysicalShift()
#    registration_method.SetOptimizerScales((1.0,1.0,0.1,0.1))    
#    registration_method.SetOptimizerScales((1.0,0.1,0.1,0.1,1.0,0.1,0.1,0.1,1.0,0.1,0.1,0.1))    
    #setup for the multi-resolution framework            
#    registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
#    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[8,3,2])
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[8,5,0])
#    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[3,2,1])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
    
    #don't optimize in-place, we would possibly like to run this cell multiple times
    #registration_method.SetInitialTransform(initial_transform, inPlace=False)
    registration_method.SetMovingInitialTransform(initial_transform)
    registration_method.SetInitialTransform(optimized_transform)
#    registration_method.SetOptimizerWeights((1.0,0.0,1.0,1.0))
    registration_method.SetOptimizerWeights((1.0,0.01,0.01,0.01,1.0,0.01,0.01,0.01,1.0,1.0,1.0,1.0))
#    registration_method.SetOptimizerWeights((1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0))
    
    #connect all of the observers so that we can perform plotting during registration
    #registration_method.AddCommand(sitk.sitkStartEvent, start_plot)
    #registration_method.AddCommand(sitk.sitkEndEvent, end_plot)
    #registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, update_multires_iterations)
    #registration_method.AddCommand(sitk.sitkIterationEvent, lambda: plot_values(registration_method))
    if(verbose):
        registration_method.AddCommand(sitk.sitkIterationEvent,lambda: command_iteration(registration_method))    
    
    #final_transform = registration_method.Execute(fixed_image,moving_image)
    #registration_method.Execute(fixed_GT,moving_GT)
    registration_method.Execute(fixed_image,moving_image)
    final_transform = sitk.Transform(optimized_transform)
    final_transform.AddTransform(initial_transform)
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
        
    return (final_transform,optimized_transform,initial_transform)    



def findOptimumSliceTform(moving_image,fixed_image,movingMask=[],fixedMask=[],verbose=True):

    initial_transform = sitk.CenteredTransformInitializer(fixed_image,moving_image,sitk.Euler2DTransform(),sitk.CenteredTransformInitializerFilter.GEOMETRY)

    optimized_transform = sitk.AffineTransform(2)

    registration_method = sitk.ImageRegistrationMethod()
    
    if(len(movingMask)>0):
        registration_method.SetMetricMovingMask(movingMask)

    if(len(fixedMask)>0):
        registration_method.SetMetricFixedMask(fixedMask)

    #similarity metric settings
#    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=20)
    registration_method.SetMetricAsMeanSquares()
#    registration_method.SetMetricAsCorrelation()
#    registration_method.SetMetricAsANTSNeighborhoodCorrelation(5)
    registration_method.SetMetricSamplingStrategy(registration_method.NONE)
#    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
#    registration_method.SetMetricSamplingPercentage(0.3)
    
    registration_method.SetInterpolator(sitk.sitkLinear)
    
    #optimizer settings
#    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, convergenceMinimumValue=1e-6, convergenceWindowSize=10, estimateLearningRate=registration_method.EachIteration, maximumStepSizeInPhysicalUnits=1.0)
#    registration_method.SetOptimizerAsRegularStepGradientDescent(learningRate=1.0,minStep=1e-4,numberOfIterations=1000,relaxationFactor=0.5,gradientMagnitudeTolerance=1e-4,estimateLearningRate=registration_method.EachIteration,maximumStepSizeInPhysicalUnits=0.0)
    registration_method.SetOptimizerAsAmoeba(simplexDelta=1.0, numberOfIterations=1000, parametersConvergenceTolerance = 1e-8, functionConvergenceTolerance = 1e-4, withRestarts = True)
#    registration_method.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=0.05,maximumNumberOfCorrections=5,maximumNumberOfFunctionEvaluations=2000,costFunctionConvergenceFactor=1e+7,lowerBound=0.0,upperBound=0.0,trace=True)
    registration_method.SetOptimizerScalesFromPhysicalShift()
#    registration_method.SetOptimizerScales((1.0,1.0,0.1,0.1))    
#    registration_method.SetOptimizerScales((1.0,0.1,0.1,0.1,1.0,0.1,0.1,0.1,1.0,0.1,0.1,0.1))    
    #setup for the multi-resolution framework            
#    registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
#    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[8,3,2])
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[0])
#    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[3,2,1])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
    
    #don't optimize in-place, we would possibly like to run this cell multiple times
    #registration_method.SetInitialTransform(initial_transform, inPlace=False)
    registration_method.SetMovingInitialTransform(initial_transform)
    registration_method.SetInitialTransform(optimized_transform)
    registration_method.SetOptimizerWeights((0.1,0.1,0.1,0.1,0.1,0.1))
    
    #connect all of the observers so that we can perform plotting during registration
    #registration_method.AddCommand(sitk.sitkStartEvent, start_plot)
    #registration_method.AddCommand(sitk.sitkEndEvent, end_plot)
    #registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, update_multires_iterations)
    #registration_method.AddCommand(sitk.sitkIterationEvent, lambda: plot_values(registration_method))
    if(verbose):
        registration_method.AddCommand(sitk.sitkIterationEvent,lambda: command_iteration(registration_method))    
    
    #final_transform = registration_method.Execute(fixed_image,moving_image)
    #registration_method.Execute(fixed_GT,moving_GT)
    registration_method.Execute(fixed_image,moving_image)
    final_transform = sitk.Transform(optimized_transform)
    final_transform.AddTransform(initial_transform)
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    return (final_transform,optimized_transform,initial_transform)    


def vector_norm(data, axis=None, out=None):
    """Return length, i.e. Euclidean norm, of ndarray along axis.

    >>> v = numpy.random.random(3)
    >>> n = vector_norm(v)
    >>> numpy.allclose(n, numpy.linalg.norm(v))
    True
    >>> v = numpy.random.rand(6, 5, 3)
    >>> n = vector_norm(v, axis=-1)
    >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=2)))
    True
    >>> n = vector_norm(v, axis=1)
    >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=1)))
    True
    >>> v = numpy.random.rand(5, 4, 3)
    >>> n = numpy.empty((5, 3))
    >>> vector_norm(v, axis=1, out=n)
    >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=1)))
    True
    >>> vector_norm([])
    0.0
    >>> vector_norm([1])
    1.0

    """
    data = np.array(data, dtype=np.float64, copy=True)
    if out is None:
        if data.ndim == 1:
            return math.sqrt(np.dot(data, data))
        data *= data
        out = np.atleast_1d(np.sum(data, axis=axis))
        np.sqrt(out, out)
        return out
    else:
        data *= data
        np.sum(data, axis=axis, out=out)
        np.sqrt(out, out)
        
        
def angle_between_vectors(v0, v1, directed=True, axis=0):
    """Return angle between vectors.

    If directed is False, the input vectors are interpreted as undirected axes,
    i.e. the maximum angle is pi/2.

    >>> a = angle_between_vectors([1, -2, 3], [-1, 2, -3])
    >>> numpy.allclose(a, math.pi)
    True
    >>> a = angle_between_vectors([1, -2, 3], [-1, 2, -3], directed=False)
    >>> numpy.allclose(a, 0)
    True
    >>> v0 = [[2, 0, 0, 2], [0, 2, 0, 2], [0, 0, 2, 2]]
    >>> v1 = [[3], [0], [0]]
    >>> a = angle_between_vectors(v0, v1)
    >>> numpy.allclose(a, [0, 1.5708, 1.5708, 0.95532])
    True
    >>> v0 = [[2, 0, 0], [2, 0, 0], [0, 2, 0], [2, 0, 0]]
    >>> v1 = [[0, 3, 0], [0, 0, 3], [0, 0, 3], [3, 3, 3]]
    >>> a = angle_between_vectors(v0, v1, axis=1)
    >>> numpy.allclose(a, [1.5708, 1.5708, 1.5708, 0.95532])
    True

    """
    v0 = np.array(v0, dtype=np.float64, copy=False)
    v1 = np.array(v1, dtype=np.float64, copy=False)
    dot = np.sum(v0 * v1, axis=axis)
    dot /= vector_norm(v0, axis=axis) * vector_norm(v1, axis=axis)
    return np.arccos(dot if directed else np.fabs(dot))


def findRotation(IOPMoving,IOPFixed):
    axisMoving = np.cross(IOPMoving[0:3],IOPMoving[3:6])
#    axisFixed = np.cross(IOPFixed[0:3],IOPFixed[3:6])
    angle = angle_between_vectors(IOPFixed[0:3],IOPMoving[0:3],directed=False)
    rotation1 = sitk.VersorTransform(tuple(axisMoving),angle)
    rotation2 = sitk.VersorTransform(tuple(axisMoving),-angle)
    tPoint1 = rotation1.TransformPoint(IOPFixed[0:3])
    tPoint2 = rotation2.TransformPoint(IOPFixed[0:3])
    if(np.sum(np.abs(np.asarray(tPoint1)-IOPMoving[0:3]))<np.sum(np.abs(np.asarray(tPoint2)-IOPMoving[0:3]))):
        rotation = sitk.VersorTransform((0,0,1),-angle)
    else:
        rotation = sitk.VersorTransform((0,0,1),angle)
    return rotation


def refineProbMap(segBP,probBP,probBPOriginal,ROIthresh):
    bpBinary = probBP>ROIthresh
    endoEdge = segment.find_boundaries(bpBinary.astype(int),connectivity=2,mode='outer',background=0)
    endo = morph.binary_fill_holes(endoEdge)
#    func.displayMontageRGB(vol,255*endoEdge)

    distEndo = morph.distance_transform_edt(np.logical_not(endoEdge),sampling=(1,1),return_distances=True,return_indices=False)
    distEndo[endo>0]=-distEndo[endo>0]
#    func.displayMontage(distEndo)
    moving_Img = sitk.GetImageFromArray(distEndo.swapaxes(0,1))
    moving_Img = sitk.Cast(moving_Img,sitk.sitkFloat32)
    moving_gt = sitk.GetImageFromArray(probBP.swapaxes(0,1))
    moving_gt = sitk.Cast(moving_gt,sitk.sitkFloat32)
    moving_gt2 = sitk.GetImageFromArray(probBPOriginal.swapaxes(0,1))
    moving_gt2 = sitk.Cast(moving_gt2,sitk.sitkFloat32)

    edgeBP = segment.find_boundaries(segBP.astype(int),connectivity=2,mode='outer',background=0)
    distBP = morph.distance_transform_edt(np.logical_not(edgeBP),sampling=(1,1),return_distances=True,return_indices=False)
    distBP[segBP>0]=-distBP[segBP>0]
#    func.displayMontage(distBP)
    fixed_Img = sitk.GetImageFromArray(distBP.swapaxes(0,1))
    fixed_Img = sitk.Cast(fixed_Img,sitk.sitkFloat32)
    
    fixed_mask = sitk.GetImageFromArray(255*segBP.swapaxes(0,1))
    fixed_mask = sitk.Cast(fixed_mask,sitk.sitkUInt8)
    
    (final_tForm,optimized_tForm,init_tForm) = findOptimumSliceTform(moving_Img,fixed_Img,[],[],verbose=False)
#    moving_RS = sitk.Resample(moving_Img, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
    moving_RSgt = sitk.Resample(moving_gt, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
    moving_RSgt2 = sitk.Resample(moving_gt2, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
#    movingS_initial = sitk.Resample(moving_Img, fixed_Img, init_tForm, sitk.sitkLinear, 0.0, fixed_image.GetPixelIDValue())
#    func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(movingS_initial).swapaxes(0,1))
#    func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(moving_Img).swapaxes(0,1))
#    func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(moving_RS).swapaxes(0,1))
#    func.displayMontageRGB(sitk.GetArrayFromImage(moving_gt).swapaxes(0,1),sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1))
#    func.displayMontageRGB(vol,255*(sitk.GetArrayFromImage(moving_gt).swapaxes(0,1)>0.5))
#    func.displayMontageRGB(vol,255*(sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1)>0.5))
    probBPRefined = sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1)
    probBPRefinedOriginal = sitk.GetArrayFromImage(moving_RSgt2).swapaxes(0,1)
    
    return(probBPRefined,probBPRefinedOriginal)



matContents = sio.loadmat('N:\\ShusilDangi\\RVSC\\TrainingSetMat\\avgVolGT.mat')
keys = matContents.keys()
for i in keys:
    exec(i+"= matContents['"+i+"']")
spacingAvgVol = spacing[0]

masks = sio.loadmat('N:\\ShusilDangi\\RVSC\\kfirROICodeMatlab\\Data\LvRvROIRVSC.mat')

# Histogram Matching Filter
histFilter = sitk.HistogramMatchingImageFilter()
histFilter.SetNumberOfHistogramLevels(256)
histFilter.SetNumberOfMatchPoints(5)
histFilter.SetThresholdAtMeanIntensity(False)

sitkMovingVol = sitk.GetImageFromArray(avgVol.swapaxes(0,2))
sitkMovingVol = sitk.Cast(sitkMovingVol,sitk.sitkFloat32)
sitkMovingVol.SetSpacing(spacingAvgVol)
sitkMovingGT = sitk.GetImageFromArray(avgGT.swapaxes(0,2))
sitkMovingGT = sitk.Cast(sitkMovingGT,sitk.sitkFloat32)
sitkMovingGT.SetSpacing(spacingAvgVol)
IOPMoving = IOP[0]

# Moving Volume
indNZ = np.nonzero(avgGT)
#indNZ = np.nonzero(avgVol)
startInd2 = (np.min(indNZ,axis=1)).astype(int)
endInd2 = (np.max(indNZ,axis=1)).astype(int)+1
movingImg = func.normalizeSlices(avgVol[startInd2[0]:int(1.25*endInd2[0]),startInd2[1]:endInd2[1],:],0,100)
#movingImg = func.normalizeSlices(avgVol[startInd2[0]:endInd2[0],startInd2[1]:endInd2[1],:],0,100)
bSlice = np.zeros((movingImg.shape[0],movingImg.shape[1]))
movingImg = np.dstack((bSlice,bSlice,movingImg,bSlice,bSlice))
movingGT = avgGT[startInd2[0]:int(1.25*endInd2[0]),startInd2[1]:endInd2[1],:]
#movingGT = avgGT[startInd2[0]:endInd2[0],startInd2[1]:endInd2[1],:]
movingGT = np.dstack((bSlice,bSlice,movingGT,bSlice,bSlice))
moving_image = sitk.GetImageFromArray(movingImg.swapaxes(0,2))
moving_image = sitk.Cast(moving_image,sitk.sitkFloat32)
moving_image.SetSpacing(spacingAvgVol)
#moving_image = histFilter.Execute(moving_image,fixed_image)
moving_GT = sitk.GetImageFromArray(movingGT.swapaxes(0,2))
moving_GT = sitk.Cast(moving_GT,sitk.sitkFloat32)
moving_GT.SetSpacing(spacingAvgVol)
#func.displayMontage(sitk.GetArrayFromImage(moving_image).swapaxes(0,2),5)
#func.displayMontage(movingGT,5)


# Fixed Volume
#indNG = [40,42,99]   # Patients with variable array sizes
#indNG = [8,25,37,40,42,43,47,75,92,99]  # Patients with bad meshes
indices = range(0,16)
#indices = range(16,48)
#for i in indNG: indices.remove(i)

execTime = np.zeros(16)
#14,20,37,46[ok],47,58,64,86[Long],
#28,33[intensity],37[cut],58[bad],86[Long],
#indices = [7,27,28,33,37,43,58,86]
#indices = [7[ok],27,28,33,86]
#indices = [33,86]
#indices = [2]
# not so good patients: 97,86,64,36,35,33,31,29,28,27,22,20,16,9
#indices = [12,17,18,26,52]

#diceFile = open('dice.csv','wb')
#wDice = csv.writer(diceFile,delimiter=',',quoting=csv.QUOTE_NONE)
#jaccardFile = open('jaccard.csv','wb')
#wJaccard = csv.writer(jaccardFile,delimiter=',',quoting=csv.QUOTE_NONE)
#sensitivityFile = open('sensitivity.csv','wb')
#wSensitivity = csv.writer(sensitivityFile,delimiter=',',quoting=csv.QUOTE_NONE)
#specificityFile = open('specificity.csv','wb')
#wSpecificity = csv.writer(specificityFile,delimiter=',',quoting=csv.QUOTE_NONE)
#PPVFile = open('PPV.csv','wb')
#wPPV = csv.writer(PPVFile,delimiter=',',quoting=csv.QUOTE_NONE)
#NPVFile = open('NPV.csv','wb')
#wNPV = csv.writer(NPVFile,delimiter=',',quoting=csv.QUOTE_NONE)

# ind = [0,6,7,9,]

for ind in indices[14:15]:
#    ind = 5
    startTime = time.time()
    fileName = 'rawData'+str(ind)+'.mat'
    matContents = sio.loadmat('N:\\ShusilDangi\\RVSC\\TrainingSetMat\\'+fileName)
#    matContents = sio.loadmat('N:\\ShusilDangi\\RVSC\\TestSetMat\\'+fileName)
    keys = matContents.keys()
    for i in keys:
        exec(i+"= matContents['"+i+"']")
    v = np.copy(func.stretchContrast(vol[:,:,:,0],0,99))
#    v = np.copy(func.normalizeSlices(vol[:,:,:,0],0,99))
#    func.displayMontage(v,5)
    spacingFixed = np.copy(spacing[0])
    sitkFixedVol = sitk.GetImageFromArray(v.swapaxes(0,2))
    sitkFixedVol = sitk.Cast(sitkFixedVol,sitk.sitkFloat32)
    sitkFixedVol.SetSpacing(spacingFixed)
    sitkFixedGT = sitk.GetImageFromArray(bp[:,:,:,0].swapaxes(0,2))
    sitkFixedGT = sitk.Cast(sitkFixedGT,sitk.sitkFloat32)
    sitkFixedGT.SetSpacing(spacingFixed)
#    func.displayMontageRGB(v,255*bp[:,:,:,0],5)
    exec('mask = masks[\'lvRvMask'+str(ind)+'\']')
#    maskVol = np.zeros(v.shape)
    maskVol = np.tile(mask,(v.shape[2],1,1))
    maskVol = np.transpose(maskVol,[1,2,0])
#    maskVol,_ = func.getCircularMask(mask,vol.shape[0:3],1.2)
#    #    func.displayMontage(np.multiply(v,maskVol),5)
    sitkMaskVol = sitk.GetImageFromArray(maskVol.swapaxes(0,2))
    sitkMaskVol = sitk.Cast(sitkMaskVol,sitk.sitkFloat32)
    sitkMaskVol.SetSpacing(spacingFixed)
    IOPFixed = IOP[0]
    
    rotation = findRotation(IOPFixed,IOPMoving)
    centerFixed = tuple(map(lambda x,y:x*y/2,sitkFixedVol.GetSize(),sitkFixedVol.GetSpacing()))
    rotation.SetCenter(centerFixed)
    sitkFixedVol = sitk.Resample(sitkFixedVol, sitkFixedVol, rotation, sitk.sitkLinear, 0.0, sitkFixedVol.GetPixelIDValue())
    sitkFixedGT = sitk.Resample(sitkFixedGT, sitkFixedGT, rotation, sitk.sitkLinear, 0.0, sitkFixedGT.GetPixelIDValue())
    sitkMaskVol = sitk.Resample(sitkMaskVol, sitkMaskVol, rotation, sitk.sitkLinear, 0.0, sitkMaskVol.GetPixelIDValue())
    rotVol = sitk.GetArrayFromImage(sitkFixedVol).swapaxes(0,2)
    rotGT = sitk.GetArrayFromImage(sitkFixedGT).swapaxes(0,2)
    rotMask = sitk.GetArrayFromImage(sitkMaskVol).swapaxes(0,2)
    
    indNZ = np.nonzero(rotMask)
#    indNZ = np.nonzero(rotVol)
    startInd1 = (np.min(indNZ,axis=1)).astype(int)
    endInd1 = (np.max(indNZ,axis=1)).astype(int)+1
#    endInd1[2] = min(endInd1[2],maskVol.shape[2])
    endInd1[2] = min(endInd1[2],v.shape[2])
    
    indApexBase = np.nonzero(bp[:,:,:,0])
    startIndApex = np.min(indApexBase,axis=1)
    endIndBase = np.max(indApexBase,axis=1)+1
#    cropVol = func.normalizeSlices(rotVol[startInd1[0]:endInd1[0],int(0.9*startInd1[1]):endInd1[1],startIndApex[2]:endIndBase[2]],0,100)
#    cropVol = func.normalizeSlices(rotVol[startInd1[0]:endInd1[0],startInd1[1]:endInd1[1],startIndApex[2]:endIndBase[2]],0,100)
    cropVol = func.normalizeSlices(rotVol[startInd1[0]:endInd1[0],startInd1[1]:endInd1[1],:],0,100)
    bSlice = np.zeros((cropVol.shape[0],cropVol.shape[1]))
    cropVol = np.dstack((bSlice,bSlice,cropVol,bSlice,bSlice))
    
    fixedImg = cropVol
#    fixedGT = rotGT[startInd1[0]:endInd1[0],int(0.9*startInd1[1]):endInd1[1],startIndApex[2]:endIndBase[2]]
#    fixedGT = rotGT[startInd1[0]:endInd1[0],startInd1[1]:endInd1[1],startIndApex[2]:endIndBase[2]]
    fixedGT = rotGT[startInd1[0]:endInd1[0],startInd1[1]:endInd1[1],:]
    fixedGT = np.dstack((bSlice,bSlice,fixedGT,bSlice,bSlice))
#    func.displayMontageRGB(fixedImg,fixedGT,5)
#    fixedMask = rotMask[startInd1[0]:endInd1[0],int(0.9*startInd1[1]):endInd1[1],:]
#    fixedMask = rotMask[startInd1[0]:endInd1[0],startInd1[1]:endInd1[1],startIndApex[2]:endIndBase[2]]
    fixedMask = rotMask[startInd1[0]:endInd1[0],startInd1[1]:endInd1[1],:]
    fixed_image = sitk.GetImageFromArray(fixedImg.swapaxes(0,2))
    fixed_image = sitk.Cast(fixed_image,sitk.sitkFloat32)
    fixed_image.SetSpacing(spacing[0])
    fixed_GT = sitk.GetImageFromArray(fixedGT.swapaxes(0,2))
    fixed_GT = sitk.Cast(fixed_GT,sitk.sitkFloat32)
    fixed_GT.SetSpacing(spacing[0])
    fixed_mask = sitk.GetImageFromArray(fixedMask.swapaxes(0,2))
    fixed_mask = sitk.Cast(fixed_mask,sitk.sitkUInt8)
    fixed_mask.SetSpacing(spacing[0])
#    func.displayMontage(fixedImg,5)
#    func.displayMontage(255*fixedGT,5)
    func.displayMontageRGB(fixedImg,255*fixedGT,5)
    
    
    # Histogram Match moving image to fixed image    
    fixed_image = histFilter.Execute(fixed_image,moving_image)    
    #moving_image = histFilter.Execute(moving_image,fixed_image)
    
    #zScaling = ((moving_image.GetSize()[2])*moving_image.GetSpacing()[2])/(fixed_image.GetSize()[2]*fixed_image.GetSpacing()[2])
    zScaling = 1
    scalingTform = sitk.AffineTransform(3)
    scalingTform.Scale((1,1,zScaling))
    resampleFlt = sitk.ResampleImageFilter()
    resampleFlt.SetTransform(scalingTform)
    resampleFlt.SetInterpolator(sitk.sitkLinear)
    resampleFlt.SetOutputOrigin(moving_image.GetOrigin())
    resampleFlt.SetOutputDirection(moving_image.GetDirection())
    resampleFlt.SetOutputPixelType(moving_image.GetPixelIDValue())
    resampleFlt.SetOutputSpacing(moving_image.GetSpacing())
    resampleFlt.SetSize((moving_image.GetSize()[0],moving_image.GetSize()[1],fixed_image.GetSize()[2]))
    moving_image1 = resampleFlt.Execute(moving_image)
    resampleFlt.SetOutputPixelType(moving_GT.GetPixelIDValue())
    moving_GT1 = resampleFlt.Execute(moving_GT)
    movingGT1 = sitk.GetArrayFromImage(moving_GT1).swapaxes(0,2)
    
#    moving_image = sitk.Resample(moving_image,(moving_image.GetSize()[0],moving_image.GetSize()[1],fixed_image.GetSize()[2]),scalingTform,sitk.sitkLinear
#    func.displayMontage(sitk.GetArrayFromImage(moving_image1).swapaxes(0,2),5)
#    func.displayMontage(sitk.GetArrayFromImage(moving_GT1).swapaxes(0,2),5)
    
    (final_transform,optimized_transform,init_transform) = findOptimumTform(moving_image1,fixed_image,[],fixed_mask,verbose=True)
    moving_resampled = sitk.Resample(moving_image1, fixed_image, final_transform, sitk.sitkLinear, 0.0, fixed_image.GetPixelIDValue())
    moving_resampledGT = sitk.Resample(moving_GT1, fixed_GT, final_transform, sitk.sitkLinear, 0.0, fixed_GT.GetPixelIDValue())
    moving_initial = sitk.Resample(moving_image1, fixed_image, init_transform, sitk.sitkLinear, 0.0, fixed_image.GetPixelIDValue())
    
#    func.displayMontageRGB(sitk.GetArrayFromImage(fixed_image).swapaxes(0,2),sitk.GetArrayFromImage(moving_initial).swapaxes(0,2),5)
    func.displayMontageRGB(sitk.GetArrayFromImage(fixed_image).swapaxes(0,2),sitk.GetArrayFromImage(moving_resampledGT).swapaxes(0,2),5)
#    func.displayMontageRGB(255*sitk.GetArrayFromImage(fixed_GT).swapaxes(0,2),sitk.GetArrayFromImage(moving_resampledGT).swapaxes(0,2),5)
##    func.displayMontageRGB(fixedGT,255*(sitk.GetArrayFromImage(moving_resampledGT).swapaxes(0,2)>0),5)
#    func.displayMontageRGB(sitk.GetArrayFromImage(fixed_image).swapaxes(0,2),sitk.GetArrayFromImage(moving_resampled).swapaxes(0,2),5)

    fixedImg = fixedImg[:,:,2:-2]
    fixedGT = fixedGT[:,:,2:-2]
    movingNew = sitk.GetArrayFromImage(moving_resampled).swapaxes(0,2)
    movingNew = movingNew[:,:,2:-2]
    movingNewGT = sitk.GetArrayFromImage(moving_resampledGT).swapaxes(0,2)
    movingNewGT = movingNewGT[:,:,2:-2]
#    mask = rotMask[:,:,2:-2]
#    func.displayMontageRGB(movingNew,movingNewGT,5)
#    func.displayMontageRGB(fixedImg,movingNewGT,5)
#
#    ##################################################################################################################################################
#    ########################### Process slicewise ################################
#    
    # This is the order individual slices are processed
    sliceIDs = range(fixedImg.shape[2])
    midInd = int(np.floor(len(sliceIDs)/2))
    indOrder = []
#    processOrder = []
    for i in range(midInd,-1,-1):
        indOrder.append(i)
        if(i!=0):
            indOrder.append(-i)
    if(np.all(fixedImg[:,:,indOrder[0]]==fixedImg[:,:,indOrder[1]])):
        indOrder.remove(-midInd)
            
    movingRefined = np.zeros(movingNew.shape)
    movingRefinedGT = np.zeros(movingNew.shape)
    
#    bpGT = 255-movingNewGT
#    bpGT = bpGT/bpGT.max()
#    ROI = movingNewGT>10
#    func.displayMontage(255*(ROI),5)
#    imgCtr = np.round(np.asarray(fixedImg.shape[0:2]).astype(float)/2).astype(int)
    bpVol = np.zeros(fixedImg.shape)
    bpVolRaw = np.zeros(fixedImg.shape)
    bpProb = np.zeros(fixedImg.shape)
    bpProbOriginal = np.zeros(fixedImg.shape)
    bpVolNonEmpty = np.zeros(fixedImg.shape)
    bpVolOriginal = np.zeros(fixedImg.shape)
#    cumMask = np.zeros((fixedImg.shape[0],fixedImg.shape[1]))
#    myoVol = np.zeros(fixedImg.shape)
#    myoVolOriginal = np.zeros(fixedImg.shape)
#    myoVolNonEmpty = np.zeros(fixedImg.shape)
#    myoVolRef = np.zeros(fixedImg.shape)
    gBP = mixture.GMM(n_components=1)
    gBG = mixture.GMM(n_components=2)

    sliceNo = np.arange(bpVol.shape[2])
    sliceNo[sliceNo>=midInd] = midInd

    midProbMap = movingNewGT[:,:,midInd]/movingNewGT[:,:,midInd].max()
#    func.displayMontage(midProbMap)

# Initializations
    bpROI = np.zeros(fixedImg[:,:,0].shape)
    processSlice = 0
    isMyoApex = False

    gmmInit = mixture.GMM(n_components=3)

    for idx in indOrder:
    
        vol = fixedImg[:,:,idx].astype(int)
        volFlt = filt.median(fixedImg[:,:,idx]/fixedImg[:,:,idx].max(),skmorph.disk(3))
#        vol = filt.gaussian_filter(fixedImg[:,:,idx]/fixedImg[:,:,idx].max(),sigma=1)
#        vol = ndi.maximum_filter(fixedImg[:,:,idx]/fixedImg[:,:,idx].max(),(4,4))
        volFlt = func.normalizeSlices(volFlt,0,100)
#        vol = np.copy(volFlt)
#        func.displayMontage(vol)
        gt = fixedGT[:,:,idx]
        bgInt = []
        bpInt = []

        if(idx==midInd):
            nearbySlice=idx
        elif(idx<0):
            nearbySlice=idx-1
        else:
            nearbySlice=idx+1
#        print(idx,nearbySlice)
    ########################################################################################################################
    ######### Segment the Bloodpool ########################################################################################    
#        try:
#        ROIthresh = max(0.8-float(sliceNo[idx])/10,0.5)

        if(np.sum(movingNewGT[:,:,idx])!=0):
            probBP = movingNewGT[:,:,idx]/movingNewGT[:,:,idx].max()
            probBPOriginal = movingNewGT[:,:,idx]
            bpVolNonEmpty[:,:,idx] = movingNewGT[:,:,idx]
        else:
            probBP = bpVolNonEmpty[:,:,nearbySlice]/bpVolNonEmpty[:,:,nearbySlice].max()
            probBPOriginal = bpVolNonEmpty[:,:,nearbySlice]
            bpVolNonEmpty[:,:,idx] = bpVolNonEmpty[:,:,nearbySlice]

        ROIthresh = np.mean(probBP[probBP>0])
#        print(ROIthresh)
#        func.displayMontageRGB(vol,255*probBP)
        ROI = fixedMask[:,:,0]>0
        ROI = skmorph.remove_small_objects(ROI,min_size=20,connectivity=1)
#        ROI = probBP>0.01
#        if(idx>0):
#            endo = probBP>0.01
#        else:
#            endo = probBP>ROIthresh
##            endo = np.logical_and(endo>0,np.sum(bpVol,axis=2))
#            endo = np.logical_and(endo>0,ROI)
        if(idx>0):
            endo = probBP>0.01
        else:
            endo = probBP>ROIthresh
        endo = np.logical_and(endo>0,ROI)
        if(np.sum(bpVol[:,:,nearbySlice]>0)):
            endo = np.logical_or(endo,bpVol[:,:,nearbySlice])

#        ROI = np.copy(endo)
#        func.displayMontageRGB(vol,255*ROI)
#        func.displayMontageRGB(vol,255*endo)
#        if(np.sum(bpVol[:,:,nearbySlice])>0):
#            endo = np.logical_and(endo>0,bpVol[:,:,nearbySlice])
#        func.displayMontageRGB(vol,255*endo)
#        
        endoVol = np.multiply(volFlt,endo)
#        endoVol = np.multiply(vol,endo)
#        func.displayMontage(endoVol)
        threshOtsu = filt.threshold_otsu(endoVol[endo>0].ravel())
        
        clustrs = gmmInit.fit_predict(endoVol[endo>0].reshape(-1,1))
#        clustrs[clustrs==0]=3
        (x,y) = np.nonzero(endo)
        initSeg = np.empty(endo.shape)
        initSeg[:] = np.NAN
        initSeg[x,y] = clustrs
#        func.displayMontage(initSeg)
        sortInd = np.argsort(gmmInit.means_,axis=0)
        bpGMM = initSeg==sortInd[2][0]
        threshGMM = np.min(endoVol[bpGMM>0].ravel())
#        func.displayMontageRGB(vol,255*bp)
#        
        thresh = (threshOtsu*threshGMM)**0.5

#        bp = endoVol>=thresh
        bp = endoVol>=threshOtsu
#        bp = skmorph.opening(bp,skmorph.disk(5))
#        if(np.sum(bp)==0):
#            bp = endoVol>=threshOtsu
#        func.displayMontageRGB(vol,255*bp)

        
#        labeledImg,nLabels = measure.label(bp,background=0,return_num=True,connectivity=1)
#        labeledImg[labeledImg==0]=nLabels
#        labeledImg[labeledImg==-1]=0
#        props = measure.regionprops(labeledImg)
#        area = []
#        for k in range(len(props)):
#            area.append(props[k].area)
#        maxArea = max(area)
#
#        if(nLabels>1):
#            bp = skmorph.remove_small_objects(bp,min_size=0.5*maxArea,connectivity=1)
#        bp = morph.binary_fill_holes(bp)
##        func.displayMontageRGB(vol,255*bp)

#        if(np.sum(bpVol[:,:,nearbySlice])==0):
#            bpMask1 = func.findBPSegment(bp,endo)
#        else:
#            bpMask = func.findBPSegment(bp,bpVol[:,:,nearbySlice])
            
        bpMask1 = func.findBPSegment(bp,endo)
        bpMask2 = np.zeros(bpMask1.shape)
        if(np.sum(bpVol[:,:,nearbySlice])>0):
            bpMask2 = func.findBPSegment(bp,bpVol[:,:,nearbySlice])
        bpMask = np.logical_or(bpMask1,bpMask2)

#        bpMask = np.copy(bp)
        _,nLabels = measure.label(bpMask,background=0,return_num=True,connectivity=1)
        r = 1
        while(nLabels>1):
            bpMask = skmorph.closing(bpMask,skmorph.disk(r))
            _,nLabels = measure.label(bpMask,background=0,return_num=True,connectivity=1)
            r+=1
##        func.displayMontageRGB(vol,255*bpMask)
##        func.displayMontageRGB(vol,255*bpVol[:,:,nearbySlice])
##        if(np.sum(bpVol[:,:,nearbySlice])>0):
##            bpMask = np.logical_and(bpMask,bpVol[:,:,nearbySlice])
        bpMaskInitial = np.copy(bpMask)
        segBP = bpMask>0
        segBP = morph.binary_fill_holes(segBP)
#        func.displayMontageRGB(vol,255*segBP)
        
#        if(idx==0 and np.sum(segBP)>np.sum(bpVol[:,:,nearbySlice])):
#            bp = np.multiply(endoVol<=thresh,endo)>0
#    #        bpMask = skmorph.convex_hull_image(bp)
#            _,nLabels = measure.label(bp,background=0,return_num=True,connectivity=1)
#    #        if(idx==0):     #Special processing for first apical slice
#    #            if()
#    
#            if(nLabels>1):
#                bp = skmorph.remove_small_objects(bp,min_size=20,connectivity=1)
#            bp = morph.binary_fill_holes(bp)
#    #        try:
#            bpMask = func.findBPSegment(bp,bp)
#            bpMaskInitial = np.copy(bpMask)
#    #            bpMask = skmorph.convex_hull_image(bpMask)
#            segBP = skmorph.convex_hull_image(bpMask)
#            myoApex = np.copy(segBP)
#            isMyoApex = True
#            continue
                
##        except:
##            continue
#        ## If probability map doesn't have distinct bp region
#        if(nLabelsBP==1):
#            endo = probMyo>0.1
#            endoEgde = segment.find_boundaries(endo.astype(int),mode='outer')
##            func.displayMontageRGB(vol,255*endo)
#            
#            distEndo = morph.distance_transform_edt(np.logical_not(endoEdge),sampling=(1,1),return_distances=True,return_indices=False)
##            regBP = morph.binary_fill_holes(distMyo==0)
##            distMyo = np.multiply(distMyo,regBP)
#            distEndo[endo>0]=-distEndo[endo>0]
##            func.displayMontage(distEndo)
#            moving_Img = sitk.GetImageFromArray(distEndo.swapaxes(0,1))
#            moving_Img = sitk.Cast(moving_Img,sitk.sitkFloat32)
#            moving_gt = sitk.GetImageFromArray(probMyo.swapaxes(0,1))
#            moving_gt = sitk.Cast(moving_gt,sitk.sitkFloat32)
#            moving_gt2 = sitk.GetImageFromArray(probMyoOriginal.swapaxes(0,1))
#            moving_gt2 = sitk.Cast(moving_gt2,sitk.sitkFloat32)
#                        
#            edgeBP = segment.find_boundaries(segBP.astype(int),connectivity=2,mode='outer',background=0)
##            distBP = morph.distance_transform_edt(segBP,sampling=(1,1),return_distances=True,return_indices=False)
#            distBP = morph.distance_transform_edt(np.logical_not(edgeBP),sampling=(1,1),return_distances=True,return_indices=False)
#            distBP[segBP>0]=-distBP[segBP>0]
##            func.displayMontage(distBP)
#            fixed_Img = sitk.GetImageFromArray(distBP.swapaxes(0,1))
#            fixed_Img = sitk.Cast(fixed_Img,sitk.sitkFloat32)
#            
#            fixed_mask = sitk.GetImageFromArray(255*segBP.swapaxes(0,1))
#            fixed_mask = sitk.Cast(fixed_mask,sitk.sitkUInt8)
#            
#            (final_tForm,optimized_tForm,init_tForm) = findOptimumSliceTform(moving_Img,fixed_Img,[],[],verbose=False)
#            moving_RS = sitk.Resample(moving_Img, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
#            moving_RSgt = sitk.Resample(moving_gt, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
#            moving_RSgt2 = sitk.Resample(moving_gt2, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
##            sitkROI_RS = sitk.Resample(sitkROI, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
#            movingS_initial = sitk.Resample(moving_Img, fixed_Img, init_tForm, sitk.sitkLinear, 0.0, fixed_image.GetPixelIDValue())
##            func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(movingS_initial).swapaxes(0,1))
##            func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(moving_Img).swapaxes(0,1))
##            func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(moving_RS).swapaxes(0,1))
##            func.displayMontageRGB(sitk.GetArrayFromImage(moving_gt).swapaxes(0,1),sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1))
##            func.displayMontageRGB(vol,255*(sitk.GetArrayFromImage(moving_gt).swapaxes(0,1)>0.5))
##            func.displayMontageRGB(vol,255*(sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1)>0.5))
#            probMyoRefined = sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1)
#            probMyoRefinedOriginal = sitk.GetArrayFromImage(moving_RSgt2).swapaxes(0,1)
#            myoVol[:,:,idx] = probMyoRefined
#            myoVolOriginal[:,:,idx] = probMyoRefinedOriginal
##            bpVol[:,:,idx] = fourierSmoothing(segBP,4)
#            bpVol[:,:,idx] = segBP
#            try:
#                bpVolRaw[:,:,idx] = func.fourierSmoothing(segBP,4)
#            except:
#                bpVolRaw[:,:,idx] = np.copy(segBP)
#            continue
        
#        segBG = np.zeros(bpMask.shape)
#        func.displayMontageRGB(vol,255*segBP)
        
#        if(np.sum(bpVol[:,:,nearbySlice])>0):
#            (probBP,probBPOriginal) = refineProbMap(segBP,probBP,probBPOriginal,ROIthresh)

#        func.displayMontageRGB(vol,probBP)
#        func.displayMontageRGB(vol,255*bpMask)
#        func.displayMontageRGB(vol,255*bp)
        
#        func.displayMontage(bpGT)
#        func.displayMontage(np.multiply(ROI,vol))
        
        # Initialization
        params = np.array([0,0,0,0,0,0])
        newParams = np.array([1,0,0,1,0,0])
#        newParams = np.array([1,1,1,1,1,1])
        itr = 0
        dd = 0.7
        print('')
        print('')
        print('PROCESSING SLICE : ',idx)
        dice = 0
#        percentile = 60

        try:
#            while(np.any(np.abs(params-newParams)>0.1) and itr<10):
            while(dice<0.99 and itr<10):
                itr += 1
#                print(itr)
                segBPOld = np.copy(segBP)
    
                indBP = np.nonzero(bpMask)
                indBPInv = np.nonzero(np.logical_xor(bpMask,ROI))
#                func.displayMontageRGB(vol,255*bpMask)
#                func.displayMontageRGB(vol,255*np.logical_xor(bpMask,ROI))
                for i in vol[indBP[0],indBP[1]]: bpInt.append(i)
                gBP.fit(np.asarray(bpInt).reshape(-1,1))
    #            bpSamples = gBP.sample(len(vol[indBP[0],indBP[1]].ravel()))
    #            plt.figure()
    #            plt.hist(vol[indBP[0],indBP[1]].ravel(),bins=np.arange(255),normed=True)
    #            plt.hist(bpSamples,bins=np.arange(255),normed=True)
                
                for i in vol[indBPInv[0],indBPInv[1]]: bgInt.append(i)
                gBG.fit(np.asarray(bgInt).reshape(-1,1))
    #            bgSamples = gBG.sample(len(vol[indBPInv[0],indBPInv[1]].ravel()))
    #            plt.figure()
    #            plt.hist(vol[indBPInv[0],indBPInv[1]].ravel(),bins=np.arange(255),normed=True)
    #            plt.hist(bgSamples,bins=np.arange(255),normed=True)
                
                xx = gBP.score(np.arange(0,256).reshape(-1,1))
                yy = gBG.score(np.arange(0,256).reshape(-1,1))
#                fig,ax = plt.subplots()
#                ax.plot(xx,'k--',label="BP loglikelihood")
#                ax.plot(yy,'b',label="BG loglikelihood")
#                legend = ax.legend(loc='upper right')

                # create unaries based on intensity likelihood
                unariesLLS = 10*xx[vol]
#                if(itr>1):
                unariesLLS[bpMask>0]=100
                unariesLLT = 10*yy[vol]
#                unariesLLS = np.round(gBP.score(vol.reshape(-1,1))).reshape(ROI.shape)
#                unariesLLT = np.round(gBG.score(vol.reshape(-1,1))).reshape(ROI.shape)
#                func.displayMontage(unariesLLS-unariesLLT,5)
        #        func.displayMontage(unariesLLS,5)
        #        func.displayMontage(unariesLLT,5)
                
                atlasGT = np.copy(np.multiply(probBP,ROI))
                atlasGT = atlasGT.astype(float)/atlasGT.max()
#                func.displayMontage(atlasGT)
#                func.displayMontageRGB(vol,255*atlasGT)
#                func.displayMontageRGB(vol,1-atlasGT)
            
            #    # create unaries based on atlas shape
#                unariesAtlS = np.round(np.log(atlasGT+sys.float_info.epsilon))
#                unariesAtlT = np.round(np.log(1-atlasGT+sys.float_info.epsilon))
##        #        func.displayMontage(unariesAtlS,5)
##        #        func.displayMontage(unariesAtlT,5)
###                func.displayMontage(unariesAtlS-unariesAtlT,5)
##            
#    #            wAtl = (1-np.exp(-itr**2+1))
#                wAtl = (1-np.exp(-itr/5.0)) #sliceNo**0.5))
#    #            wAtl = (float(itr**2)/(itr**2+10))
#                unariesS = (1-wAtl)*unariesLLS+wAtl*unariesAtlS
##                unariesS[bpMask>0]=100
#                unariesT = (1-wAtl)*unariesLLT+wAtl*unariesAtlT
###                unariesS = 10*unariesLLS+1*unariesAtlS
###                unariesT = 10*unariesLLT+1*unariesAtlT
            
#                LL = 10*(unariesS-unariesT)
                LL = unariesLLS-unariesLLT
#                func.displayMontage(LL)
#                LLSeg = 10*np.copy(LL)
#                LLSeg[bpMask>0]=100
#                func.displayMontage(LLSeg)
#                LL[bp>0]=100
#                LL = 10*LL
#                LL[segBG>0]=-100
                # for visualization purposes
#                func.displayMontage(LL)
#                func.displayMontage(unariesS,5)
                #func.displayMontage(unariesT,5)
                #func.displayMontage(vol,5)
#                func.displayMontageRGB(LL,atlasGT)
            #    
                # as we convert to int, we need to multipy to get sensible values
#                unaries = np.stack([LLSeg, -LLSeg],axis=-1).copy("C").astype(np.int32)
                unaries = np.stack([unariesLLS, unariesLLT],axis=-1).copy("C").astype(np.int32)
#                unaries = np.stack([unariesS, unariesT],axis=-1).copy("C").astype(np.int32)
                # create potts pairwise
                pairwise = -np.eye(2, dtype=np.int32)
                
                # use the gerneral graph algorithm
                # first, we construct the grid graph
                inds = np.arange(vol.size).reshape(vol.shape)
                horz = np.c_[inds[:,:-1].ravel(), inds[:,1:].ravel()]   # horizontal edges
                vert = np.c_[inds[:-1,:].ravel(), inds[1:,:].ravel()]   # vertical edges
            #    depth = np.c_[inds[:,:,:-1].ravel(), inds[:,:,1:].ravel()]  # slice edges
                edges = np.vstack([horz, vert]).astype(np.int32)
    #            eWeight = -1*np.absolute((vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]])/10).reshape(edges.shape[0],1)
#                eWeight1 = 5*itr*np.exp(-10*np.absolute(LL.ravel()[edges[:,0]]-LL.ravel()[edges[:,1]])/float(itr)).reshape(edges.shape[0],1)
                eWeight1 = 50*itr*np.exp(-10.0*np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]])/float(itr)).reshape(edges.shape[0],1)
                eWeight2 = 200*np.exp(-10.0*(atlasGT.ravel()[edges[:,0]]+atlasGT.ravel()[edges[:,1]])).reshape(edges.shape[0],1)
#                eWeight2 = 10*(3/(1+atlasGT.ravel()[edges[:,0]]+atlasGT.ravel()[edges[:,1]])).reshape(edges.shape[0],1)
#                eWeight = (10*(np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]])<20)+1*(np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]])>=20)).reshape(edges.shape[0],1)
#                eWeight = np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]]).reshape(edges.shape[0],1)
#                eWeight = np.min(np.vstack([np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]]), 100*np.ones(edges.shape[0])]),axis=0).reshape(edges.shape[0],1)
#                eWeight = np.max(np.vstack([100*np.ones(edges.shape[0])-np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]]), np.zeros(edges.shape[0])]),axis=0).reshape(edges.shape[0],1)
                #eWeight = 10*np.exp(-np.absolute(volGT.ravel()[edges[:,0]]-volGT.ravel()[edges[:,1]])).reshape(edges.shape[0],1)
#                eWeight = 1*(np.exp(-np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]])/20).reshape(edges.shape[0],1))
#                #eWeight = 10*np.ones((edges.shape[0],1))
                edges = np.hstack((edges,eWeight1+eWeight2)).astype(np.int32)
#                edges = np.hstack((edges,eWeight2)).astype(np.int32)
#                edges = np.hstack((edges,eWeight1)).astype(np.int32)
                
                # we flatten the unaries
                result_graph = cut_from_graph(edges, unaries.reshape(-1, 2), pairwise)
                
                seg = result_graph.reshape(vol.shape)

#                func.displayMontageRGB(vol,255*seg)
#                if(-idx<3):
#                    seg = np.multiply(seg,ROICirc)
                
#                segFilled = morph.binary_fill_holes(seg)
                
#                segRefined = skmorph.remove_small_objects(segFilled,min_size=20,connectivity=2)
#                segBP = func.findBPSegment(segRefined,bpMaskInitial)
        
                bp1 = func.findBPSegment(seg,bpMaskInitial)
                bp2 = np.zeros(bpMask1.shape)
                if(np.sum(bpVol[:,:,nearbySlice])>0):
                    bp2 = func.findBPSegment(seg,bpVol[:,:,nearbySlice])
                segBP = np.logical_or(bp1,bp2)
                _,nLabels = measure.label(segBP,background=0,return_num=True,connectivity=1)
                r = 1
                while(nLabels>1):
                    segBP = skmorph.closing(segBP,skmorph.disk(r))
                    _,nLabels = measure.label(segBP,background=0,return_num=True,connectivity=1)
                    r+=1
#                segBP = func.findBPSegment(seg,bpMaskInitial)
                segBP = morph.binary_fill_holes(segBP)
                r = 10
                segBP = skmorph.closing(segBP,skmorph.disk(r))
#                func.displayMontageRGB(vol,255*segBP)
                if(np.sum(bpVol)>0):
#                    func.displayMontageRGB(255*segBP,255*(np.sum(bpVol,axis=2)>0))
                    extraSeg = 1*segBP-1*np.logical_or((np.sum(bpVol,axis=2)>0),endo)
                else:
                    extraSeg = 1*segBP-1*endo
                extraSeg[extraSeg<0] = 0
#                func.displayMontage(extraSeg)
#                func.displayMontageRGB(255*segBP,255*endo)
#
                if(idx<=0 and np.sum(extraSeg)>0.1*np.sum(segBP)):
                    if(itr==1):
                        bp = endoVol>=threshGMM
                        bpMask1 = func.findBPSegment(bp,endo)
                        bpMask2 = np.zeros(bpMask1.shape)
                        if(np.sum(bpVol[:,:,nearbySlice])>0):
                            bpMask2 = func.findBPSegment(bp,bpVol[:,:,nearbySlice])
                        bpMask = np.logical_or(bpMask1,bpMask2)
                
                        _,nLabels = measure.label(bpMask,background=0,return_num=True,connectivity=1)
                        r = 1
                        while(nLabels>1):
                            bpMask = skmorph.closing(bpMask,skmorph.disk(r))
                            _,nLabels = measure.label(bpMask,background=0,return_num=True,connectivity=1)
                            r+=1
                        bpMaskInitial = np.copy(bpMask)
                        segBP = bpMask>0
                    elif(np.sum(bpVol[:,:,nearbySlice])>0):
                        segBP = np.logical_and(segBP,bpVol[:,:,nearbySlice])
                    else:
                        segBP = np.logical_and(segBP,atlasGT>0.5)
                        
#                    itr = 0
#                    continue
#                    segVol = np.multiply(vol,segBP)
#                    threshOtsu = filt.threshold_otsu(vol[segBP>0].ravel())
#                    segBP = endoVol>=thresh
#                    segBP = func.findBPSegment(segBP,endo)
#                    segBP = segBP>0

                segRaw = np.multiply(seg,segBP)
                segRawFilled = morph.binary_fill_holes(segRaw)
#                func.displayMontageRGB(vol,255*segRaw,5)
#                segBG = np.logical_or(segBG,np.logical_xor(seg,segBP))
#                segBP = func.fitEllipse(segBP)
#                func.displayMontageRGB(vol,255*segBP)
#                func.displayMontageRGB(255*segBPOld,255*segBP)

                (_,_,_,_,dice,_) = func.evalMetrics(segBP,segBPOld,np.ones(segBP.shape))
                if(dice<0.5):
                    # RV expanded to LV or outside, stop iteration
                    print("LARGE BP EXPANSION!!!")
                    segBP = np.copy(segBPOld)
                    probBPRefined = np.copy(probBP)
                    probBPRefinedOriginal = np.copy(probBPOriginal)
                    break
                
                bpBinary = probBP>ROIthresh
                endoEdge = segment.find_boundaries(bpBinary.astype(int),connectivity=2,mode='outer',background=0)
                endo = morph.binary_fill_holes(endoEdge)
#                func.displayMontageRGB(vol,255*endoEdge)
                
                distEndo = morph.distance_transform_edt(np.logical_not(endoEdge),sampling=(1,1),return_distances=True,return_indices=False)
                distEndo[endo>0]=-distEndo[endo>0]
    #            func.displayMontage(distEndo)
                moving_Img = sitk.GetImageFromArray(distEndo.swapaxes(0,1))
                moving_Img = sitk.Cast(moving_Img,sitk.sitkFloat32)
                moving_gt = sitk.GetImageFromArray(probBP.swapaxes(0,1))
                moving_gt = sitk.Cast(moving_gt,sitk.sitkFloat32)
                moving_gt2 = sitk.GetImageFromArray(probBPOriginal.swapaxes(0,1))
                moving_gt2 = sitk.Cast(moving_gt2,sitk.sitkFloat32)
            
    #            sitkROI = sitk.GetImageFromArray(ROICirc.swapaxes(0,1))
    #            sitkROI = sitk.Cast(sitkROI,sitk.sitkFloat32)
                
                edgeBP = segment.find_boundaries(segBP.astype(int),connectivity=2,mode='outer',background=0)
    #            distBP = morph.distance_transform_edt(segBP,sampling=(1,1),return_distances=True,return_indices=False)
                distBP = morph.distance_transform_edt(np.logical_not(edgeBP),sampling=(1,1),return_distances=True,return_indices=False)
                distBP[segBP>0]=-distBP[segBP>0]
    #            func.displayMontage(distBP)
                fixed_Img = sitk.GetImageFromArray(distBP.swapaxes(0,1))
                fixed_Img = sitk.Cast(fixed_Img,sitk.sitkFloat32)
                
                fixed_mask = sitk.GetImageFromArray(255*segBP.swapaxes(0,1))
                fixed_mask = sitk.Cast(fixed_mask,sitk.sitkUInt8)
                
                (final_tForm,optimized_tForm,init_tForm) = findOptimumSliceTform(moving_Img,fixed_Img,[],[],verbose=False)
                moving_RS = sitk.Resample(moving_Img, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
                moving_RSgt = sitk.Resample(moving_gt, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
                moving_RSgt2 = sitk.Resample(moving_gt2, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
    #            sitkROI_RS = sitk.Resample(sitkROI, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
                movingS_initial = sitk.Resample(moving_Img, fixed_Img, init_tForm, sitk.sitkLinear, 0.0, fixed_image.GetPixelIDValue())
#                func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(movingS_initial).swapaxes(0,1))
#                func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(moving_Img).swapaxes(0,1))
#                func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(moving_RS).swapaxes(0,1))
#                func.displayMontageRGB(sitk.GetArrayFromImage(moving_gt).swapaxes(0,1),sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1))
#                func.displayMontageRGB(vol,255*(sitk.GetArrayFromImage(moving_gt).swapaxes(0,1)>0.5))
#                func.displayMontageRGB(vol,255*(sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1)>0.5))
                probBPRefined = sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1)
                probBPRefinedOriginal = sitk.GetArrayFromImage(moving_RSgt2).swapaxes(0,1)
    #            refinedROI = sitk.GetArrayFromImage(sitkROI_RS).swapaxes(0,1)
#                func.displayMontageRGB(vol,255*probBPRefined)
#                func.displayMontageRGB(vol,255*probBPRefinedOriginal)
    #            func.displayMontageRGB(vol,refinedROI)
                params = np.copy(newParams)
                newParams = np.asarray(optimized_tForm.GetParameters())
                print(itr,params,newParams)
        #        func.displayMontageRGB(ROI,refinedROI)
        #        func.displayMontage(segBP)
        #        func.displayMontage(255*seg,5)
        #        func.displayMontageRGB(255*gt,255*segBP)
        #        func.displayMontageRGB(vol,255*segBP)
                    # next iteration
                probBP = np.copy(probBPRefined)
                probBPOriginal = np.copy(probBPRefinedOriginal)
                ROI = probBP>0.01
#                ROI = probBPRefined>ROIthresh
#                ROI = probBPRefined>0.01
#                func.displayMontageRGB(vol,probBP)
#                func.displayMontageRGB(vol,255*ROI)
#                ROI = morph.binary_fill_holes(ROI)
#                ROICirc,r = func.getCircularMask(ROI,ROI.shape,1.0)
#                ROIAtl = morph.binary_erosion(ROI,skmorph.disk(0.15*r))
    #            func.displayMontageRGB(vol,ROICirc)
#                bpMask = np.copy(segBP)
                bpMask = np.copy(segRawFilled)
#                func.displayMontageRGB(vol,255*segRawFilled)
#                func.displayMontageRGB(vol,255*segBP)

#            if(-idx<4 and idx<1 and processSlice>5):
#                outArea = 1*segBP-1*bpROI
##                outArea = 1*segBP-1*bpVol[:,:,nearbySlice[idx]]
#                outArea[outArea<0]=0
#                print('outside area = ',np.sum(outArea))
#                if(np.sum(outArea)>0):
#                    print('BASAL/APICAL SLICE!!!')
#                    segBPOld = np.copy(segBP)
##                    segBP = np.logical_and(segBP>0,bpROI>0)
#                    segBP = np.logical_and(segRawFilled>0,bpROI>0)
#                    segBP = func.fitEllipse(segBP)
##                    func.displayMontageRGB(255*segBPOld,255*bpVol[:,:,nearbySlice[idx]])
##                    func.displayMontageRGB(255*segBPOld,255*bpROI)
#                    if(np.sum(movingNewGT[:,:,idx])!=0):
#                        probMyo = movingNewGT[:,:,idx]/movingNewGT[:,:,idx].max()
#                        probMyoOriginal = movingNewGT[:,:,idx]
#                    else:
#                        probMyo = movingNewGT[:,:,nearbySlice]/movingNewGT[:,:,nearbySlice].max()
#                        probMyoOriginal = movingNewGT[:,:,nearbySlice]
#                    myoBinary = probMyo>ROIthresh
#        #            func.displayMontageRGB(vol,255*myoBinary)
#                    endoEdge,_ = func.splitEndoEpi(myoBinary)
#                    endo = morph.binary_fill_holes(endoEdge)
#        #            func.displayMontageRGB(vol,255*endo)
#                    
#        #            distMyo = morph.distance_transform_edt(np.logical_not(myoBinary),sampling=(1,1),return_distances=True,return_indices=False)
#                    distEndo = morph.distance_transform_edt(np.logical_not(endoEdge),sampling=(1,1),return_distances=True,return_indices=False)
#                    distEndo[endo>0]=-distEndo[endo>0]
#        #            func.displayMontage(distEndo)
#                    moving_Img = sitk.GetImageFromArray(distEndo.swapaxes(0,1))
#                    moving_Img = sitk.Cast(moving_Img,sitk.sitkFloat32)
#                    moving_gt = sitk.GetImageFromArray(probMyo.swapaxes(0,1))
#                    moving_gt = sitk.Cast(moving_gt,sitk.sitkFloat32)
#                    moving_gt2 = sitk.GetImageFromArray(probMyoOriginal.swapaxes(0,1))
#                    moving_gt2 = sitk.Cast(moving_gt2,sitk.sitkFloat32)
#                                    
#                    edgeBP = segment.find_boundaries(segBP.astype(int),connectivity=2,mode='outer',background=0)
#        #            distBP = morph.distance_transform_edt(segBP,sampling=(1,1),return_distances=True,return_indices=False)
#                    distBP = morph.distance_transform_edt(np.logical_not(edgeBP),sampling=(1,1),return_distances=True,return_indices=False)
#                    distBP[segBP>0]=-distBP[segBP>0]
#        #            func.displayMontage(distBP)
#                    fixed_Img = sitk.GetImageFromArray(distBP.swapaxes(0,1))
#                    fixed_Img = sitk.Cast(fixed_Img,sitk.sitkFloat32)
#                    
#                    fixed_mask = sitk.GetImageFromArray(255*segBP.swapaxes(0,1))
#                    fixed_mask = sitk.Cast(fixed_mask,sitk.sitkUInt8)
#                    
#                    (final_tForm,optimized_tForm,init_tForm) = findOptimumSliceTform(moving_Img,fixed_Img,[],[],verbose=False)
#                    moving_RS = sitk.Resample(moving_Img, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
#                    moving_RSgt = sitk.Resample(moving_gt, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
#                    moving_RSgt2 = sitk.Resample(moving_gt2, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
#        #            sitkROI_RS = sitk.Resample(sitkROI, fixed_Img, final_tForm, sitk.sitkLinear, 0.0, fixed_Img.GetPixelIDValue())
#                    movingS_initial = sitk.Resample(moving_Img, fixed_Img, init_tForm, sitk.sitkLinear, 0.0, fixed_image.GetPixelIDValue())
#        #            func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(movingS_initial).swapaxes(0,1))
#        #            func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(moving_Img).swapaxes(0,1))
#        #            func.displayMontageRGB(sitk.GetArrayFromImage(fixed_Img).swapaxes(0,1),sitk.GetArrayFromImage(moving_RS).swapaxes(0,1))
#        #            func.displayMontageRGB(sitk.GetArrayFromImage(moving_gt).swapaxes(0,1),sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1))
#        #            func.displayMontageRGB(vol,255*(sitk.GetArrayFromImage(moving_gt).swapaxes(0,1)>0.5))
#        #            func.displayMontageRGB(vol,255*(sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1)>0.5))
#                    probMyoRefined = sitk.GetArrayFromImage(moving_RSgt).swapaxes(0,1)
#                    probMyoRefinedOriginal = sitk.GetArrayFromImage(moving_RSgt2).swapaxes(0,1)
#    #                break
#            bpROI = np.logical_or(bpROI>0,segBP>0)
##            func.displayMontage(bpROI)
#
        except:
            print('WHILE LOOP!')
            continue
#
        try:
            bpProb[:,:,idx] = probBPRefined
            bpProbOriginal[:,:,idx] = probBPRefinedOriginal
#            bpVol[:,:,idx] = fourierSmoothing(segBP,4)
            bpVol[:,:,idx] = segBP
#            bpVolRaw[:,:,idx] = func.fourierSmoothing(segRawFilled,4)
        except:
            print('ASSIGNMENT')
            continue
#        func.displayMontageRGB(fixedImg,255*bpVol,5)
        
    func.displayMontageRGB(fixedImg,255*bpVol,5)
###    func.displayMontageRGB(fixedImg,255*bpVolRaw,5)
    func.displayMontageRGB(255*fixedGT,255*bpVol,5)
#    func.displayMontageRGB(fixedImg,255*bpProb,5)
#    func.displayMontageRGB(fixedImg,255*bpProbOriginal,5)
##    func.displayMontageRGB(fixedImg,255*myoVol,5)
##    func.displayMontageRGB(fixedImg,255*(myoVolOriginal>128),5)
##    func.displayMontageRGB(fixedGT,255*myoVol,5)
##    func.displayMontageRGB(fixedGT,255*bpVolRaw,5)
##    func.displayMontageRGB(fixedImg,fixedGT,5)
#
#
## Find the Region of Interest
#    ROI = np.zeros(fixedImg[:,:,0].shape)
#    for idx in indOrder[0:5]:
#        ROI = ROI+1*(myoVol[:,:,idx]>0.1)
#    ROI = ROI>0
#    ROI = morph.binary_fill_holes(ROI)
##    ROI,_ = func.getCircularMask(ROI,fixedImg[:,:,0].shape,1.2)
##    func.displayMontage(ROI)
#
#    ROIMidSlice = myoVol[:,:,indOrder[0]]>0.01
#    ROIMidSlice = morph.binary_fill_holes(ROIMidSlice)
#    normalizedVol = np.zeros(fixedImg.shape)
#    for idx in indOrder:
#        ROISlice = myoVol[:,:,idx]>0.01
#        ROISlice = morph.binary_fill_holes(ROISlice)
#        if(np.sum(ROISlice)==0):
#            normalizedVol[:,:,idx] = fixedImg[:,:,idx]
#            continue
##        normalizedVol[:,:,idx] = func.normalizeSlices(fixedImg[:,:,idx],0,100,ROI)
#        normalizedVol[:,:,idx] = func.hist_match(fixedImg[:,:,idx],fixedImg[:,:,indOrder[0]],ROISlice,ROIMidSlice)
##    func.displayMontageRGB(fixedImg,normalizedVol,5)
##    func.displayMontage(fixedImg,5)
##    func.displayMontage(normalizedVol,5)
#    myoInt = []
#    bgInt = []
#    bpInt = []
#    for idx in indOrder[0:-5]:
##        vol = func.normalizeSlices(fixedImg[:,:,idx],0,100,ROI)
##        vol = hist_match(fixedImg[:,:,idx],fixedImg[:,:,indOrder[0]],ROISlice,ROIMidSlice)
#        vol = normalizedVol[:,:,idx]
##        func.displayMontage(np.dstack([fixedImg[:,:,idx],vol]))
#        gt = fixedGT[:,:,idx]
#        segBP = bpVol[:,:,idx]
#        bpEdge = segment.find_boundaries(segBP.astype(int),mode='outer')
#        distBP = morph.distance_transform_edt(np.logical_not(bpEdge>0.5),sampling=(1,1),return_distances=True,return_indices=False)
#        distBP[segBP==1]=0
#        distBP[distBP>3]=0
##        myoMask = distBP>0
##        func.displayMontageRGB(vol,255*myoMask)
#        probMyoRefined = myoVol[:,:,idx]
#        refinedROI = probMyoRefined>0.01
##        func.displayMontage(refinedROI)
#        refinedROI = morph.binary_fill_holes(refinedROI)
#        myoMask = probMyoRefined>0.5
##        myoMaskFilled = morph.binary_fill_holes(myoMask)
##        bgMask = np.logical_xor((refinedROI>0.5),myoMaskFilled)
##        bgMask = np.logical_xor(bgMask,segBP>0)
##        bgMask = np.logical_not(myoMaskFilled)
##        myoMaskBig = probMyoRefined>0.5
#        bgMask = np.logical_and(np.logical_not(myoMask),refinedROI)
##        bgMask = np.logical_not(myoMask)
#        indMyo = np.nonzero(myoMask)
#        indBG = np.nonzero(bgMask)
#        indBP = np.nonzero(segBP)
##        func.displayMontageRGB(vol,255*myoMask)
##        func.displayMontageRGB(vol,255*bgMask)
##        func.displayMontageRGB(vol,255*segBP)
#        
#        for i in vol[indBP[0],indBP[1]]: bpInt.append(i)
#        for i in vol[indMyo[0],indMyo[1]]: myoInt.append(i)
#        for i in vol[indBG[0],indBG[1]]: bgInt.append(i)
#
#    gMyo = mixture.GMM(n_components=1)
#    gMyo.fit(np.asarray(myoInt).reshape(-1,1))
##    gMyo.fit(np.asarray(vol[indMyo[0],indMyo[1]]).reshape(-1,1))
##    myoSamples = gMyo.sample(len(vol[indMyo[0],indMyo[1]].ravel()))
##    plt.figure()
##    plt.hist(vol[indMyo[0],indMyo[1]].ravel(),bins=np.arange(255),normed=True)
##    plt.hist(myoSamples,bins=np.arange(255),normed=True)
##    means = gMyo.means_
##    indSort = np.argsort(means.ravel())
##    p,r = gMyo.score_samples(np.arange(0,256).reshape(-1,1))
##    llMyo = np.log(np.multiply(r[:,indSort[1]],np.exp(p))+sys.float_info.epsilon)
#    llMyo = gMyo.score(np.arange(0,256).reshape(-1,1))
#    
#    gBG = mixture.GMM(n_components=3)
#    gBG.fit(np.asarray(bgInt).reshape(-1,1))
##    gBG.fit(np.asarray(vol[indBG[0],indBG[1]]).reshape(-1,1))
##    bgSamples = gBG.sample(len(vol[indBG[0],indBG[1]].ravel()))
##    plt.figure()
##    plt.hist(vol[indBG[0],indBG[1]].ravel(),bins=np.arange(255),normed=True)
##    plt.hist(bgSamples,bins=np.arange(255),normed=True)
##    means = gBG.means_
##    indSort = np.argsort(means.ravel())
##    p,r = gBG.score_samples(np.arange(0,256).reshape(-1,1))
##    llBG = np.log(np.multiply(r[:,indSort[0]],np.exp(p))+sys.float_info.epsilon)
##    llBG = np.log(np.multiply(r[:,indSort[0]],np.exp(p))+np.multiply(r[:,indSort[2]],np.exp(p))+sys.float_info.epsilon)
#    llBG = gBG.score(np.arange(0,256).reshape(-1,1))
#
##    xx = gMyo.score(np.arange(0,256).reshape(-1,1))
##    yy = gBG.score(np.arange(0,256).reshape(-1,1))
##    fig,ax = plt.subplots()
##    ax.plot(xx,'k--',label="Myo loglikelihood")
##    ax.plot(yy,'b',label="BG loglikelihood")
##    legend = ax.legend(loc='upper right')
#
#    midInd = int(np.floor(fixedImg.shape[2]/2))
#    sliceNo = np.arange(bpVol.shape[2])
#    sliceNo[sliceNo>=midInd] = midInd
#
#    ll3D = np.zeros(fixedImg.shape)
#    segVol = np.zeros(fixedImg.shape)
#    myoVolOriginal = myoVolOriginal/myoVolOriginal.max()
#    for idx in indOrder:
#        vol = normalizedVol[:,:,idx]
#        gt = fixedGT[:,:,idx]
#        segBP = bpVol[:,:,idx]
#        probMyoRefined = myoVolOriginal[:,:,idx]
#        refinedROI = probMyoRefined>0.01
#        refinedROI = morph.binary_fill_holes(refinedROI)
#        myoMask = probMyoRefined>0.5
#        myoMaskFilled = morph.binary_fill_holes(myoMask)
#        bgMask = np.logical_xor((refinedROI>0.5),myoMaskFilled)
###        bgMask = np.logical_xor(bgMask,segBP>0.5)
###        func.displayMontageRGB(vol,segBP)
###        func.displayMontageRGB(vol,255*myoMask)
###        func.displayMontageRGB(vol,255*bgMask)
###        func.displayMontageRGB(segBP,255*myoMask)
###        func.displayMontage(np.multiply(vol,refinedROI))
##        
#        # create unaries based on intensity likelihood
#        unariesLLMyo = llMyo[vol.astype(int)]
#        unariesLLBG = llBG[vol.astype(int)]
##        func.displayMontage(unariesLLS-unariesLLT,5)
##        func.displayMontage(unariesLLMyo,5)
##        func.displayMontage(unariesLLBG,5)
#        
#        atlasMyo = np.copy(probMyoRefined)
##        func.displayMontage(255*atlasMyo,5)
#        atlasNonMyo = 1-atlasMyo
##        func.displayMontage(atlasNonMyo)
#
#    #    # create unaries based on atlas shape
#        unariesAtlMyo = np.log(atlasMyo+sys.float_info.epsilon)
#        unariesAtlNonMyo = np.log(atlasNonMyo+sys.float_info.epsilon)
##        func.displayMontage(unariesAtlMyo,5)
##        func.displayMontage(unariesAtlBG,5)
#    #    func.displayMontage(unariesAtlS-unariesAtlT,5)
#    #    
#        bpEdge = segment.find_boundaries(segBP.astype(int),mode='outer')
#        distBP = morph.distance_transform_edt(np.logical_not(bpEdge>0.5),sampling=(1,1),return_distances=True,return_indices=False)
#        distBP[distBP>10] = 10
#        
##        ROIthresh = max(0.8-float(sliceNo[idx])/10,0.5)
#
#        LLIntensity = unariesLLMyo-unariesLLBG
#        LLAtls = unariesAtlMyo-unariesAtlNonMyo
##        LLAtls = atlasMyo-0.5
#        LLDist = 10-2*distBP
##        LLDist = -np.log(distBP/10+sys.float_info.epsilon)
#        LLDist[segBP==1]=-10
##        LLDist = np.log(10-distBP+sys.float_info.epsilon)
##        func.displayMontage(LLIntensity)
##        func.displayMontage(LLAtls)
##        func.displayMontage(LLDist)
#        ll = 10*LLIntensity+10*LLAtls+5*LLDist
##        func.displayMontage(ll)
#        ll3D[:,:,idx] = ll
#        if(idx==0 and isMyoApex==True):
#            ll = -1000*np.ones(vol.shape)
#            ll[myoApex>0]=1000
#            ll3D[:,:,idx] = ll
##            myoApex = np.copy(segBP)
##            isMyoApex = True
#
###        func.displayMontage(ll)
##                    
##        # as we convert to int, we need to multipy to get sensible values
#        unaries = np.stack([ll,-ll],axis=-1).copy("C").astype(np.int32)
#        # create potts pairwise
#        pairwise = -1*np.eye(2, dtype=np.int32)
#        # use the gerneral graph algorithm
#        # first, we construct the grid graph
#        inds = np.arange(vol.size).reshape(vol.shape)
#        horz = np.c_[inds[:,:-1].ravel(), inds[:,1:].ravel()]   # horizontal edges
#        vert = np.c_[inds[:-1,:].ravel(), inds[1:,:].ravel()]   # vertical edges
#    #    depth = np.c_[inds[:,:,:-1].ravel(), inds[:,:,1:].ravel()]  # slice edges
#        edges = np.vstack([horz, vert]).astype(np.int32)
##        eWeight = 10-np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]]).reshape(edges.shape[0],1)
##        eWeight[eWeight<0] = 0
#        eWeight = np.exp(-30*np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]])).reshape(edges.shape[0],1)
#        #eWeight = 10*np.exp(-np.absolute(volGT.ravel()[edges[:,0]]-volGT.ravel()[edges[:,1]])).reshape(edges.shape[0],1)
#        #eWeight = 10*np.ones((edges.shape[0],1))
#        edges = np.hstack((edges,eWeight)).astype(np.int32)
#        
#        # we flatten the unaries
##            result_graph = cut_from_graph(edges, unaries.reshape(-1, 3), pairwise)
#        result_graph = cut_from_graph(edges, unaries.reshape(-1, 2), pairwise)
#        
#        seg = result_graph.reshape(vol.shape)
##        func.displayMontage(seg)
##        func.displayMontageRGB(vol,255*seg)
##        func.displayMontageRGB(255*fixedGT[:,:,idx],255*seg)
#        
#        segVol[:,:,idx] = seg
##    
###        func.displayMontageRGB(fixedGT[:,:,idx],255*seg,5)    
##    execTime[ind] = time.time()-startTime
##    dice,jaccard,sensitivity,specificity,PPV,NPV = func.evaluateMetrics(fixedGT,segVol,option='intersection')
##    wDice.writerow(dice)
##    wJaccard.writerow(jaccard)
##    wSensitivity.writerow(sensitivity)
##    wSpecificity.writerow(specificity)
##    wPPV.writerow(PPV)
##    wNPV.writerow(NPV)
##timeFile = open('time.csv','wb')
##wTime = csv.writer(timeFile,delimiter=',',quoting=csv.QUOTE_NONE)
##wTime.writerow(execTime)
##timeFile.close()
##    
##diceFile.close()
##jaccardFile.close()
##sensitivityFile.close()
##specificityFile.close()
##PPVFile.close()
##NPVFile.close()
##
##    print(results)
##    vol = normalizedVol
##    unaries = np.stack([ll3D,-ll3D],axis=-1).copy("C").astype(np.int32)
##    # create potts pairwise
##    pairwise = -1*np.eye(2, dtype=np.int32)
###            pairwise = -1*np.eye(3, dtype=np.int32)
###            pairwise = pairwise-1*np.ones(pairwise.shape)
###            pairwise[0,2] = 0
###            pairwise[2,0] = 0
###            pairwise = pairwise.astype('int32')
##    # use the gerneral graph algorithm
##    # first, we construct the grid graph
##    inds = np.arange(vol.size).reshape(vol.shape)
##    horz = np.c_[inds[:,:-1,:].ravel(), inds[:,1:,:].ravel()]   # horizontal edges
##    vert = np.c_[inds[:-1,:,:].ravel(), inds[1:,:,:].ravel()]   # vertical edges
##    depth = np.c_[inds[:,:,:-1].ravel(), inds[:,:,1:].ravel()]  # slice edges
##    edges = np.vstack([horz, vert, depth]).astype(np.int32)
###    eWeight = 5-np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]]).reshape(edges.shape[0],1)
###    eWeight[eWeight<0]=0
###    eWeight = 10*eWeight
###    eWeight[eWeight>20]=20
###        eWeight[eWeight<0] = 0
##    eWeight = 100*np.exp(-30*np.absolute(vol.ravel()[edges[:,0]]-vol.ravel()[edges[:,1]])).reshape(edges.shape[0],1)
###    eWeight = 100*np.exp(-np.absolute(ll3D.ravel()[edges[:,0]]-ll3D.ravel()[edges[:,1]])).reshape(edges.shape[0],1)
###    #eWeight = 10*np.exp(-np.absolute(volGT.ravel()[edges[:,0]]-volGT.ravel()[edges[:,1]])).reshape(edges.shape[0],1)
###    #eWeight = 10*np.ones((edges.shape[0],1))
##    edges = np.hstack((edges,eWeight)).astype(np.int32)
##    
##    # we flatten the unaries
###            result_graph = cut_from_graph(edges, unaries.reshape(-1, 3), pairwise)
##    result_graph = cut_from_graph(edges, unaries.reshape(-1, 2), pairwise)
##    
##    segVol = result_graph.reshape(vol.shape)
#
#    func.displayMontage(fixedImg,5)
#    func.displayMontage(255*segVol,5)
#    func.displayMontageRGB(fixedImg,128*segVol,5)
#    func.displayMontageRGB(fixedGT,128*segVol,5)
#    func.displayMontageRGB(fixedImg,fixedGT,5)
