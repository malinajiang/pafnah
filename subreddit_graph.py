import codecs
import json
import math
import pickle
import dill

import numpy as np

import collections

def read_dataset(path):
  with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()
  dataset = json.loads(content)
  return dataset

def subreddit_subscribers():
  subscribers_file = open('subreddit_subscribers.txt', 'r')
  subscribers = pickle.load(subscribers_file)
  subscribers_file.close()

  return subscribers

def get_givers_comments():
  givers_comments_file = open('givers_comment_counts.txt', 'r')
  givers_comments = dill.load(givers_comments_file)
  givers_comments_file.close()

  return givers_comments

def get_subreddit_comments():
  subreddit_comments_file = open('subreddit_comments.txt')
  subreddit_comments = dill.load(subreddit_comments_file)
  subreddit_comments_file.close()

  return subreddit_comments

def read_subreddits(dataset):
  d = {}
  for request in dataset:
    for subreddit in request['requester_subreddits_at_request']:
      if subreddit in d:
        users_list = d[subreddit]
        users_list[request['requester_username']] = 1
        d[subreddit] = users_list
      else:
        d[subreddit] = {}
        d[subreddit][request['requester_username']] = 1
  return d

def subreddits_only_graph(subreddit_to_subscribers, subscribers):
  subscribers_graph = open('subreddit_only_graph.json', 'w')
  data = {}
  data['nodes'] = []
  data['links'] = []
  subreddit_pairs = {}
  nonempty = 0
  for i in subreddit_to_subscribers:
    for j in subreddit_to_subscribers:
      if i != j and (j, i) not in subreddit_pairs:
        subreddit_pairs[(i, j)] = []
        s = set(subreddit_to_subscribers[i])
        t = set(subreddit_to_subscribers[j])
        subreddit_pairs[(i, j)] = s.union(t)

  used_subscribers = {}
  for k,v in subreddit_pairs.items():
    link = {}
    link['source'] = k[0]
    link['target'] = k[1]
    if '/r/'+k[0] in subscribers and '/r/'+k[1] in subscribers:
      val = float(len(v))/(len(subscribers['/r/'+k[0]])+len(subscribers['/r/'+k[1]]))
      if val != 0:
        if k[0] not in used_subscribers:
          d1 = {}
          d1['id'] = k[0]
          d1['group'] = 1
          data['nodes'].append(d1)
          used_subscribers[k[0]] = 1
        if k[1] not in used_subscribers:
          d2 = {}
          d2['id'] = k[1]
          d2['group'] = 1
          data['nodes'].append(d2)
          used_subscribers[k[1]] = 1
        link['value'] = val
        data['links'].append(link)
  print "writing"
  json.dump(data,subscribers_graph, indent=4)
  print "done"
  subscribers_graph.close()

def popular_subreddits_unweighted(subreddits, subscribers, top_n):
  popular = sorted(subreddits, key = lambda k: len(subreddits[k]) / float(subscribers[k]), reverse = True)
  return popular[:top_n]

def popular_subreddits_weighted(subreddits, comments, top_n):
  popular = sorted(subreddits, key = lambda k: subreddits[k] / float(comments[k]), reverse = True)
  return popular[:top_n]

def gen_requester_unweighted(dataset):
  requesters = collections.defaultdict(lambda: list())
  subreddits_unweighted = collections.defaultdict(lambda: list())

  for i in xrange(len(dataset)):
    request = dataset[i]
    requester = request['requester_username']
    subreddits = request['requester_subreddits_at_request']

    for subreddit in subreddits:
      subreddit = '/r/' + subreddit
      requesters[requester].append(subreddit)
      subreddits_unweighted[subreddit].append(requester)

  return requesters, subreddits_unweighted

def gen_giver_unweighted(givers_comments):
  subreddits_unweighted = collections.defaultdict(lambda: list())

  for giver in givers_comments:
    subreddits = givers_comments[giver]

    for subreddit in subreddits:
      subreddit = '/r/' + subreddit
      subreddits_unweighted[subreddit].append(giver)

  return subreddits_unweighted

def gen_giver_weighted(dataset, givers_comments):
  subreddits_weighted = collections.defaultdict(lambda: 0)

  for giver in givers_comments:
    subreddits = givers_comments[giver]

    for subreddit in subreddits:
      subreddits_weighted[subreddit] += subreddits[subreddit]

  return subreddits_weighted

def main(dataset):
  subscribers = subreddit_subscribers()
  givers_comments = get_givers_comments()
  subreddit_comments = get_subreddit_comments()
  
  requesters, requester_subreddits_unweighted = gen_requester_unweighted(dataset)
  requester_subreddits_unweighted = {k:v for k, v in requester_subreddits_unweighted.items() if k in subscribers}
  requester_popular_unweighted = popular_subreddits_unweighted(requester_subreddits_unweighted, subscribers, 10)
  print [(s, len(requester_subreddits_unweighted[s]), len(requester_subreddits_unweighted[s]) / float(subscribers[s])) for s in requester_popular_unweighted]

  giver_subreddits_unweighted = gen_giver_unweighted(givers_comments)
  giver_subreddits_unweighted = {k:v for k, v in giver_subreddits_unweighted.items() if k in subscribers}
  giver_popular_unweighted = popular_subreddits_unweighted(giver_subreddits_unweighted, subscribers, 10)
  print [(s, len(giver_subreddits_unweighted[s]), len(giver_subreddits_unweighted[s]) / float(subscribers[s])) for s in giver_popular_unweighted]

  giver_subreddits_weighted = gen_giver_weighted(dataset, givers_comments)
  giver_subreddits_weighted = {k:v for k, v in giver_subreddits_weighted.items() if k in subreddit_comments and subreddit_comments[k] > 1000}
  giver_popular_weighted = popular_subreddits_weighted(giver_subreddits_weighted, subreddit_comments, 10)
  print [(s, giver_subreddits_weighted[s], giver_subreddits_weighted[s] / float(subreddit_comments[s])) for s in giver_popular_weighted]

  # subreddit_to_subscribers = read_subreddits(dataset)
  # subreddits_only_graph(subreddit_to_subscribers, subreddits_unweighted)

if __name__ == '__main__':
  path = './pizza_request_dataset/pizza_request_dataset.json'
  dataset = read_dataset(path)

  main(dataset)
