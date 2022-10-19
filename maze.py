import requests
import networkx as nx
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def dfs(base_url: str):
    visited_nodes = set()
    stack = [base_url]
    list_contents = []
    titles = {}
    edges = []
    treasures = {}
    while len(stack) > 0:
        curr_node = stack.pop()
        if curr_node in visited_nodes:
            continue
        visited_nodes.add(curr_node)
        response = requests.get(curr_node, timeout=10)
        response.raise_for_status()
        html = BeautifulSoup(response.text, 'html.parser')
        # get title
        title = html.select_one('title').text
        titles[curr_node] = title

        # check for hidden spans
        hidden_spans = html.find_all('span')
        for span in hidden_spans:
            list_contents.append(span.text)

        # get list contents
        list_items = html.select('ul li')
        for list_item in list_items:
            list_contents.append(list_item.text)
        table_rows = html.select('tr')
        for table_row in table_rows:
            key = None
            for table_item in table_row.find_all('td'):
                if key:
                    treasures[key] = table_item.text
                    key = None
                else:
                    key = table_item.text

        # get anchor links
        anchor_links = html.select('a[href]')
        for link in anchor_links:
            link_url = urljoin(curr_node, link['href'])
            if 'maze' not in link_url or link_url in visited_nodes:
                continue
            edges.append((curr_node, link_url))
            stack.append(link_url)
    return edges, list_contents, titles, treasures


edges, list_items, titles, treasures = dfs('http://www.cs.loyola.edu/~isaacman/403/maze/')
print(list_items)
graph = nx.DiGraph()
graph.add_edges_from(edges)
graph = nx.relabel_nodes(graph, lambda node: f'{titles[node]}\n{node.replace("http://www.cs.loyola.edu/~isaacman/403/maze/", "")}')
color_map = []
start_node = None
end_node = None
for node in graph:
    if 'Treasure' in node:
        color_map.append('green')
        end_node = node
    elif 'Entrance' in node:
        color_map.append('blue')
        start_node = node
    else:
        color_map.append('white')
figure = plt.gcf()
figure.set_size_inches(10, 10)
nx.draw_networkx(graph, pos=nx.spring_layout(graph, k=.5), font_size=6, node_color=color_map)
ax = plt.gca()
ax.collections[0].set_edgecolor('black')
ax.collections[0].set_alpha(0.3)
plt.savefig('network.png')

# valid treasures
for list_item in list_items:
    if list_item in treasures:
        print("Found treasure: ", treasures[list_item])

# print shortest path
print('->'.join(nx.astar_path(graph, start_node, end_node)).replace('\n', ': '))
