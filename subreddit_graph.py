import codecs
import json
import math
import pickle
import collections

def read_dataset(path):
  with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()
  dataset = json.loads(content)
  return dataset

def subreddit_suscribers():
  suscribers_file = open('subreddit_suscribers.txt', 'r')
  suscribers = pickle.load(suscribers_file)
  suscribers_file.close()

  return suscribers

def popular_subreddits(subreddits, suscribers, top_n):
  popular = sorted(subreddits, key = lambda k: len(subreddits[k]) / float(suscribers[k]), reverse = True)
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

def main(dataset):
  suscribers = subreddit_suscribers()
  requesters, subreddits_unweighted = gen_requester_unweighted(dataset)
  subreddits_unweighted = {k:v for k, v in subreddits_unweighted.items() if k in suscribers and suscribers[k] > 0}
  popular = popular_subreddits(subreddits_unweighted, suscribers, 10)

  print [(s, len(subreddits_unweighted[s]), len(subreddits_unweighted[s]) / float(suscribers[s])) for s in popular]

if __name__ == '__main__':
  path = './pizza_request_dataset/pizza_request_dataset.json'
  dataset = read_dataset(path)

  main(dataset)








