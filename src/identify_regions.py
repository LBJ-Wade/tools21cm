from skimage.filters import threshold_otsu
from scipy.signal import argrelextrema
import c2raytools as c2t
import matplotlib.pyplot as plt
import superpixels

def bubbles_from_slic(data, n_segments=5000, bins=50):
	"""
	Parameters
	----------
	data      : The brightness temperature cube.
	n_segments: No. of superpixels (Default: 2000).
	bins      : No. of bins for the PDF used for stitching (Default: 50).
	Return
	----------
	Binary cube where regions pixels are the True values.
	"""
	labels  = superpixels.slic_cube(data, n_segments=n_segments)
	bin_sl  = superpixels.stitch_maximumdeviation(data, labels, bins=bins, binary=True)
	return bin_sl

def bubbles_from_kmeans(data, upper_lim=True, n_jobs=1, n_clusters=3):
	"""
	Parameters
	----------
	data      : The brightness temperature/xfrac cube.
	upper_lim : This decides which mode in the PDF is to be identified.
                    'True' identifies ionized regions in brightness temperature, while
		    'False' identifies in the xfrac data (Default: True).
	n_jobs    : No. of cores to use (Default: 1).
	n_cluster : No. of clusters found in the PDF (Default: 3).
	Return
	----------
	Binary cube where regions pixels are the True values.
	"""
	if n_clusters==2: array, t_th = threshold_kmeans(data, upper_lim=upper_lim, n_jobs=n_jobs)
	else: array = threshold_kmeans_3cluster(cube, upper_lim=upper_lim, n_jobs=n_jobs)
	return array

def bubbles_from_fixed_threshold(data, threshold=0, upper_lim=True):
	"""
	Parameters
	----------
	data      : The brightness temperature/xfrac cube.
	threshold : The fixed threshold value (Default: 0). 
	upper_lim : This decides which mode in the PDF is to be identified.
                    'True' identifies ionized regions in brightness temperature, while
		    'False' identifies in the xfrac data (Default: True).
	Return
	----------
	Binary cube where regions pixels are the True values.
	"""
	if upper_lim: return (data<=threshold)
	else: return  (data>=threshold)

def threshold_kmeans(cube, upper_lim=False, mean_remove=True, n_jobs=1):
	"""
	The input is the brightness temperature cube.
	"""
	array = np.zeros(cube.shape)
	#km = KMeans(n_clusters=2)
	if mean_remove:
		if upper_lim: X = cube[cube<=cube.mean()].reshape(-1,1)
		else: X = cube[cube>=cube.mean()].reshape(-1,1)
	else:
	 	X  = cube.reshape(-1,1)
	y = KMeans(n_clusters=2, n_jobs=n_jobs).fit_predict(X)
	if X[y==1].mean()>X[y==0].mean(): t_th = X[y==0].max()
	else: t_th = X[y==1].max()
	if upper_lim: array[cube<=t_th] = 1
	else: array[cube>t_th] = 1
	print "The output contains a tuple with binary-cube and determined-threshold."
	return array, t_th
	
def threshold_kmeans_3cluster(cube, upper_lim=False, n_jobs=1):
	"""
	The input is the brightness temperature cube.
	"""
	km = KMeans(n_clusters=3, n_jobs=n_jobs)
	X  = cube.reshape(-1,1)
	array = np.zeros(X.shape)
	km.fit(X)
	y = km.labels_
	centers = km.cluster_centers_
	if upper_lim: true_label = centers.argmin()
	else: true_label = centers.argmax()
	array[y==true_label] = 1
	array = array.reshape(cube.shape)
	return array
