import collections
from bs4 import BeautifulSoup
from urllib2 import urlopen
import pickle

def subreddit_subscribers():
  base_url = 'http://redditmetrics.com/top/offset/'
  subscribers = dict()
  success = True
  page = 0

  while True:
    url = base_url + str(page * 100)

    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('tbody')
    rankings = [tr for tr in body.findAll('tr')]

    for ranking in rankings:
      subreddit = [td for td in ranking.findAll('td')]
      name = subreddit[1].a['href']
      num_subscribers = subreddit[2].find(text = True)
      num_subscribers = int(num_subscribers.replace(',', ''))

      if num_subscribers < 1000:
        success = False
        break

      subscribers[name] = int(num_subscribers)

    if not success:
      break

    page += 1

  subscribers_file = open('subreddit_subscribers.txt', 'wb')
  pickle.dump(subscribers, subscribers_file)
  subscribers_file.close()

def main():
  subreddit_subscribers()

if __name__ == '__main__':
  main()