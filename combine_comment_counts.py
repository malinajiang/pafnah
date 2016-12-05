import dill
import sys
import os

def main(dirn, prefix):
	d = os.listdir(dirn)
	files = []
	for f in d:
		if f[:len(prefix)] == prefix:
			r = f[len(prefix)+1:-4]
			start, end = r.split('_')
			files.append((int(start), int(end), f))
	files.sort(reverse=True)
	counts = {}
	for f in files:
		fp = open(dirn + '/' + f[2], 'r')
		counts.update(dill.load(fp))
		fp.close()
	fp = open('combined_' + prefix, 'w')
	dill.dump(counts, fp)
	fp.close()

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2])
