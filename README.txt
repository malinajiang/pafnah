normalized_final_comment_counts.txt
Use dill. Dict from user to dict of subreddit to comment count. Contains only users in Jurafsky dataset.

In the data directory - everything based on nonzero_counts.txt
use dill for:
	indices.txt
		sorted list of users in normalized_final_comment_counts.
	weights.txt
		weight matrix
	degrees.txt
		degree vector
	nonzero_counts.txt
		normalized_final_comments_counts with data-less users filtered out.
	top_degrees.txt
		degree vector after sparsifying.
	top_vals.txt
		sorted eigenvalues for top_lagrangian_sparse.txt
	top_vecs.txt
		eigenvectors for top_lagrangian_sparse.txt corresponding to top_vals.txt
	km_centers1,2.txt
		list of cluster centers from kmeans
	km_num_clusters.txt
		list of number of clusters at each index for kmeans
	km_counters.txt
		list of counters from kmeans
	km_labels.txt
		list of labels from kmeans
	km_kmeans1,2.txt
		kmeans objects for top_vecs.txt

use scipy.io for:
	top_weights_sparse.txt
		weight matrix after sparsifying
	top_degrees_sparse.txt
		degree matrix after sparsifying
	top_lagrangian_sparse.txt
		lagrangian matrix after sparsifying