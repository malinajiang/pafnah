import codecs
import json
import pickle
import collections

def read_dataset(path):
  with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()
  dataset = json.loads(content)
  return dataset

def get_requesters_givers(dataset):
  requesters = set()
  givers = set()

  for i in xrange(len(dataset)):
    request = dataset[i]
    requester = request['requester_username']
    giver = request['giver_username_if_known']

    requesters.add(requester)
    if giver != 'N/A':
      givers.add(giver)

  requesters_file = open('pizza_requesters.txt', 'wb')
  pickle.dump(requesters, requesters_file)
  requesters_file.close()

  givers_file = open('pizza_givers.txt', 'wb')
  pickle.dump(givers, givers_file)
  givers_file.close()

def main():
  path = './pizza_request_dataset/pizza_request_dataset.json'
  dataset = read_dataset(path)
  get_requesters_givers(dataset)

if __name__ == '__main__':
  main()
