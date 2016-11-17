import os
import collections
import dill
import pickle

def get_subreddit_files():
  data_dir = './subreddit_comments/2014_comment_info/'
  files = list()

  for data_file in os.listdir(data_dir):
  	files.append(data_dir + data_file)

  return files

def get_requesters():
  requesters_file = open('pizza_requesters.txt', 'r')
  requesters = pickle.load(requesters_file)
  requesters_file.close()

  return requesters

def get_givers():
  givers_file = open('pizza_givers.txt', 'r')
  givers = pickle.load(givers_file)
  givers_file.close()

  return givers

def subreddit_comments(files, requesters, givers):
  requester_comments = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
  giver_comments = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
  subreddit_comments = collections.defaultdict(lambda: 0)

  for data_file in files:
    subreddit = (data_file.split('/')[-1]).split('.')[0]
    print subreddit

    if subreddit == '__count__':
      pass

    with open(data_file, 'r') as f:
      # format of lines <comment_id>\t<timestamp>\t<author>\t<score>\t<parent_id>\t<post_id>
      for line in f:
        info = line.split('\t')
        timestamp = info[1]
        author = info[2]
 
        if author in requesters:
          requester_comments[author][subreddit] += 1
          subreddit_comments[subreddit] += 1
        elif author in givers:
          giver_comments[author][subreddit] += 1
          subreddit_comments[subreddit] += 1

  requester_comments_file = open('requester_comments.txt', 'wb')
  dill.dump(requester_comments, requester_comments_file)
  requester_comments_file.close()

  giver_comments_file = open('giver_comments.txt', 'wb')
  dill.dump(giver_comments, giver_comments_file)
  giver_comments_file.close()

  subreddit_comments_file = open('subreddit_comments.txt', 'wb')
  dill.dump(subreddit_comments, subreddit_comments_file)
  subreddit_comments_file.close()

def main():
  files = get_subreddit_files()
  requesters = get_requesters()
  givers = get_givers()
  subreddit_comments(files, requesters, givers)

if __name__ == '__main__':
  main()


