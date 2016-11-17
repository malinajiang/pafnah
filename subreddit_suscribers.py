import collections
from bs4 import BeautifulSoup
from urllib2 import urlopen
import pickle

def subreddit_suscribers():
  base_url = 'http://redditmetrics.com/top/offset/'
  suscribers = dict()
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
      num_suscribers = subreddit[2].find(text = True)
      num_suscribers = int(num_suscribers.replace(',', ''))

      if num_suscribers < 1000:
        success = False
        break

      suscribers[name] = int(num_suscribers)

    if not success:
      break

    page += 1

  suscribers_file = open('subreddit_suscribers.txt', 'wb')
  pickle.dump(suscribers, suscribers_file)
  suscribers_file.close()

def main():
  subreddit_suscribers()

if __name__ == '__main__':
  main()