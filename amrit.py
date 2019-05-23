import json, time
from dijkstra import Graph, createGraphFromGeojson

config = {}
config['graph_file'] = 'graph.json'
config['nodes_file'] = 'selected_nodes.geojson'
config['edges_file'] = 'selected_edges.geojson'
config['landmarks_file'] = 'selected_landmarks.geojson'

try:
    with open(config['graph_file'],'r') as fp:
        edges = json.load(fp)
except:
    print("graph file doesn't exist ")
    edges = createGraphFromGeojson(config['nodes_file'],config['edges_file'])
try:
    with open(config['landmarks_file'],'r') as fp:
        landmarks_json = json.load(fp)
        landmarks = landmarks_json["features"]
except:
    landmarks = {}
if(edges):
    graph = Graph(edges,landmarks,config)
else:
    raise


print(graph.dijkstra("5099", "375").result['removedvertices'])
t4 = time.time()
graph.get_geom_from_path()
# print(graph.result['geom_path'])
with open('simple_djikstra.geojson','w') as f:
    f.write(graph.to_geojson())
    f.close()

print(graph.dijkstra_landmark("5099", "375").result['removedvertices'])
graph.get_geom_from_path()
# print(graph.result['geom_path'])
with open('simple_djikstra_landmark.geojson','w') as f:
    f.write(graph.to_geojson())
    f.close()