import dill
import collections
import sys
import snap
from scipy import io
from scipy.stats import ttest_ind
from scipy.cluster.vq import kmeans,vq
import random
from pygraph.classes.graph import graph
from pygraph.algorithms.minmax import shortest_path

# all_subscribers: list of usernames
# subscriber_ids: dict of username to # id
def init():
	edges = collections.defaultdict(lambda: set())
	# with open ('./data/USE_THIS_comment_counts.txt') as f:

	# 	d = dill.load(f)
	# 	all_subscribers = sorted(d.keys())
	# 	subscriber_ids = {}
	# 	for i in xrange(len(all_subscribers)):
	# 		subscriber_ids[all_subscribers[i]] = i
	
	# f.close()
	# print 'Loaded comment counts'
	
	f = open('pizza_requesters.txt', 'r')
	requesters = dill.load(f)
	f.close()

	f2 = open('pizza_givers.txt', 'r')
	givers = dill.load(f2)
	f2.close()

	f3 = open('successful_requests.txt', 'r')
	successful = dill.load(f3)
	f3.close()

	subscriber_ids = {}
	with open('./data/indices.txt') as f:
		all_subscribers = dill.load(f)
		for i in xrange(len(all_subscribers)):
			subscriber_ids[all_subscribers[i]] = i
	f.close()

	print 'Loaded requesters and givers'

	with open('./data/top_weights_sparse.txt.mtx') as f:
		w = io.mmread(f)
		weights = w.toarray()

		for i in xrange(len(weights)):
			tupled_weights = [(j, weights[i][j]) for j in xrange(len(weights[i]))]
			sorted_weights = sorted(tupled_weights, key = lambda x: x[1], reverse=True)
			num = 0
			for x in sorted_weights:
				if x[1] != 0 and (all_subscribers[x[0]] in requesters or all_subscribers[x[0]] in givers):
					edges[i].add(x[0])
					edges[x[0]].add(i)
					if all_subscribers[i] in successful and all_subscribers[x[0]] in successful:
						if successful[all_subscribers[i]] == all_subscribers[x[0]]:
							completed+=1
					num += 1
				if num == 5:
					break
	f.close()
	print 'Loaded weights'

	snap_graph = snap.TUNGraph.New()
	for node in edges:
		if not snap_graph.IsNode(node):
			snap_graph.AddNode(node)
		for neighbor in edges[node]:
			if not snap_graph.IsNode(neighbor):
				snap_graph.AddNode(neighbor)
			if not snap_graph.IsEdge(node, neighbor):
				snap_graph.AddEdge(node, neighbor)

	# shortest_graph = None
	shortest_graph = graph()
	for node in edges:
		if not shortest_graph.has_node(node):
			shortest_graph.add_node(node)
		for neighbor in edges[node]:
			if not shortest_graph.has_node(neighbor):
				shortest_graph.add_node(neighbor)
			if not shortest_graph.has_edge((node, neighbor)):
				shortest_graph.add_edge((node, neighbor), wt = weights[node][neighbor])

	return (edges, subscriber_ids, weights, snap_graph, shortest_graph, successful, requesters, givers, all_subscribers)

def degree(edges, weights, subscriber_ids, successful, requesters, givers):
	weights = weights.tolist()

	degrees = {}
	for node in edges:
		degrees[node] = sum(weights[node][i] for i in edges[node])

	all_users = requesters | givers

	succ_degrees = list()
	unsucc_degrees = list()
	succ_weights = list()
	unsucc_weights = list()
	for requester in requesters:
		if requester in subscriber_ids and subscriber_ids[requester] in degrees:
			if requester in successful:
				succ_degrees.append(degrees[subscriber_ids[requester]])
				succ_weights.extend([x for x in weights[subscriber_ids[requester]] if x > 0])
			else:
				unsucc_degrees.append(degrees[subscriber_ids[requester]])
				unsucc_weights.extend([x for x in weights[subscriber_ids[requester]] if x > 0])

	giver_degrees = list()
	giver_weights = list()
	for giver in givers:
		if giver in subscriber_ids and subscriber_ids[giver] in degrees:
			giver_degrees.append(degrees[subscriber_ids[giver]])
			giver_weights.extend([x for x in weights[subscriber_ids[giver]] if x > 0])


	t, p = ttest_ind(succ_degrees, unsucc_degrees, equal_var=False)
	print 'Successful vs. unsuccessful degrees: ', t, p

	t, p = ttest_ind(succ_degrees, giver_degrees, equal_var=False)
	print 'Successful vs. giver degrees: ', t, p

	t, p = ttest_ind(unsucc_degrees, giver_degrees, equal_var=False)
	print 'Unsuccessful vs. giver degrees: ', t, p

	print 'Successful requester average out degree: ', sum(succ_degrees) / float(len(succ_degrees))
	print 'Unsuccessful requester average out degree: ', sum(unsucc_degrees) / float(len(unsucc_degrees))
	print 'Giver average out degree: ', sum(giver_degrees) / float(len(giver_degrees))

	t, p = ttest_ind(succ_weights, unsucc_weights, equal_var=False)
	print 'Successful vs. unsuccessful weights: ', t, p

	t, p = ttest_ind(succ_weights, giver_weights, equal_var=False)
	print 'Successful vs. giver weights: ', t, p

	t, p = ttest_ind(unsucc_weights, giver_weights, equal_var=False)
	print 'Unsuccessful vs. giver weights: ', t, p		

	print 'Successful requester average weight: ', sum(succ_weights) / float(len(succ_weights))
	print 'Unsuccessful requester average weight: ', sum(unsucc_weights) / float(len(unsucc_weights))
	print 'Giver average weight: ', sum(giver_weights) / float(len(giver_weights))

	succ_succ_weights = list()
	succ_unsucc_weights = list()
	succ_giver_weights = list()
	unsucc_unsucc_weights = list()
	unsucc_giver_weights = list()
	giver_giver_weights = list()
	requester_giver_weights = list()

	for u1 in all_users:
		for u2 in all_users:
			if u1 == u2 or u1 not in subscriber_ids or u2 not in subscriber_ids:
				continue

			if u1 in successful and u2 in successful:
				succ_succ_weights.append(weights[subscriber_ids[u1]][subscriber_ids[u2]])
			elif u1 in successful and u2 not in successful and u2 not in givers:
				succ_unsucc_weights.append(weights[subscriber_ids[u1]][subscriber_ids[u2]])
			elif u1 in successful and u2 in givers:
				succ_giver_weights.append(weights[subscriber_ids[u1]][subscriber_ids[u2]])
			elif u1 not in successful and u2 not in successful and u2 not in givers:
				unsucc_unsucc_weights.append(weights[subscriber_ids[u1]][subscriber_ids[u2]])
			elif u1 not in successful and u1 not in givers and u2 in givers:
				unsucc_giver_weights.append(weights[subscriber_ids[u1]][subscriber_ids[u2]])
			elif u1 in givers and u2 in givers:
				giver_giver_weights.append(weights[subscriber_ids[u1]][subscriber_ids[u2]])
			else:
				continue

			if u1 in successful and u2 == successful[u1]:
				requester_giver_weights.append(weights[subscriber_ids[u1]][subscriber_ids[u2]])

	succ_succ_weights = [x for x in succ_succ_weights if x > 0]
	succ_unsucc_weights = [x for x in succ_unsucc_weights if x > 0]
	succ_giver_weights = [x for x in succ_giver_weights if x > 0]
	unsucc_unsucc_weights = [x for x in unsucc_unsucc_weights if x > 0]
	unsucc_giver_weights = [x for x in unsucc_giver_weights if x > 0]
	giver_giver_weights = [x for x in giver_giver_weights if x > 0]
	requester_giver_weights = [x for x in requester_giver_weights if x > 0]

	print 'Successful-successful average weight: ', sum(succ_succ_weights) / float(len(succ_succ_weights))
	print 'Successful-unsuccessful average weight: ', sum(succ_unsucc_weights) / float(len(succ_unsucc_weights))
	print 'Successful-giver average weight: ', sum(succ_giver_weights) / float(len(succ_giver_weights))
	print 'Unsuccessful-unsuccessful average weight: ', sum(unsucc_unsucc_weights) / float(len(unsucc_unsucc_weights))
	print 'Unsuccessful-giver average weight: ', sum(unsucc_giver_weights) / float(len(unsucc_giver_weights))
	print 'Giver-giver average weight: ', sum(giver_giver_weights) / float(len(giver_giver_weights))
	print 'Requester-giver average weight: ', sum(requester_giver_weights) / float(len(requester_giver_weights))

	f = open('degrees_filtered.txt', 'w')
	dill.dump(degrees, f)
	f.close()

def betweenness_centrality(graph, all_subscribers, successful, requesters, givers):
	Nodes = snap.TIntFltH()
	Edges = snap.TIntPrFltH()
	snap.GetBetweennessCentr(graph, Nodes, Edges, 1.0)

	succ_btwn = list()
	unsucc_btwn = list()
	giver_btwn = list()
	node_centralities = {}

	for node in Nodes:
		user = all_subscribers[node]
		if user in successful:
			succ_btwn.append(Nodes[node])
		elif user in requesters:
			unsucc_btwn.append(Nodes[node])

		if user in givers:
			giver_btwn.append(Nodes[node])

		node_centralities[node] = Nodes[node]

	t, p = ttest_ind(succ_btwn, unsucc_btwn, equal_var=False)
	print 'Successful vs. unsuccessful betweenness: ', t, p

	t, p = ttest_ind(succ_btwn, giver_btwn, equal_var=False)
	print 'Successful vs. giver betweenness: ', t, p

	t, p = ttest_ind(unsucc_btwn, giver_btwn, equal_var=False)
	print 'Unsuccessful vs. giver betweenness: ', t, p	

	print 'Successful requester average betweenness centrality: ', sum(succ_btwn) / float(len(succ_btwn))
	print 'Unsuccessful requester average betweenness centrality: ', sum(unsucc_btwn) / float(len(unsucc_btwn))
	print 'Giver average betweenness centrality: ', sum(giver_btwn) / float(len(giver_btwn))

	f = open('betweenness_centrality_filtered.txt', 'w')
	dill.dump(node_centralities, f)
	f.close()

def shortest_paths(graph, subscriber_ids, successful, requesters, givers, all_subscribers):
	succ_short_paths = []
	unsucc_short_paths = []
	giver_short_paths = []

	shortest_paths = dict()

	for requester in requesters:
		if requester in subscriber_ids:
			if graph.has_node(subscriber_ids[requester]):
				(tree, dists) = shortest_path(graph, subscriber_ids[requester])
				avg_shorted_path = list()
				for target, value in dists.items():
					if all_subscribers[target] in givers:
						if requester in successful:
							succ_short_paths.append(dists[target])
						else:
							unsucc_short_paths.append(dists[target])

						avg_shorted_path.append(dists[target])
				
				shortest_paths[requester] = sum(avg_shorted_path) / float(len(avg_shorted_path))

	for giver in givers:
		if giver in subscriber_ids:
			if graph.has_node(subscriber_ids[giver]):
				(trees, dist) = shortest_path(graph, subscriber_ids[giver])
				for target, value in dists.items():
					if all_subscribers[target] in givers:
						giver_short_paths.append(dists[target])

	t, p = ttest_ind(succ_short_paths, unsucc_short_paths, equal_var=False)
	print 'Successful vs. unsuccessful shortest paths: ', t, p

	t, p = ttest_ind(succ_short_paths, giver_short_paths, equal_var=False)
	print 'Successful vs. giver shortest paths: ', t, p

	t, p = ttest_ind(unsucc_short_paths, giver_short_paths, equal_var=False)
	print 'Unsuccessful vs. giver shortest paths: ', t, p	

	print "Successful shortest paths: ", sum(succ_short_paths) / float(len(succ_short_paths))
	print "Unsuccessful shortest paths: ", sum(unsucc_short_paths) / float(len(unsucc_short_paths))
	print "Giver shortest paths: ", sum(giver_short_paths) / float(len(giver_short_paths))

	f = open('shortest_paths.txt', 'w')
	dill.dump(shortest_paths, f)
	f.close()

def coarsening(edges, subscriber_ids, weights, num_clusters):
	weights = weights.tolist()
	clusters = dict()
	iteration = 0

	for node in edges.keys():
		cluster = set()
		cluster.add(node)
		clusters[node] = cluster

	prev_nodes = 2 * len(edges)
	while len(edges) > num_clusters:
		num_nodes = len(edges)

		if (prev_nodes - num_nodes < 2):
			break
		else:
			prev_nodes = num_nodes

		nodes = clusters.keys()
		random.shuffle(nodes)

		matched = set()
		counter = 0
		for node in nodes:
			counter += 1
			print "Node: " + str(counter) + '/' + str(num_nodes)

			if node not in clusters:
				continue

			if node in matched:
				continue

			sorted_weights = sorted(weights[node], reverse = True)
			no_match = True

			for i in xrange(len(sorted_weights)):
				max_neighbor = weights[node].index(sorted_weights[i])
				if max_neighbor not in edges[node] or max_neighbor not in clusters:
					continue
				if max_neighbor not in matched and max_neighbor != node and sorted_weights[i] > 0:
					no_match = False
					break

			if no_match:
				continue

			clusters[node] = clusters[node].union(clusters[max_neighbor])
			clusters.pop(max_neighbor)
			
			matched.add(node)
			matched.add(max_neighbor)
			
			for edge in edges[max_neighbor]:
				if edge not in edges[node]:
					edges[node].add(edge)

				weights[edge][node] += weights[edge][max_neighbor]
				weights[node][edge] = weights[edge][node]

			edges.pop(max_neighbor, None)

		edges_f = open('edges_' + str(iteration) + '.txt', 'w')
		dill.dump(edges, edges_f)
		edges_f.close()

		weights_f = open('weights_' + str(iteration) + '.txt', 'w')
		dill.dump(weights, weights_f)
		weights_f.close()

		clusters_f = open('clusters_' + str(iteration) + '.txt', 'w')
		dill.dump(clusters, clusters_f)
		clusters_f.close()

		iteration += 1

	f = open('coarsening_combined.txt', 'w')
	dill.dump(clusters, f)
	f.close()

def clusters_to_matrices():
	edges_f = open('coarsening_data_new/edges_5.txt', 'r')
	edges = dill.load(edges_f)
	edges_f.close()
	print 'Loaded coarsening edges'

	weights_f = open('coarsening_data_new/weights_5.txt', 'r')
	weights = dill.load(weights_f)
	weights_f.close()
	print 'Loaded coarsening weights'

	clusters_f = open('coarsening_data_new/clusters_5.txt', 'r')
	clusters = dill.load(clusters_f)
	clusters_f.close()
	print 'Loaded coarsening clusters'

	count = 0
	total_nodes = set()
	for x in clusters:
		count += len(clusters[x])
		total_nodes = total_nodes.union(clusters[x])

	cluster_nodes = dict()
	nodes = sorted(clusters.keys())
	for i in xrange(len(nodes)):
		cluster_nodes[nodes[i]] = i

	weights_matrix = [[0 for x in range(len(nodes))] for y in range(len(nodes))]
	for i in xrange(len(weights)):
		for j in xrange(len(weights[i])):
			if i in cluster_nodes and j in cluster_nodes:
				weights_matrix[cluster_nodes[i]][cluster_nodes[j]] = weights[i][j]

	weights_matrix_f = open('coarsening_weights_matrix.txt', 'w')
	dill.dump(weights_matrix, weights_matrix_f)
	weights_matrix_f.close()

	degrees_vector = list()
	for i in xrange(len(nodes)):
		degrees_vector.append(sum(weights_matrix[i]))

	degrees_vector_f = open('coarsening_degrees_vector.txt', 'w')
	dill.dump(degrees_vector, degrees_vector_f)
	degrees_vector_f.close()

def uncoarsening():
	f = open('coarsening_data_new/top_km.txt', 'r')
	top_km = dill.load(f)
	f.close()

	f2 = open('coarsening_data_new/top_km_counters.txt', 'r')
	top_km_counters = dill.load(f2)
	f2.close()

	clusters_f = open('coarsening_data_new/clusters_5.txt', 'r')
	clusters = dill.load(clusters_f)
	clusters_f.close()
	print 'Loaded coarsening clusters'

	uncoarsened_clusters = list()

	nodes = sorted(clusters.keys())
	num_nodes = 3932

	for i in xrange(len(top_km)):
		num_clusters = top_km[i].n_clusters
		assignment = top_km[i].labels_
		kmeans_cluster = [0] * num_nodes

		for j in xrange(len(nodes)):
			for k in clusters[nodes[j]]:
				kmeans_cluster[k] = assignment[j]
		uncoarsened_clusters.append((num_clusters, kmeans_cluster))

	f = open('uncoarsened_kmeans.txt', 'w')
	dill.dump(uncoarsened_clusters, f)
	f.close()

def main():
	edges, subscriber_ids, weights, graph, shortest_graph, successful, requesters, givers, all_subscribers = init()
	# coarsening(edges, subscriber_ids, weights, 500)
	# clusters_to_matrices()
	uncoarsening()
	# degree(edges, weights, subscriber_ids, successful, requesters, givers)
	# betweenness_centrality(graph, all_subscribers, successful, requesters, givers)
	# shortest_paths(shortest_graph, subscriber_ids, successful, requesters, givers, all_subscribers)

if __name__ == '__main__':
	main()