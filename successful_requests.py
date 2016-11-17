import codecs
import json
import pickle
import collections

def read_dataset(path):
  with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()
  dataset = json.loads(content)
  return dataset

def get_successful_requests(dataset):
  successful_requests = dict()
  edited = dict()
  number_edited = 0

  for i in xrange(len(dataset)):
    request = dataset[i]
    requester = request['requester_username']
    giver = request['giver_username_if_known']
    request_text = request['request_text']
    edit_aware = request['request_text_edit_aware']

    if request['requester_received_pizza']:
      if giver == 'N/A':
        edited_text = request_text.replace(edit_aware, '').strip(' \n\t\r')
        if edited_text != '':
          edited[requester] = edited_text
          number_edited += 1

    successful_requests[requester] = giver

  successful_requests_file = open('successful_requests.txt', 'wb')
  pickle.dump(successful_requests, successful_requests_file)
  successful_requests_file.close()

  print 'Number of edited successful posts: %d' % number_edited

  edited_posts = open('edited_posts.txt', 'wb')
  for requester in edited:
    edited_posts.write(requester + '\n')
    edited_posts.write(edited[requester] + '\n')
    edited_posts.write('****************************************\n')

def main():
  path = './pizza_request_dataset/pizza_request_dataset.json'
  dataset = read_dataset(path)
  get_successful_requests(dataset)

if __name__ == '__main__':
  main()