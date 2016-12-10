import dill
import sys
import os
import math
import heapq
import numpy as np
from scipy import io, sparse
import matlab.engine
from scipy.sparse import linalg
from sklearn.cluster import KMeans
from collections import Counter

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
		s += (cluster[i]-data[i])**2
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

def calcWeightsAndDegrees(counts):
	users = sorted(counts.keys())
	weights = []
	degrees = []
	for i, u1 in enumerate(users):
		w = [0]*len(users)
		for j, u2 in enumerate(users):
			if i > j:
				w[j] = weights[j][i]
			elif i < j:
				w[j] = dot_product(counts[u1], counts[u2])
		weights.append(w)
		degrees.append(sum(w))
	return users, weights, degrees

def calcTopWeightsAndDegrees(weights):
	edges = set()
	degrees = [0]*len(weights)
	neighbors = [{} for i in range(len(weights))]
	for u, uw in enumerate(weights):
		suw = [(uw[i], i) for i in range(len(uw))]
		top = heapq.nlargest(5, suw)
		d = 0
		for e in top:
			if e[0] > 0:
				edges.add((u, e[1]))
				edges.add((e[1], u))
				neighbors[u][e[1]] = weights[u][e[1]]
				neighbors[e[1]][u] = weights[e[1]][u]
	I = []
	J = []
	V = []
	for e in edges:
		I.append(e[0])
		J.append(e[1])
		V.append(weights[e[0]][e[1]])
	for e in edges:
		degrees[e[0]] += weights[e[0]][e[1]]
	return (degrees,I,J,V, neighbors)

#weights should be the full matrix, not just top 5
def runSRC(weights, dirname):
	d, I, J, V = calcTopWeightsAndDegrees(weights)
	print "Calculated top weights and degrees"
	dump(d, dirname + '/top_degrees.txt')
	size = len(d)
	W = sparse.coo_matrix((V, (I, J)), shape=(size, size))
	D = sparse.coo_matrix((d, (range(size), range(size))), shape=(size, size))
	L = D - W
	print "Calculated W, D, L"
	io.mmwrite(dirname + '/top_weights_sparse.txt', W)
	io.mmwrite(dirname + '/top_degrees_sparse.txt', D)
	io.mmwrite(dirname + '/top_lagrangian_sparse.txt', L)
	vals, vecs = linalg.eigsh(L, k=size-1)
	print "Calculated eigenvals/vecs"
	# okay do I want to confirm that vals is sorted in increasing order or just assume
	npsave(vals, dirname + '/top_vals.txt')
	npsave(vecs, dirname + '/top_vecs.txt')
	#nclusters = [2,3,4,5,6,7,8,9,10,11,13,16,20,25,31,38,46,55,65,76,88,101,115,130,146,163,181,200,220,241,263,286,310,335,361,388,416,445,475,506,538,571,605,640,676,713,751,790,830,871,913,956,1000]
	nclusters = [2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,325,350,375,400,425,450,475,500,550,600,650,700,800,900,1000]
	counters = []
	kmeans = []
	for n in nclusters:
		kmean = KMeans(n_clusters=n, random_state=0).fit(vecs[:,0:n])
		kmeans.append(kmean)
		label = kmean.labels_.tolist()
		c = Counter(label)
		counters.append(c)
		topclusters = sorted([c[k] for k in c if c[k] > 16], reverse=True)
		print n, "clusters:", topclusters
	dump(counters, dirname + '/top_km_counters.txt')
	dump(kmeans, dirname + '/top_km.txt')
	return (d,I,J,V,W,D,L,vals,vecs,counters,kmeans)

def dump(data, fname):
	f = open(fname, 'w')
	dill.dump(data, f)
	f.close()

def load(fname):
	f = open(fname, 'r')
	data = dill.load(f)
	f.close()
	return data

def npsave(data, fname):
	f = open(fname, 'w')
	np.save(f, data)
	f.close()

def npload(fname):
	f = open(fname, 'r')
	data = np.load(f)
	f.close()
	return data

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