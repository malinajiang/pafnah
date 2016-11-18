import collections
import praw
import dill
import sys

def main(start, length):
	r = praw.Reddit(user_agent="Counting comment and submission count for subreddits for each user who has posted in Random Acts of Pizza by /u/spunker325")
	f = open('authors.txt', 'r')
	counts = {}
	linecount = 0
	invalids = []
	for i in range(start):
		line = f.readline()
	for line in f:
		if linecount % 25 == 0:
				print linecount
		if linecount == length:
			break
		linecount += 1
		author, time = line.split()
		time = float(time)
		user = r.get_redditor(author)
		if author in counts:
			continue
		user_counts = collections.defaultdict(lambda: 0)
		try:
			for comment in user.get_comments(limit=None):
				if comment.created_utc < time:
					user_counts[comment.subreddit.display_name] += 1
			for post in user.get_submitted(limit=None):
				if post.created_utc < time:
					user_counts[post.subreddit.display_name] += 1
			counts[author] = user_counts
		except (praw.errors.NotFound, praw.errors.Forbidden) as e:
			print author, e
			invalids.append(author)
	f.close()
	f = open('comment_counts_' + str(start) + '_' + str(start+length-1) + '.txt', 'w')
	dill.dump(counts, f)
	f.close()
	print invalids

if __name__ == "__main__":
	main(int(sys.argv[1]), int(sys.argv[2]))
