import dill
import sys
import os
import math

def main(filename):
	f = open(filename, 'r')
	counts = dill.load(f)
	f.close()
	for user in counts:
		s = 0
		for count in counts[user].values():
			s += count * count
		magnitude = math.sqrt(s)
		for sr in counts[user]:
			counts[user][sr] /= magnitude
	f = open('normalized_' + filename, 'w')
	dill.dump(counts, f)
	f.close()

if __name__ == "__main__":
	main(sys.argv[1])
