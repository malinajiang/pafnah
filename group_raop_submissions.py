import dill
import sys
import os

def main():
	f = open('raop_submissions_edited.txt', 'r')
	requests = open('raop_request.txt', 'w')
	offers = open('raop_offer.txt', 'w')
	thanks = open('raop_thank.txt', 'w')
	metas = open('raop_meta.txt', 'w')
	contests = open('raop_contest.txt', 'w')
	bads = open('raop_bad.txt', 'w')
	others = open('raop_other.txt', 'w')
	for line in f:
		metadata = line.split('\t')
		# postid timestamp authorname flair title body edited	
		if len(metadata) != 7:
			bads.write(line)
		else:
			title = metadata[4].lower()
			body = metadata[5].lower()
			if '[req' in title or '[req' in body:
				requests.write(line)
			elif '[offer]' in title or '[offer' in body:
				offers.write(line)
			elif '[thank' in title or '[thank' in body:
				thanks.write(line)
			elif '[contest]' in title or '[contest' in body:
				contests.write(line)
			elif '[meta]' in title or '[meta' in body:
				metas.write(line)
			else:
				others.write(line)
	f.close()
	requests.close()
	offers.close()
	thanks.close()
	metas.close()
	contests.close()
	bads.close()
	others.close()

if __name__ == "__main__":
	main()
