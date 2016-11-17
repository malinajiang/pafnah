import collections
import praw

def main(argv):
	r = praw.Reddit(user_agent="Counting comment and submission count for subreddits for each user who has posted in Random Acts of Pizza by /u/spunker325")
	f = open('authors.txt', 'r')
	counts = {}
	for line in f:
		author, time = line.split()
		user = r.get_redditor(author)
		if user in counts:
			continue
		user_counts = collections.defaultdict(lambda: 0)
		for comment in user.get_comments(limit=None):
			if comment.created_utc < time:
				user_counts[comment.subreddit.display_name] += 1
		for post in user.get_submission(limit=None):
			if post.created_utc < time
				user_counts[post.subreddit.display_name] += 1
		counts[user] = user_counts
	f.close()

if __name__ == "__main__":
	main()
