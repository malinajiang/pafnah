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

    subscriber_ids = {}
    f5 = open('./data/indices.txt', 'r')
    all_subscribers = dill.load(f5)
    for i in xrange(len(all_subscribers)):
        subscriber_ids[all_subscribers[i]] = i
    f5.close()

    f6 = open('shortest_paths.txt', 'r')
    shorts = dill.load(f6)
    f6.close()

    f7 = open('coarsening_data_new/110_labels.txt')
    coarsening_labels = dill.load(f7)
    f7.close()

    clusters_counts = dict([x, coarsening_labels.count(x)] for x in coarsening_labels)
    top_clusters = sorted(clusters_counts, key = lambda x: clusters_counts[x], reverse = True)[:5]
    large_clusters = [x for x in clusters_counts if clusters_counts[x] > 1]

    for requester in requesters:
        if requester not in subscriber_ids or subscriber_ids[requester] not in degrees:
            continue

        index = subscriber_ids[requester]
        features = {}
        features['degree'] = degrees[index]
        # features['between'] = between[index]
        features['short'] = shorts[requester]

        for i in xrange(110):
            # if i not in large_clusters:
            #     continue

            if coarsening_labels[index] == i:
                features['cluster_' + str(i)] = 1
            else:
                features['cluster_' + str(i)] = 0

        train[requester] = features
        dev[requester] = features

    return (train, dev, successful, subscriber_ids)

def learn_predictor(train, dev, successful, subscriber_ids, evaluate):
    weights = collections.defaultdict(lambda: 0)  # feature => weight
    num_iters = 500

    for t in range(num_iters):
        eta = 0.001
        
        for requester, features in train.items():
            success = 1 if requester in successful else -1
            margin = (dot_product(weights, features)) * success
            if margin < 1:
                increment(weights, eta * success, features)

    if evaluate:
        correct = 0
        for requester, features in dev.items():
            success = 1 if requester in successful else -1
            score = dot_product(weights, features)
            
            if abs(success - score) <= 0.5: 
                correct += 1

    return (weights, correct)

def random_predictor(train, dev, successful, subscriber_ids, evaluate):
    # no training phase

    if evaluate:
        correct = 0
        for requester in dev:
            success = 1 if requester in successful else -1

            score = random.randint(0, 1)
            if score == 1 and success == 1:
                correct += 1
            elif score == 0 and success == -1:
                correct += 1

    return correct

def main():
    train, dev, successful, subscriber_ids = read_dataset()
    weights, learn_correct = learn_predictor(train, dev, successful, subscriber_ids, True)
    rand_correct = random_predictor(train, dev, successful, subscriber_ids, True)

    print learn_correct / float(len(dev))
    print rand_correct / float(len(dev))

    # random
    # 0.4711

    # degree
    # 0.01, 0.5763

    # betweenness
    # 0.000000001, 0.2875

    # shortest path
    # 0.01, 0.8871

    # clusters
    # 0.01, 0.8954

    # top 5 clusters
    # 0.01, 0.6637

    # degree, shortest path
    # 0.0001, 0.8860

    # degree, betweenness, shortest path
    # 0.0000001, 0.3935

    # degree, shortest path, clusters
    # 0.001, 0.8898

    # degree, shortest path, top 5 clusters
    # 0.001, 0.8871

    # degree, shortest path, large clusters
    # 0.01, 0.8135
    # 0.01, 0.8910

if __name__ == "__main__":
    main()
