import codecs
import json
import math
import dill 
import pickle
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

def subreddit_comments():
  subreddit_comments_file = open('subreddit_comments.txt', 'r')
  subreddit_comments = dill.load(subreddit_comments_file)
  subreddit_comments_file.close()
  return subreddit_comments

def requester_comments():
  requester_comments_file = open('requester_comments.txt', 'r')
  requester_comments = dill.load(requester_comments_file)
  requester_comments_file.close()
  print len(requester_comments)
  return requester_comments

def subreddits_user_graph(subreddit, user):
  subreddit_users_graph = open('subreddit_requesters_graph.json', 'w')
  data = {}
  data['nodes'] = []
  data['links'] = []
  numsubreddits = 0
  useds = {}
  for s in subreddit:
    if subreddit[s] > 1200:
      numsubreddits += 1
      d = {}
      d['id'] = s
      d['group'] = 3
      data['nodes'].append(d)
      useds[s] = 1

  numusers = 700
  for u,subreddits in user.items():
    if numusers != 0:
      d = {}
      d['id'] = u
      d['group'] = 4
      data['nodes'].append(d)
      for s,n in subreddits.items():
        if s in useds:
          val = int(100*(float(n)/subreddit[s]))
          if val >= 1:
            link = {}
            link['source'] = u
            link['target'] = s
            link['value'] = 100*(float(n)/subreddit[s])
            data['links'].append(link)
      numusers -= 1
  json.dump(data,subreddit_users_graph, indent=4)
  subreddit_users_graph.close()

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

def subreddits_only_graph(subreddit_to_subscribers, subscribers, popular):
  print "here"
  subscribers_graph = open('subreddit_only_graph.json', 'w')
  data = {}
  data['nodes'] = []
  data['links'] = []
  subreddit_pairs = {}
  nonempty = 0
  for i in subreddit_to_subscribers:
    for j in subreddit_to_subscribers:
      if i != j and (j, i) not in subreddit_pairs:
        l = []
        s = set(subreddit_to_subscribers[i])
        t = set(subreddit_to_subscribers[j])
        for subscriber in s:
          if subscriber in t:
            nonempty+=1
            l.append(subscriber)
        if len(l) != 0:
          subreddit_pairs[(i,j)] = l

  print nonempty
  print "writing json"
  used_subscribers = {}
  for k,v in subreddit_pairs.items():
    if '/r/'+k[0] in subscribers and '/r/'+k[1] in subscribers and '/r/'+k[0] in popular and '/r/'+k[1] in popular:
      val = int(100*float(len(v))/(len(subscribers['/r/'+k[0]])+len(subscribers['/r/'+k[1]])))
      if val >= 1 :
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
        link = {}
        link['source'] = k[0]
        link['target'] = k[1]
        link['value'] = val
        data['links'].append(link)
  print "writing"
  json.dump(data,subscribers_graph, indent=4)
  print "done"
  subscribers_graph.close()

def popular_subreddits(subreddits, subscribers, top_n):
  popular = sorted(subreddits, key = lambda k: len(subreddits[k]) / float(subscribers[k]), reverse = True)
  p = {}
  for i in xrange(top_n/2):
    p[popular[i]] = 1
  mid = len(popular)/2
  for j in xrange(len(popular)-top_n/2, len(popular)):
    p[popular[j]] = 1
  # return popular[:top_n]
  return p

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

def main(dataset):
  s_comments = subreddit_comments()
  r_comments = requester_comments()
  subreddits_user_graph(s_comments, r_comments)

  # suscribers = subreddit_subscribers()
  # requesters, subreddits_unweighted = gen_requester_unweighted(dataset)
  # subreddits_unweighted = {k:v for k, v in subreddits_unweighted.items() if k in suscribers and suscribers[k] > 0}
  # popular = popular_subreddits(subreddits_unweighted, suscribers, 20)
  # subreddit_to_subscribers = read_subreddits(dataset)
  # subreddits_only_graph(subreddit_to_subscribers, subreddits_unweighted, popular)

  # print [(s, len(subreddits_unweighted[s]), len(subreddits_unweighted[s]) / float(suscribers[s])) for s in popular]

if __name__ == '__main__':
  path = './pizza_request_dataset/pizza_request_dataset.json'
  dataset = read_dataset(path)

  main(dataset)
