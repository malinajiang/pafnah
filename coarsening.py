import dill
import collections
import sys
# import snap
from pygraph.classes.graph import graph
from pygraph.algorithms.minmax import shortest_path

def init():
	with open ('normalized_combined_comment_counts.txt') as f:
		edges = collections.defaultdict(lambda: set())

		d = dill.load(f)
		all_subscribers = sorted(d.keys())
		subscriber_ids = {}
		for i in xrange(len(all_subscribers)):
			subscriber_ids[all_subscribers[i]] = i
	# print subscriber_ids
	f.close()
	# print subscriber_ids['lynzee']
	print 'Loaded comment counts'
	
	f = open('pizza_requesters.txt', 'r')
	f2 = open('pizza_givers.txt', 'r')
	requesters = dill.load(f)
	givers = dill.load(f2)
	f.close()
	f2.close()
	print 'Loaded requesters and givers'

	with open('weights.txt') as f:
		weights = dill.load(f)

		for i in xrange(len(weights)):
			tupled_weights = [(j, weights[i][j]) for j in xrange(len(weights[i]))]
			sorted_weights = sorted(tupled_weights, key = lambda x: x[1], reverse=True)
			num = 0
			for x in sorted_weights:
				if x[1] != 0 and (all_subscribers[x[0]] in requesters or all_subscribers[x[0]] in givers):
					edges[i].add(x[0])
					edges[x[0]].add(i)
					num += 1
				if num == 5:
					break

	# print edges
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

	shortest_graph = graph()
	for node in edges:
		if not shortest_graph.has_node(node):
			shortest_graph.add_node(node)
		for neighbor in edges[node]:
			if not shortest_graph.has_node(neighbor):
				shortest_graph.add_node(neighbor)
			if not shortest_graph.has_edge((node, neighbor)):
				shortest_graph.add_edge((node, neighbor), wt = weights[node][neighbor])

	return (edges, subscriber_ids, weights, shortest_graph, requesters, givers)

	# edges = collections.defaultdict(lambda: list())
	# edges[0].append(1)
	# edges[0].append(2)
	# edges[1].append(2)
	# edges[1].append(0)
	# edges[2].append(0)
	# edges[2].append(3)
	# edges[2].append(1)
	# edges[3].append(2)
	# edges[3].append(4)
	# edges[4].append(3)

	# weights = []
	# weights.append([0, 0.5, 0.3, 0, 0])
	# weights.append([0.5, 0, 0.6, 0, 0])
	# weights.append([0.3, 0.6, 0, 0.1, 0])
	# weights.append([0, 0, 0.1, 0, 0.2])
	# weights.append([0, 0, 0, 0.2, 0])	

	# subscriber_ids = 0

	# return (edges, subscriber_ids, weights)

def degree(edges, weights):
	degrees = {}
	for node in edges:
		degrees[node] = sum(weights[node][i] for i in edges[node])
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

def shortest_paths(graph, all_subscribers, requesters, givers):
	# f = open('requester_comments.txt', 'r')
	# f2 = open('giver_comments.txt', 'r')
	f3 = open('successful_requests.txt', 'r')
	# requester_comments = dill.load(f)
	# giver_comments = dill.load(f2)
	successful = dill.load(f3)
	# f.close()
	# f2.close()
	f3.close()

	# requesters = set(requester_comments.keys())
	# givers = set(giver_comments.keys())
	# print all_subscribers
	succ_short_paths = []
	nosucc_short_paths = []
	count = 0
	for requester in requesters:
		count += 1
		print count
		if requester in all_subscribers:
			if graph.has_node(all_subscribers[requester]):
				(tree, dists) = shortest_path(graph, all_subscribers[requester])
				for target, value in dists.items():
					if requester in all_subscribers and target in all_subscribers and target in givers:
						requester_id = all_subscribers[requester]
						giver_id = all_subscribers[giver]
						if successful[requester_id] == giver_id:
							succ_short_paths.append(dists[target])
						else:
							nosucc_short_paths.append(dists[target])

	print "Successful: ", sum(succ_short_paths)/float(len(succ_short_paths))
	print "Unsuccessful: ", sum(nosucc_short_paths)/float(len(nosucc_short_paths))

def coarsening(edges, subscriber_ids, weights, num_clusters):
	clusters = collections.defaultdict(lambda: set())

	while len(edges) > num_clusters:
		print len(edges)

		nodes = edges.keys()
		matched = set()

		for node in nodes:
			print "Node: ", node

			if node in matched:
				continue

			# print weights[node]
			sorted_weights = sorted(weights[node], reverse = True)
			no_match = True

			for i in xrange(len(sorted_weights)):
				max_neighbor = weights[node].index(sorted_weights[i])
				if max_neighbor not in edges[node]:
					continue
				if max_neighbor not in matched and sorted_weights[i] > 0:
					no_match = False
					break

			# print "Max neighbor: ", max_neighbor

			if no_match:
				continue

			# print "Clusters before: ", clusters
			clusters[node].add(max_neighbor)
			if max_neighbor in clusters:
				clusters[node] = clusters[node].union(clusters[max_neighbor])
				clusters.pop(max_neighbor)
			
			# print "Clusters after: ", clusters
			matched.add(node)
			matched.add(max_neighbor)
			
			# print "Matched: ", matched
			for edge in edges[max_neighbor]:
				if edge not in edges[node]:
					edges[node].add(edge)

				weights[edge][node] += weights[edge][max_neighbor]
				weights[node][edge] = weights[edge][node]

			# print "Edges: ", edges
			edges.pop(max_neighbor, None)
		

	print clusters
	f = open("coarsening_combined.txt", 'w')
	dill.dump(clusters, f)
	f.close()

def main():
	edges, subscriber_ids, weights, graph, requesters, givers = init()
	# coarsening(edges, subscriber_ids, weights, 4000)
	# degree(edges, weights)
	# betweenness_centrality(graph)
	shortest_paths(graph, subscriber_ids, requesters, givers)

if __name__ == '__main__':
	main()