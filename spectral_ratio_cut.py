import dill
import sys
import os
import math
import heapq
import numpy as np
from scipy import io
import matlab.engine

W = []
D = []
L = []
Dtilde = []
subscriberIDs = {}

def dot_product(subreddits1, subreddits2):
	s = 0.0
	for sr in subreddits1:
		if sr in subreddits2:
			s += (subreddits1[sr]*subreddits2[sr])
	return s

def euclidean_dist(cluster, data):
	s = 0.0
	for i in xrange(len(cluster)):
		s += (cluster[i]*data[i])**2
	return math.sqrt(s)

def init():
	# f = open('normalized_combined_comment_counts.txt', 'r')
	# di = dill.load(f)
	# allsubscribers = sorted(di.keys())
	# diagonal = []
	# weights = []
	# print len(di)
	# for i in xrange(len(allsubscribers)):
	# 	print i
	# 	w = [0]*len(allsubscribers)
	# 	d = 0
	# 	subscriberIDs[i] = allsubscribers[i]
	# 	for j in xrange(len(allsubscribers)):
	# 		if i > j:
	# 			w[j] = weights[j][i]
	# 		if i != j:
	# 			subreddits1 = di[allsubscribers[i]]
	# 			subreddits2 = di[allsubscribers[j]]
	# 			if len(subreddits1) != 0 and len(subreddits2) != 0:
	# 				w[j] = dot_product(subreddits1, subreddits2)
	# 				if w[j] != 0:
	# 					d += 1
	# 			else:
	# 				w[j] = 0 
	# 	weights.append(w)
	# 	diagonal.append(d)
	global D
	global W
	f2 = open('weights.txt', 'r')
	W = dill.load(f2)
	f2.close()
	f3 = open('diagonal.txt', 'r')
	D = dill.load(f3)
	f3.close()

	# global L
	# global Dtilde
	# D = np.diag(diagonal)
	# Dtilde = np.diag(diagonal)
	# W = np.matrix(weights)
	# L = D - W
	# for i in xrange(len(diagonal)):
	# 	for j in xrange(len(diagonal)):
	# 		Dtilde[i][j] = diagonal[i]*diagonal[j]	
	# print Dtilde		

def runSpectralRatioCut():
	# e_val, e_vec = linalg.eig(L)
	print "matlab"
	eng = matlab.engine.start_matlab()
	eng.workspace['W'] = W
	eng.workspace['D'] = D
	[e_val, e_vec] = eng.eval('calc_eig(D, W)')

	print e_vec
	f1 = open('e_val_ratio_cut.txt', 'w')
	f2 = open('e_vec_ratio_cut.txt', 'w')
	dill.dump(e_val, f1)
	dill.dump(e_vec, f2)
	#find k smallest eigenvectors 
	smallestEVals = {}
	for i in xrange(1, len(e_val)):
		if e_val[i] not in smallestEVals:
			clusters[e_vec[:, i]] = []
			smallestEVals[e_val[i]] = 1

	print clusters 
	#perform k-means 
	while True:
		newClusters = {}
		for i in xrange(len(e_val)):
			dis = sys.maxint
			for j in clusters:
				if j not in newClusters:
					newClusters[j] = []
				edis = euclidean_dist(clusters[j], e_vec[:, i])
				if dis > edis:
					dis = edis
					newClusters[j].append(i)
		toPop = []
		for k in newClusters:
			total = [0]*len(newClusters[k])
			for l in newClusters[k]:
				total += e_vec[:, newClusters[k][l]]
			total /= len(newClusters[k])
			print total
			newClusters[total] = newClusters[k]
			toPop.append(k)
		for i in toPop:
			newClusters.pop(i)
		if newClusters == clusters:
			break
		else:
			clusters = copy.copy(newClusters)

	for i in xrange(len(clusters)):
		print "CLUSTER "+ i
		for j in xrange(len(clusters[i])):
			print subscriberIDs[j]

def runMaxMod():
	e_val, e_vec = LA.eig(Dtilde - W)

	#find k smallest eigenvectors 
	for i in xrange(len(e_val)):
		heapq.heappush(heap, (e_val[i], i))
	heapq._heapify_max(heap)
	clusters = {}
	for i in range(k):
		(val, ID) = heapq.heappop(heap)
		clusters[e_vec[:, ID]] = []
		heapq._heapify_max(heap)

	#perform k-means 
	while True:
		newClusters = {}
		for i in xrange(len(e_val)):
			dis = sys.maxint
			for j in clusters:
				if j not in newClusters:
					newClusters[j] = []
				edis = euclidean_dist(clusters[j], e_vec[:, i])
				if dis > edis:
					dis = edis
					newClusters[j].append(i)
		if newClusters == clusters:
			break
		else:
			clusters = copy.copy(newClusters)

	for i in xrange(len(clusters)):
		print "CLUSTER "+ i
		for j in xrange(len(clusters[i])):
			print subscriberIDs[j]

def main():
	init()

	runSpectralRatioCut()

if __name__ == "__main__":
	main()