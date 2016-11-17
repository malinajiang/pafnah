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

def subreddit_subscribers():
  subscribers_file = open('subreddit_subscribers.txt', 'r')
  subscribers = pickle.load(subscribers_file)
  subscribers_file.close()

  return subscribers

def popular_subreddits(subreddits, subscribers, top_n):
  popular = sorted(subreddits, key = lambda k: len(subreddits[k]) / float(subscribers[k]), reverse = True)
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
  subscribers = subreddit_subscribers()
  requesters, subreddits_unweighted = gen_requester_unweighted(dataset)
  subreddits_unweighted = {k:v for k, v in subreddits_unweighted.items() if k in subscribers and subscribers[k] > 0}
  popular = popular_subreddits(subreddits_unweighted, subscribers, 10)

  print [(s, len(subreddits_unweighted[s]), len(subreddits_unweighted[s]) / float(subscribers[s])) for s in popular]

if __name__ == '__main__':
  path = './pizza_request_dataset/pizza_request_dataset.json'
  dataset = read_dataset(path)

  main(dataset)








