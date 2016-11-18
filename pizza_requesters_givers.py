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
  received_pizza = 0
  giver_identified = 0

  requesters = set()
  givers = set()

  for i in xrange(len(dataset)):
    request = dataset[i]
    requester = request['requester_username']
    giver = request['giver_username_if_known']

    if request['requester_received_pizza']:
      received_pizza += 1
      if giver != 'N/A':
        giver_identified += 1

    requesters.add(requester)
    if giver != 'N/A':
      givers.add(giver)

  requesters_file = open('pizza_requesters.txt', 'wb')
  pickle.dump(requesters, requesters_file)
  requesters_file.close()

  givers_file = open('pizza_givers.txt', 'wb')
  pickle.dump(givers, givers_file)
  givers_file.close()

  givers_timestamp_file = open('pizza_givers_timestamp.txt', 'wb')
  for i in xrange(len(dataset)):
    request = dataset[i]
    giver = request['giver_username_if_known']
    if giver != 'N/A':
      timestamp = request['unix_timestamp_of_request']
      givers_timestamp_file.write(giver + '\t' + str(timestamp) + '\n')
  givers_timestamp_file.close()


  print 'Number of successful requests: %d' % received_pizza
  print 'Number of identifiable givers: %d' % giver_identified

def main():
  path = './pizza_request_dataset/pizza_request_dataset.json'
  dataset = read_dataset(path)
  get_requesters_givers(dataset)

if __name__ == '__main__':
  main()
