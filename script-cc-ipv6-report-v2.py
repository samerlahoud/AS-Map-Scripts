# syntax: python script-cc-ipv6-report.py cc LB
#!/usr/local/bin/python
# This version generates an html file
import simplejson
import urllib
import sys
import math
import time
import HTML

cc_input = sys.argv[2]
localtime = time.localtime(time.time())
date_input = time.strftime("%Y%m%d", localtime)

output_folder = './output/'
data_folder = './data/' 

asn2cc_file = open(data_folder+'delegated-rir-latest-parsed', 'r')
asn2name_file = open(data_folder+'autnums.txt', 'r')
rir_file=open(data_folder+"delegated-rir-latest",'r')
# open an HTML output file
html_file = open(output_folder+('ipv6-report-%s-%s.html' %(cc_input, date_input)), 'w')
txt_report_file=open(output_folder+('ipv6-report-%s-%s.txt' %(cc_input, date_input)),'w')

# Get plain AS numbers for dotted notation
def as_plain(as_nb):
	if '.' in as_nb:
		as_dot_split=as_nb.split('.')
		as_nb_plain = int(as_dot_split[0])*65536 + int(as_dot_split[1])
		as_nb_plain = str(as_nb_plain)
	else: 
		as_nb_plain = as_nb
	return as_nb_plain

# Get a list of AS number to country code conversion
asn2cc_list={}
for line in asn2cc_file:
	if line.startswith('#'):
		continue 
	w=line.split('|')
	asn2cc_list[as_plain(w[0])] = w[3]

# Get a list of AS number to name conversions 
asn2name_list={}
for line in asn2name_file:
	if not line.startswith('AS'):
		continue 
	w=line.split()
	current_plain_asn = as_plain(w[0][2:])  
	asn2name_list[current_plain_asn] = w[1] 
	
# Get a list of allocated IPv6 prefixes for input cc
# Note that prefixes can be allocated to a CC but announced by an external AS
cc_allocated_ipv6_prefix_list=[]
for line in rir_file:
	if line.startswith('#'):
 		continue 
 	w=line.split('|')
 	if (w[1] == cc_input and w[2] == 'ipv6'):
 		cc_allocated_ipv6_prefix_list.append(w[3]+'/'+w[4])

# prefix_announce is not significative => then removed it
output_table = HTML.Table(header_row=['IPv6 prefix', 'RRC visibility', 'Total number of RRCs', 'Prefix AS number', 'Prefix holder', 'Prefix description'])
txt_report_file.write('###\nDetailed IPv6 report for %s\n###\n' % cc_input)
txt_report_file.write('%s\t%s\t%s\t%s\t%s\t%s\n' %('ipv6_prefix', 'visible_nb_RRC', 'total_nb_RRC', 'prefix_asn', 'prefix_holder', 'prefix_descr'))

# Get information about cc allocated IPv6 prefixes
cc_announced_prefix_nb = 0
for ipv6_prefix in cc_allocated_ipv6_prefix_list:
# Get an overview about IPv6 prefixes
	prefix_overview_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/plugin/prefix-overview/data.json?resource='+ipv6_prefix))
	prefix_holder = prefix_overview_json['data']['holder']
	prefix_asn = prefix_overview_json['data']['asn']
	prefix_related_prefixes = prefix_overview_json['data']['related_prefixes']
	if prefix_related_prefixes:
		print prefix_related_prefixes
	#prefix_announce = prefix_overview_json['data']['announced']
# Get information about address space description
	prefix_hierarchy_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/plugin/address-space-hierarchy/data.json?resource='+ipv6_prefix))
	if (prefix_hierarchy_json['data']['exact']):
		prefix_descr = prefix_hierarchy_json['data']['exact'][0]['descr']
	elif (prefix_hierarchy_json['data']['less_specific']):	
		prefix_descr = prefix_hierarchy_json['data']['less_specific'][0]['descr']
	elif (prefix_hierarchy_json['data']['more_specific']):	
		prefix_descr = prefix_hierarchy_json['data']['more_specific'][0]['descr']
		
#output_ipv6_report_file.write('\n'.join(cc_allocated_ipv6_prefix_list))

#Get the visibility of announced IPv6 prefixes
	visible_nb_RRC = 0
	total_nb_RRC = 0
	#if prefix_announce:
		#print ipv6_prefix
	prefix_visibility_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/plugin/visibility/data.json?resource='+ipv6_prefix))

	for i in range(len(prefix_visibility_json['data']['visibilities'])):
		total_nb_RRC = total_nb_RRC + int(prefix_visibility_json['data']['visibilities'][i]['ipv6_full_table_peer_count'])
		visible_nb_RRC = visible_nb_RRC + int(prefix_visibility_json['data']['visibilities'][i]['ipv6_full_table_peer_count']) - len(prefix_visibility_json['data']['visibilities'][i]['ipv6_full_table_peers_not_seeing'])
		
	#print ipv6_prefix, total_nb_RRC, visible_nb_RRC	
	output_table.rows.append([ipv6_prefix, str(visible_nb_RRC), total_nb_RRC, str(prefix_asn), str(prefix_holder), prefix_descr])
	txt_report_file.write('%s\t%s\t%s\t%s\t%s\t%s\n' %(ipv6_prefix, visible_nb_RRC, total_nb_RRC, prefix_asn, prefix_holder, prefix_descr))
 
	if visible_nb_RRC > 0:
		cc_announced_prefix_nb = cc_announced_prefix_nb +1

htmltable = str(output_table)
#html_file.write('<h1>IPv6 report</h1>')
html_file.write('<h2>Prefix statistics</h2>')
htmlcode =  HTML.list(['Total number of allocated prefixes: %s' %len(cc_allocated_ipv6_prefix_list), 'Number of announced prefixes: %s' %cc_announced_prefix_nb])
html_file.write(htmlcode)
html_file.write('<h2>Allocation and visibility report</h2>')
html_file.write('<p>This report was last updated on %s</p>' %time.strftime('%X %x %Z'))	
html_file.write(htmltable)

html_file.close()	

txt_report_file.write('###\nSummary IPv6 report for %s\n###\n' % cc_input)
txt_report_file.write('%s\t%s\t%s\n' %('Country Code', 'Total Number of Allocated Prefixes', 'Number of Announced Prefixes'))
txt_report_file.write('%s\t%s\t%s\n' %(cc_input, len(cc_allocated_ipv6_prefix_list), cc_announced_prefix_nb))