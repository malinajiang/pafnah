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

    for k, v in degrees.items():
        if indices[k] in requesters:
            features = {}
            features['degree'] = v
            features['betweenness'] = between[k]
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
    feature_vector['between'] = request['degree']
    

    # request received pizza 
    success = 1 if indices[ID] in success else -1

    return feature_vector, success


def learn_predictor(evaluate):
    train_data, dev_data, successful, indices = read_dataset()
    weights = collections.defaultdict(lambda: 0)  # feature => weight
    num_iters = 500

    for t in range(num_iters):
        eta = .0000001 # .0000001
        for ID, features in train_data.items():
            feature_vector, success = extract_features(ID, features, successful, indices)
            dotProd = (dot_product(feature_vector, weights))*success
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
            if abs(success - score) <= 0.5: correct += 1
            r = random.randint(0,1)
            if r == 1 and success == 1:
                rando += 1
            elif r == 0 and success == -1:
                rando += 1

        print 'correct: ' + str(correct)
        print 'random: ' + str(float(rando)/len(dev_data))
        print 'percentage: ' + str(float(correct)/len(dev_data))
    
    print weights
    return weights


def main(argv):
    learn_predictor(True)

if __name__ == "__main__":
    main(sys.argv[1:])
