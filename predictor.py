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
import codecs
import json
from util import *
from collections import Counter

def read_dataset(path):
  with codecs.open(path, 'r', 'utf-8') as myFile:
    content = myFile.read()
  dataset = json.loads(content)
  train = []
  dev = []
  for i in xrange(len(dataset)):
    if dataset[i]['in_test_set']:
        train.append(dataset[i])
    else:
        dev.append(dataset[i])
  return (train, dev)

def extract_features(request):
    """
    Extract features for a face corresponding to the face_id and with
    attributes in the dict face_attrs.
    """
    feature_vector = collections.defaultdict(lambda: 0)

    # Karma -> need API

    # Existence in top 10 subreddits
    feature_vector['AskReddit'] = 1 if 'AskReddit' in request['requester_subreddits_at_request'] else 0
    
    feature_vector['promos'] = 1 if 'promos' in request['requester_subreddits_at_request'] else 0

    feature_vector['Loans'] = 1 if 'Loans' in request['requester_subreddits_at_request'] else 0

    feature_vector['RandomActsOfCookies'] = 1 if 'RandomActsOfCookies' in request['requester_subreddits_at_request'] else 0

    feature_vector['sharedota2'] = 1 if 'sharedota2' in request['requester_subreddits_at_request'] else 0

    feature_vector['Random_Acts_Of_Pizza'] = 1 if 'Random_Acts_Of_Pizza' in request['requester_subreddits_at_request'] else 0

    feature_vector['reportthespammers'] = 1 if 'reportthespammers' in request['requester_subreddits_at_request'] else 0

    feature_vector['codbo'] = 1 if 'codbo' in request['requester_subreddits_at_request'] else 0

    feature_vector['sc2partners'] = 1 if 'sc2partners' in request['requester_subreddits_at_request'] else 0

    feature_vector['Assistance'] = 1 if 'Assistance' in request['requester_subreddits_at_request'] else 0

    feature_vector['t:heatdeathoftheuniverse'] = 1 if 't:heatdeathoftheuniverse' in request['requester_subreddits_at_request'] else 0
    
    # Length of the textpost
    text = request['request_text'].split()
    feature_vector['length_textpost'] = len(text)

    # user similarity with giver -> need API

    # Number of comments on post
    feature_vector['num_comments'] = request['request_number_of_comments_at_retrieval']
    # Post upvotes - downvotes
    feature_vector['textpost_upvotes_minus_downvotes'] = request['number_of_upvotes_of_request_at_retrieval'] - request['number_of_downvotes_of_request_at_retrieval']

    # requester_upvotes_minus_downvotes_at_request
    feature_vector['requester_upvotes_minus_downvotes'] = request['requester_number_of_posts_on_raop_at_request']

    # request received pizza 
    success = 1 if request['requester_received_pizza'] else -1

    return feature_vector, success


def learn_predictor(evaluate):
    train_data, dev_data = read_dataset('./pizza_request_dataset/pizza_request_dataset.json')
    weights = collections.defaultdict(lambda: 0)  # feature => weight
    num_iters = 500

    for t in range(num_iters):
        eta = .06 # .00001
        for request in train_data:
            feature_vector, success = extract_features(request)
            dotProd = (dot_product(feature_vector, weights))*success
        if dotProd < 1:
            increment(weights, eta * success, feature_vector)

        # train_correct = evaluate_predictor(train_data, extract_features, weights)
        # dev_correct = evaluate_predictor(dev_data, extract_features, weights)
        # print "Official: train = %s, dev = %s" % (train_correct, dev_correct)

    if evaluate:

        correct = 0
        for request in dev_data:
            feature_vector, success = extract_features(request)
            score = dot_product(weights, feature_vector)
            if abs(success - score) <= 0.5: correct += 1
        print 'correct: ' + str(correct)
        print 'percentage: ' + str(float(correct)/len(dev_data))
    
    print weights
    return weights


def main(argv):
    learn_predictor(True)

if __name__ == "__main__":
    main(sys.argv[1:])
