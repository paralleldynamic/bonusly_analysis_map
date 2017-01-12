from urllib.request import urlopen as urlopen
from urllib.request import Request as Request
from json import loads, dump
from pprint import pprint
import networkx as nx
from datetime import datetime

nodes = set()
edges = []

start_time = datetime.now()

# API token is stored separately from the application for security
with open("data_files/network_mapping_token.txt", "r") as f:
    token = f.readline()

# creates the Request abstraction for the API url for the requested user information
def make_request(api, *args):
    headers = {"Authorization": "Bearer " + token}
    get_link = "https://bonus.ly/api/v1/" + api
    if args:
        get_link = get_link + "?"
        for item in args:
            get_link = get_link + "&" + item
	# functionality to add more specific API calls
    # if kwargs:
    #     for k,v in kwargs:
    #         headers[k] = v
    return Request(get_link, headers=headers)

# dumps a JSON file for local storage of requested data, and returns the parsed Response text
# url_data takes a Request object
def write_data(outfile, url_data):
    response = urlopen(url_data)
    data = response.read().decode('utf-8', errors='ignore')
    data = loads(data)['result']
    with open(outfile, 'w', newline='', encoding='utf-8', errors='ignore') as f:
        #pprint(data, stream=f)
        dump(data,f, indent='\t')
    return data

# initial request to get all users in the company
req = make_request('users', 'limit=500', 'include_archived=false')
users = write_data("data_files/users.json", req)

# iterate through each user to pull their bonuses
# each user is added to graph nodes, each bonus is added to edges
for user in users:
    user_id = user["id"]
    api = 'users/' + user_id + '/bonuses'
    outfile_name = 'data_files/bonuses/' + user_id + "_bonuses.json"
    nodes.add(user_id)
    req = make_request(api, 'limit=500')
    data = write_data(outfile_name, req)
    for bonus in data:
        edge = tuple([user_id,bonus['giver']['id']])
        edges.append(edge)

# create a graph object and populate with users and transactions
graph = nx.Graph()
graph.add_nodes_from(nodes)
graph.add_edges_from(edges)

# write a .graphml file to create a visualization in Gephi
nx.write_graphml(graph, "network_map/bonusly_network_map.graphml", prettyprint=True)

end_time = datetime.now()

print(end_time - start_time)
