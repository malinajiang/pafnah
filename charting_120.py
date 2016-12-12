
import numpy as np
import matplotlib.pyplot as plt
import pylab
import random
import matplotlib
import math
matplotlib.rcParams['backend'] = "Qt4Agg"

# top 5, degree, short = 
# eta: 1e-05
# random: 0.521642619312
# percentage: 0.886237513873

# top 10, degree, short = 
# eta: 1e-05
# random: 0.496115427303
# percentage: 0.886237513873

# top 20, degree, short = 
# eta: 1e-05
# random: 0.50332963374
# percentage: 0.886514983352

# top 50, degree, short = 
# eta: 1e-05
# random: 0.489733629301
# percentage: 0.88679245283

# top 87, degree, short = 
# eta: 0.0001
# random: 0.493063263041
# percentage: 0.889567147614
def main():
	#--------problem2.2----------
	x = [5, 10, 20, 50, 87]
	y = [88.6237513873, 88.6237513873, 88.6514983352, 88.679245283, 88.9567147614]
	# problem5 = list(sampley)
	# plt.figure(1)
	plt.plot(np.array(x), np.array(y), 'b')
	# plt.title("Sampling")
	plt.xlabel("Number of Clusters")
	plt.ylabel("Accuracy(%)")

	pylab.show()

if __name__ == "__main__":
	main()