import dill
import collections
import sys
# import snap
from scipy import io
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

	completed = 0
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
	print completed
	f.close()
	print 'Loaded weights'

	# graph = snap.TUNGraph.New()
	# for node in edges:
	# 	if not graph.IsNode(node):
	# 		graph.AddNode(node)
	# 	for neighbor in edges[node]:
	# 		if not graph.IsNode(neighbor):
	# 			graph.AddNode(neighbor)
	# 		if not graph.IsEdge(node, neighbor):
	# 			graph.AddEdge(node, neighbor)

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

	return (edges, subscriber_ids, weights, graph, shortest_graph, successful, requesters, givers, all_subscribers)

def degree(edges, weights, subscriber_ids, successful, requesters, givers):
	degrees = {}
	for node in edges:
		degrees[node] = sum(weights[node][i] for i in edges[node])

	print len(edges)
	print len(weights)

	print 'successful'
	print successful.keys()

	print 'requesters'
	print requesters

	print 'subscribers'
	print subscriber_ids.keys()

	succ_degrees = list()
	unsucc_degrees = list()
	for requester in requesters:
		if requester in subscriber_ids and subscriber_ids[requester] in degrees:
			if requester in successful:
				succ_degrees.append(degrees[subscriber_ids[requester]])
			else:
				unsucc_degrees.append(degrees[subscriber_ids[requester]])

	giver_degrees = list()
	for giver in givers:
		if giver in subscriber_ids and subscriber_ids[giver] in degrees:
			giver_degrees.append(degrees[subscriber_ids[giver]])

	print 'Successful requester average out degree: ', sum(succ_degrees) / float(len(succ_degrees))
	print 'Unsuccessful requester average out degree: ', sum(unsucc_degrees) / float(len(unsucc_degrees))
	print 'Giver average out degree: ', sum(giver_degrees) / float(len(giver_degrees))

	f = open('degrees_filtered.txt', 'w')
	dill.dump(degrees, f)
	f.close()

def betweenness_centrality(graph):
	Nodes = snap.TIntFltH()
	Edges = snap.TIntPrFltH()
	snap.GetBetweennessCentr(graph, Nodes, Edges, 1.0)

	node_centralities = {}
	for node in Nodes:
		node_centralities[node] = Nodes[node]

	f = open('betweenness_centrality_filtered.txt', 'w')
	dill.dump(node_centralities, f)
	f.close()

def shortest_paths(graph, subscriber_ids, successful, requesters, givers, all_subscribers):
	succ_short_paths = []
	nosucc_short_paths = []
	count = 0
	for requester in requesters:
		count += 1
		print count
		if requester in subscriber_ids:
			if graph.has_node(subscriber_ids[requester]):
				(tree, dists) = shortest_path(graph, subscriber_ids[requester])
				for target, value in dists.items():
					if all_subscribers[target] in givers:
						print 'here'
						if successful[requester] == all_subscribers[target]:
							succ_short_paths.append(dists[target])
						else:
							nosucc_short_paths.append(dists[target])

	print "Successful: ", sum(succ_short_paths) / float(len(succ_short_paths))
	print "Unsuccessful: ", sum(nosucc_short_paths) / float(len(nosucc_short_paths))

def coarsening(edges, subscriber_ids, weights, num_clusters):
	clusters = collections.defaultdict(lambda: set())
	iteration = 0

	while len(edges) > num_clusters:
		num_nodes = len(edges)

		nodes = edges.keys()
		random.shuffle(nodes)

		matched = set()

		print num_nodes

		counter = 0

		for node in nodes:
			counter += 1
			print "Node: " + str(counter) + '/' + str(num_nodes)

			if node in matched:
				continue

			sorted_weights = sorted(weights[node], reverse = True)
			no_match = True

			for i in xrange(len(sorted_weights)):
				max_neighbor = weights[node].index(sorted_weights[i])
				if max_neighbor not in edges[node]:
					continue
				if max_neighbor not in matched and sorted_weights[i] > 0:
					no_match = False
					break

			if no_match:
				continue

			clusters[node].add(max_neighbor)
			if max_neighbor in clusters:
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
		

	print clusters
	f = open('coarsening_combined.txt', 'w')
	dill.dump(clusters, f)
	f.close()

def clusters_to_matrices():
	edges_f = open('coarsening_edges.txt', 'r')
	edges = dill.load(edges_f)
	edges_f.close()
	print 'Loaded coarsening edges'

	weights_f = open('coarsening_weights.txt', 'r')
	weights = dill.load(weights_f)
	weights_f.close()
	print 'Loaded coarsening weights'

	clusters_f = open('coarsening_clusters.txt', 'r')
	clusters = dill.load(clusters_f)
	clusters_f.close()
	print 'Loaded coarsening clusters'

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

	print degrees_vector

	degrees_vector_f = open('coarsening_degrees_vector.txt', 'w')
	dill.dump(degrees_vector, degrees_vector_f)
	degrees_vector_f.close()

def main():
	edges, subscriber_ids, weights, graph, shortest_graph, successful, requesters, givers, all_subscribers = init()
	# coarsening(edges, subscriber_ids, weights, 4000)
	# clusters_to_matrices()
	# degree(edges, weights, subscriber_ids, successful, requesters, givers)
	# betweenness_centrality(graph)
	shortest_paths(shortest_graph, subscriber_ids, successful, requesters, givers, all_subscribers)

if __name__ == '__main__':
	main()