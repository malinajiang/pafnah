# File: algorithm.py
# --------------------
# Extracts features for each face from the face_dict.txt file, then
# runs stochastic gradient descent to train the predictor.

import copy
import random
import collections
import math
import sys
import ast
import json
import dill
from util import *
from collections import Counter
#(31, 2), (53, 2), (77, 2), (75, 5), (29, 6), (42, 6), (47, 6), (65, 6), (72, 6), (83, 6), (101, 6), (105, 6), (3, 7), (20, 7), 
#(36, 7), (37, 7), (66, 7), (70, 7), (85, 7), (102, 7), (15, 8), (19, 8), (27, 8), (43, 8), (54, 8), (58, 8), (61, 8), (71, 8), 
#(74, 8), (78, 8), (93, 9), (30, 10), (62, 10), (86, 10), (100, 10), (108, 10), (23, 11), (81, 11), (104, 11), (21, 12), (33, 12), 
#(48, 12), (79, 12), (88, 12), (90, 12), (68, 14), (94, 14), (97, 14), (82, 15), (96, 15), (40, 17), (45, 17), (63, 17), (99, 18), 
#(52, 19), (57, 19), (44, 21), (64, 21), (73, 21), (76, 21), (87, 22), (92, 26), (67, 29), (84, 32), (6, 35), (56, 36), (55, 40), 
#(107, 42), (1, 49), (106, 68), (103, 72), (0, 74), (26, 78), (109, 78), (89, 79), (91, 129), (2, 176), (9, 278), (5, 336), (69, 1601)
usedlabels = []
numclusters = 50
def read_dataset():
    train = {}
    dev = {}

    f = open('degrees_filtered.txt', 'r')
    degrees = dill.load(f)
    f.close()

    f2 = open('betweenness_centrality_filtered.txt', 'r')
    between = dill.load(f2)
    f2.close()

    f3 = open('successful_requests.txt', 'r')
    successful = dill.load(f3)
    f3.close()

    f4 = open('pizza_requesters.txt', 'r')
    requesters = dill.load(f4)
    f4.close()

    f5 = open('./data/indices.txt','r')
    indices = dill.load(f5)
    f5.close()
    
    f6 = open('shortest_paths.txt', 'r')
    shorts = dill.load(f6)
    f6.close()

    f7 = open('./data/120_labels.txt', 'r')
    labels = dill.load(f7)
    f7.close()

    f8 = open('./data/goodlabels_120.txt', 'r')
    goodlabels = dill.load(f8)
    f8.close()

    global numclusters
    numclusters = len(goodlabels)

    for k, v in degrees.items():
        if indices[k] in requesters:
            features = {}
            features['degree'] = v
            # features['between'] = between[k]
            features['short'] = shorts[indices[k]]
            for i in range(len(goodlabels)):
                if len(usedlabels) != numclusters:
                    usedlabels.append(goodlabels[i])
                if labels[k] == goodlabels[i]:
                    features['cluster_'+str(goodlabels[i])] = 1
                else:
                    features['cluster_'+str(goodlabels[i])] = 0
            train[k] = features
            dev[k] = features
    return (train, dev, successful, indices)

def extract_features(ID, request, success, indices):
    """
    Extract features for a face corresponding to the face_id and with
    attributes in the dict face_attrs.
    """
    feature_vector = collections.defaultdict(lambda: 0)

    # Existence in top 10 subreddits
    feature_vector['degree'] = request['degree']
    # feature_vector['between'] = request['between']
    feature_vector['short'] = request['short']
    for i in range(len(usedlabels)):
        feature_vector['cluster_'+str(usedlabels[i])] = request['cluster_'+str(usedlabels[i])]

    # request received pizza 
    success = 1 if indices[ID] in success else -1

    return feature_vector, success


def learn_predictor(evaluate):
    train_data, dev_data, successful, indices = read_dataset()
    weights = collections.defaultdict(lambda: 0)  # feature => weight
    num_iters = 500

    for t in range(num_iters):
        eta = .01 # .0000001
        for ID, features in train_data.items():
            feature_vector, success = extract_features(ID, features, successful, indices)
            dotProd = (dot_product(feature_vector, weights)) * success
            if dotProd < 1:
                increment(weights, eta * success, feature_vector)

        # train_correct = evaluate_predictor(train_data, extract_features, weights)
        # dev_correct = evaluate_predictor(dev_data, extract_features, weights)
        # print "Official: train = %s, dev = %s" % (train_correct, dev_correct)

    if evaluate:
        rando = 0
        correct = 0
        for ID, features in dev_data.items():
            feature_vector, success = extract_features(ID, features, successful, indices)
            score = dot_product(weights, feature_vector)
            if abs(success - score) <= 0.5: 
                correct += 1
           
            r = random.randint(0,1)
            if r == 1 and success == 1:
                rando += 1
            elif r == 0 and success == -1:
                rando += 1

        print 'eta: '+ str(eta)
        print 'random: ' + str(float(rando)/len(dev_data))
        print 'percentage: ' + str(float(correct)/len(dev_data))
    
    return weights


def main():
    learn_predictor(True)

if __name__ == "__main__":
    main()
