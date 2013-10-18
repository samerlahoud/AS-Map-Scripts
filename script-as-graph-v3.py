#!/usr/local/bin/python

import sys
import pydot

# syntaxe  python script-as-graph-v2.py FR

# using the peer cones from http://as-rank.caida.org/
## f = open('./data/as-rank.caida.peercones-with-IX.txt', 'r')
f = open('./data/asconn-ipv6-avril-2012-peercone.txt', 'r')

# using the as-rel from http://www.caida.org/data/active/as-relationships/index.xml
# f = open('./data/as-rel.20100120.a0.01000.txt', 'r')
# g = open('./output/as-rel-graph-'+sys.argv[1]+'.dot', 'w')

h = open('./data/as-name-nb-010911.txt', 'r')
g = open('./output/as-ipv6-peer-graph-'+sys.argv[1]+'.dot', 'w')
#k = open('./data/as-rank.caida.as-dump-info.txt', 'r')
k = open('./data/delegated-rir-latest-parsed', 'r')

as_graph = pydot.Dot(graph_type='digraph')

as_list=[]
for line in k:
    if line.startswith('#'):
        continue
    w = line.split('|')
    if w[3] == sys.argv[1]:
        as_list.append(w[0])

#as_list=['209']
#print as_list

def as_ntoa(as_num):
    ligne =[]
    h.seek(0)
    for ligne in h:
	if ligne.startswith('AS'+as_num):
            w=ligne.split()
            if w[1]:
                return w[1]
    return as_num

# Put Labels for nodes in as_list
for as_counter in as_list: 
	node = pydot.Node("AS %s" % as_counter+'\n'+as_ntoa(as_counter))
	as_graph.add_node(node)
	node.set('style', 'filled')
	node.set('fillcolor', '.7 .3 1.0')
	node.set('URL',"http://bgp.he.net/AS%s" % as_counter)

for line in f:
    if line.startswith('#'):
        continue
# using peer cones
    w=line.split('|')

# using as-rel
#      w=line.split(' ')    

    as_relation=w[2].rstrip('\n')
    if w[0] not in as_list and w[1] not in as_list:
        continue

    for i in [0,1]:
        if w[i] not in as_list:
			node = pydot.Node("AS %s" % as_ntoa(w[i]))
			as_graph.add_node(node)
			node.set('style', 'filled')
			node.set('shape', 'ellipse')
			node.set('fillcolor', '.4 .3 1.0')
			node.set('URL',"http://bgp.he.net/AS%s" % w[i])
            
# comment if you do not want AS-Names as node labels
#	g.write(w[0]+' [label="' + as_ntoa(w[0]) + '"]\n')

# using peer cones
    if as_relation == '-1': 

# using as-rel
#       if as_relation == '1':

        as_graph.add_edge(pydot.Edge(w[0], w[1]))
		
# comment if you do not want bidirectional arrows
#	if as_relation == '-1': 
#		g.write(w[0]+' -> '+w[1]+ '[arrowhead=dot]'+';\n')

# With B-IX
#    if as_relation == '0': 
#        g.write(w[0]+' -> '+w[1] + '[dir=none]'+';\n')
	as_graph.write_png('example1_graph.png')