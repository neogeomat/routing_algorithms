from collections import deque, namedtuple
import json
import time
import pickle

# we'll use infinity as a default distance to nodes.
inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')

config = {}
config['graph_file'] = 'graph.json'
config['nodes_file'] = 'selected_nodes.geojson'
config['edges_file'] = 'selected_edges.geojson'

print("Program Started at " + str(time.time()))

def make_edge(start, end, cost=1):
    return Edge(start, end, cost)

def createGraphFromGeojson(node_file=config['nodes_file'], edge_file=config['edges_file']):
        t1 = time.time()
        with open(config['edges_file'], "r") as read_file:
            edges_json = json.load(read_file)
            edges = edges_json["features"]

        with open(config['nodes_file'], "r") as read_file:
            nodes_json = json.load(read_file)
            nodes = nodes_json["features"]
        
        g = []
        for edge in edges:
            start, end = None, None
            for node in nodes:
                if (node["geometry"]["coordinates"] ==
                        edge["geometry"]["coordinates"][0][0]):

                    start = node["properties"]["nodeID"]
                if (node["geometry"]["coordinates"] ==
                        edge["geometry"]["coordinates"][0][-1]):

                    end = node["properties"]["nodeID"]

            if (start is not None) & (end is not None):
                # twice to be bidirectional
                g.append((str(start), str(end), edge["properties"]["length"]))
                g.append((str(end), str(start), edge["properties"]["length"]))
        t2 = time.time()
        print("time to load data", t2-t1)
        with open('graph.json', 'w') as outfile:  
            json.dump(g, outfile)
        return g
        # create the network

class Graph:
    # graph.pickle is the saved graph, if it doesn't exist new one is created from the geojson files.
    def __init__(self, edges=[]):
        # let's check that the data is right
        wrong_edges = [i for i in edges if len(i) not in [2, 3]]
        if wrong_edges:
            raise ValueError('Wrong edges data: {}'.format(wrong_edges))

        self.edges = [make_edge(*edge) for edge in edges]
        self.result = {}

    @property
    def vertices(self):
        return set(
            sum(
                ([edge.start, edge.end] for edge in self.edges), []
            )
        )

    def get_node_pairs(self, n1, n2, both_ends=True):
        if both_ends:
            node_pairs = [[n1, n2], [n2, n1]]
        else:
            node_pairs = [[n1, n2]]
        return node_pairs

    def remove_edge(self, n1, n2, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        edges = self.edges[:]
        for edge in edges:
            if [edge.start, edge.end] in node_pairs:
                self.edges.remove(edge)

    def add_edge(self, n1, n2, cost=1, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        for edge in self.edges:
            if [edge.start, edge.end] in node_pairs:
                return ValueError('Edge {} {} already exists'.format(n1, n2))

        self.edges.append(Edge(start=n1, end=n2, cost=cost))
        if both_ends:
            self.edges.append(Edge(start=n2, end=n1, cost=cost))

    @property
    def neighbours(self):
        neighbours = {vertex: set() for vertex in self.vertices}
        for edge in self.edges:
            neighbours[edge.start].add((edge.end, edge.cost))

        return neighbours

    def dijkstra(self, source, dest):
        assert source in self.vertices, 'Such source node doesn\'t exist'
        distances = {vertex: inf for vertex in self.vertices}
        previous_vertices = {
            vertex: None for vertex in self.vertices
        }
        distances[source] = 0
        vertices = self.vertices.copy()
        removedvertices = []

        while vertices:
            current_vertex = min(
                vertices, key=lambda vertex: distances[vertex])         
            
            for neighbour, cost in self.neighbours[current_vertex]:
                alternative_route = distances[current_vertex] + cost
                if alternative_route < distances[neighbour]:
                    distances[neighbour] = alternative_route
                    previous_vertices[neighbour] = current_vertex
            if distances[current_vertex] == inf or current_vertex == dest:
                break
            vertices.remove(current_vertex)
            removedvertices.append(current_vertex)

        path, current_vertex = deque(), dest
        while previous_vertices[current_vertex] is not None:
            path.appendleft(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        if path:
            path.appendleft(current_vertex)
        self.result["path"] = path
        self.result["removedvertices"] = removedvertices
        return self

    def get_geom_from_path(self):
        with open(config['nodes_file'], "r") as read_file:
            nodes_json = json.load(read_file)
            nodes = nodes_json["features"]
        self.result['geom_path'] = []
        for node in nodes:
            for vertex in self.result["path"]:
                if(node["properties"]["nodeID"] == int(vertex)):
                    self.result['geom_path'].append([node["geometry"]["coordinates"]])
        return self

try:
    with open(config['graph_file'],'r') as fp:
        edges = json.load(fp)
except:
    print("graph file doesn't exist ")
    edges = createGraphFromGeojson()
graph = Graph(edges)


# example of the Graph structure
# graph = Graph([
#     ("a", "b", 7),  ("a", "c", 9),  ("a", "f", 14), ("b", "c", 10),
#     ("b", "d", 15), ("c", "d", 11), ("c", "f", 2),  ("d", "e", 6),
#     ("e", "f", 9)])
t3 = time.time()
# print("time to create graph",t3-t2)
# find a route
print(graph.dijkstra("1101", "1098").result)
t4 = time.time()
print("time to find route",t4-t3)
graph.get_geom_from_path()
print(graph.result['geom_path'])
# print(graph.dijkstra("5907", "460"))
# t4 = time.time()
# print("time to finf route", t4-t3)

# TODO find the respective coordinates (nodes, edges? what should be the
# return format?
# TODO start and destination points are probably not exactly the nodes
