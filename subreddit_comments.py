import os
import collections
import dill

def get_subreddit_files():
  data_dir = './subreddit_comments/2014_comment_info/'
  files = list()

  for data_file in os.listdir(data_dir):
  	files.append(data_dir + data_file)

  return files


def subreddit_comments(files):
  user_comments = collections.defaultdict(lambda: collections.defaultdict(lambda: list()))
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
        score = info[3]

        user_comments[author][subreddit].append((timestamp, score))
        subreddit_comments[subreddit] += 1

  user_comments_file = open('user_comments.txt', 'wb')
  dill.dump(user_comments, user_comments_file)
  user_comments_file.close()

  subreddit_comments_file = open('subreddit_comments.txt', 'wb')
  dill.dump(subreddit_comments, subreddit_comments_file)
  subreddit_comments_file.close()

def main():
  files = get_subreddit_files()
  subreddit_comments(files)

if __name__ == '__main__':
  main()