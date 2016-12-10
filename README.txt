normalized_final_comment_counts.txt
Use dill. Dict from user to dict of subreddit to comment count. Contains only users in Jurafsky dataset.

In the data directory
	USE_THIS_comment_counts.txt
		Jurafsky users with data-less users filtered out. Normalized comment counts.
Use dill for:
	indices.txt
		sorted list of users in weights.txt
	weights.txt
		weight matrix
	degrees.txt
		degree vector.
	top_degrees.txt
		degree vector after sparsifying.
	km_counters.txt
		list of counters from kmeans
	km_kmeans.txt
		kmeans objects for top_vecs.txt

use numpy for
	top_vals.txt
		sorted eigenvalues for top_lagrangian_sparse.txt
	top_vecs.txt
		eigenvectors for top_lagrangian_sparse.txt corresponding to top_vals.txt

use scipy.io for:
	top_weights_sparse.txt
		weight matrix after sparsifying
	top_degrees_sparse.txt
		degree matrix after sparsifying
	top_lagrangian_sparse.txt
		lagrangian matrix after sparsifying