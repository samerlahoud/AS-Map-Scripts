#!/usr/local/bin/python
# python script-as-graph-v4.py ip 4 cc FR date 20120823
import sys
import networkx as nx
import pydot
from collections import defaultdict
import HTML
import time

ip_input = sys.argv[2] 
cc_input = sys.argv[4]
date_input = sys.argv[6]
output_folder = './output/'
figure_folder = './output/figures/'
rel_figure_folder = './figures/'
data_folder = './data/'

# http://bgp.potaroo.net/v6/as6447/asconn.txt ou http://bgp.potaroo.net/as6447/asconn.txt
# peercone files are geenrated for asconn by parse-asconn-undir and give only c2p relations

if ip_input == '6':
	as_relation_file = open(data_folder+'peercone-asconn-v6-'+date_input+'.txt', 'r')
if ip_input == '4':
	as_relation_file = open(data_folder+'peercone-asconn-v4-'+date_input+'.txt', 'r')

asn2name_file = open(data_folder+'autnums.txt', 'r')
output_dot_filename = 'as-graph-ipv%s-%s-%s.dot' %(ip_input, cc_input, date_input)
output_png_filename = 'as-graph-ipv%s-%s-%s.png' %(ip_input, cc_input, date_input)
asn2cc_file = open(data_folder+'delegated-rir-latest-parsed', 'r')
#rir_file=open("./data/delegated-rir-latest",'r')
html_file = open(output_folder+('as-graph-ipv%s-%s-%s.html' %(ip_input, cc_input, date_input)), 'w')

as_graph = nx.DiGraph()
as_pydot_graph = pydot.Dot(graph_type='digraph')
as_dot_cluster =pydot.Cluster(sys.argv[4],label=sys.argv[4])

# Get plain AS numbers for dotted notation
def as_plain(as_nb):
	if '.' in as_nb:
		as_dot_split=as_nb.split('.')
		as_nb_plain = int(as_dot_split[0])*65536 + int(as_dot_split[1])
		as_nb_plain = str(as_nb_plain)
	else: 
		as_nb_plain = as_nb
	return as_nb_plain

# Get a list of AS number to name conversions 
asn2name_list={}
for line in asn2name_file:
	if not line.startswith('AS'):
		continue 
	w=line.split()
	current_plain_asn = as_plain(w[0][2:])  
	asn2name_list[current_plain_asn] = w[1] 

# Get a list of AS number to country code conversion
asn2cc_list={}
for line in asn2cc_file:
	if line.startswith('#'):
		continue 
	w=line.split('|')
	asn2cc_list[as_plain(w[0])] = w[3] 

## Get a list of allocated  prefixes for all cc
# asn2prefix_list=defaultdict(list)
# for line in rir_file:
# 	if line.startswith('#'):
# 		continue 
# 	w=line.split('|')
# 	if ip_input == '6':
# 		if (w[2] == 'ipv6' and w[1] != '*'):
# 			asn2prefix_list[as_plain(w[4])].append(w[3]) 
# 	if ip_input == '4':
# 		if (w[2] == 'ipv4' and w[1] != '*'):
# 			asn2prefix_list[as_plain(w[4])].append(w[3]) 
#print asn2prefix_list 			

# Add nodes and edges to graph
for line in as_relation_file:
     if line.startswith('#'):
         continue
     w = line.split('|')
     
     if as_plain(w[0]) in asn2name_list:
     	asname1 = asn2name_list[as_plain(w[0])]
     else: 
     	asname1 = 'noname'
     
     if as_plain(w[1]) in asn2name_list:
     	asname2 = asn2name_list[as_plain(w[1])]
     else:
     	asname2 = 'noname'
     	
     if as_plain(w[0]) in asn2cc_list:
     	ascc1 = asn2cc_list[as_plain(w[0])]
     else: 
     	ascc1 = 'nocc'
     
     if as_plain(w[1]) in asn2cc_list:
     	ascc2 = asn2cc_list[as_plain(w[1])]
     else:
     	ascc2 = 'nocc'
     
     as_graph.add_node(as_plain(w[0]), as_name=asname1, as_cc=ascc1)
     as_graph.add_node(as_plain(w[1]), as_name=asname2, as_cc=ascc2)
     # customer to provider edge
     as_graph.add_edge(as_plain(w[1]), as_plain(w[0]), as_rel=w[2].rstrip())

# ecosystem AS list
eco_as_list=[]
for n in as_graph: 
  	if as_graph.node[n]['as_cc'] == cc_input:
  		if n not in eco_as_list:
 			eco_as_list.append(n)
 		for as_neighbor_counter in as_graph.successors(n): 				
 			if (as_neighbor_counter not in eco_as_list):
 				eco_as_list.append(as_neighbor_counter)
 		for as_neighbor_counter in as_graph.predecessors(n): 				
 			if (as_neighbor_counter not in eco_as_list):
 				eco_as_list.append(as_neighbor_counter)

# Filtered Graph corresponding to the AS ecosystem
filtered_graph = as_graph.subgraph(eco_as_list)

# Remove edges between external ASes
for e in filtered_graph.edges():
 	if not (filtered_graph.node[e[0]]['as_cc'] == cc_input or filtered_graph.node[e[1]]['as_cc'] == cc_input):
 		filtered_graph.remove_edge(e[0],e[1])

# Transform graph to pydot for pretty drawing
as_pydot_graph=nx.to_pydot(filtered_graph)

for current_node in as_pydot_graph.get_nodes():
	#print current_node.get('as_cc')
	if current_node.get('as_cc') == cc_input:
		current_node.set('style', 'filled')
		current_node.set('shape', 'box')
		#current_node.set('fillcolor', '.7 .3 1.0')
		current_node.set('fillcolor', 'orange')
		current_node.set('URL',"http://bgp.he.net/AS%s" % current_node.get_name())
		current_node.set('label','AS %s' % current_node.get_name()+'\n'+current_node.get('as_name'))
		as_dot_cluster.add_node(current_node)
	else:
		current_node.set('style', 'filled')
		current_node.set('shape', 'ellipse')
		#current_node.set('fillcolor', '.4 .3 1.0')
		current_node.set('fillcolor', 'green')
		current_node.set('URL',"http://bgp.he.net/AS%s" % current_node.get_name())
		current_node.set('label','AS %s' % current_node.get_name()+'\n'+current_node.get('as_name'))

as_pydot_graph.add_subgraph(as_dot_cluster)		
as_pydot_graph.write_dot(figure_folder+output_dot_filename)
as_pydot_graph.write_png(figure_folder+output_png_filename)
#html_file.write('<h1>IPv%s AS graph</h1>\n' %ip_input)
html_file.write('<h2>Graph statistics</h2>\n')
htmlcode =  HTML.list(['Number of nodes: %s' %filtered_graph.number_of_nodes(), 'Number of edges: %s' %filtered_graph.size()])
html_file.write(htmlcode)
html_file.write('<h2>IPv%s AS graph</h2>\n' %ip_input)
html_file.write('<p>This graph was last updated on %s based on RIS raw data %s</p>\n' %(time.strftime('%X %x %Z'), date_input))
html_file.write('<img src=''%s'' alt="IPv%s AS graph" width="90%%" class="center" />' %(rel_figure_folder+output_png_filename, ip_input))
html_file.close()
