class Graph:
	def __init__(self):
		self.nodes = {}

	def add_node(self, node):
		self.nodes[node.name] = node

	def connect(self, node_name1, node_name2):
		node1 = self.get(node_name1)
		node2 = self.get(node_name2)

		node1.add_neigh(node2)

	def disconnect(self, node_name1, node_name2):
		node1 = self.get(node_name1)
		node2 = self.get(node_name2)

		node1.remove_neigh(node2)

	def get(self, name):
		return self.nodes[name]


	# Search functions
	def predecessors(self, node_name):
		predecessors = []
		for item in self.nodes:
			other_node = self.get(item)
			if node_name in other_node.neigh:
				predecessors.append(other_node.name)

		return predecessors

	def successors(self, node_name):
		node = self.get(node_name)

		successors = []
		for item in self.nodes:
			if item in node.neigh:
				successors.append(item)

		return successors

	def path_to_end(self, initial_node):
		return self.path_to_end_rec(initial_node, [])

	def path_to_end_rec(self, node_name, path):
		for next_node in self.predecessors(node_name):
			path.append(next_node)
			path = self.path_to_end_rec(next_node, path)
			
		return path



class Node:
	def __init__(self, name, info):
		self.name = name
		self.info = info

		self.neigh = {}

	def add_neigh(self, node):
		self.neigh[node.name] = node

	def remove_neigh(self, node_name):
		del self.neigh[node_name]
