### Samer Lahoud www.lahoud.fr

# syntax: python script-cc-ipv6-report.py cc LB
#!/usr/local/bin/python
# This version generates an html file
import simplejson
import urllib
import sys
import math
import time
import HTML
from countryinfo import countries

# get country code
cc_input = sys.argv[2]
country_name=[country['name'] for country in countries if country['code']==cc_input][0]
localtime = time.localtime(time.time())
date_input = time.strftime("%Y%m%d", localtime)

# set input and output folders
output_folder = './output/'
data_folder = './data/' 
rel_figure_folder = './figures/'

# open data files
asn2cc_file = open(data_folder+'delegated-rir-latest-parsed', 'r')
asn2name_file = open(data_folder+'autnums.txt', 'r')
rir_file=open(data_folder+"delegated-rir-latest",'r')

# open HTML and txt output files
html_file = open(output_folder+('ipv6-report-%s-%s.html' %(cc_input, date_input)), 'w')
txt_report_file=open(output_folder+('ipv6-report-%s-%s.txt' %(cc_input, date_input)),'w')

# get plain AS numbers for dotted notation
def as_plain(as_nb):
	if '.' in as_nb:
		as_dot_split=as_nb.split('.')
		as_nb_plain = int(as_dot_split[0])*65536 + int(as_dot_split[1])
		as_nb_plain = str(as_nb_plain)
	else: 
		as_nb_plain = as_nb
	return as_nb_plain

# get a list of AS number to country code conversion
asn2cc_list={}
for line in asn2cc_file:
	if line.startswith('#'):
		continue 
	w=line.split('|')
	asn2cc_list[as_plain(w[0])] = w[3]

# get a list of AS number to name conversions 
asn2name_list={}
for line in asn2name_file:
	if not line.startswith('AS'):
		continue 
	w=line.split()
	current_plain_asn = as_plain(w[0][2:])  
	asn2name_list[current_plain_asn] = w[1] 
	
# get a list of allocated IPv6 prefixes for country code
# note that prefixes can be allocated to a cc but announced by an external AS
cc_allocated_ipv6_prefix_list=[]
for line in rir_file:
	if line.startswith('#'):
 		continue 
 	w=line.split('|')
 	if (w[1] == cc_input and w[2] == 'ipv6'):
 		cc_allocated_ipv6_prefix_list.append(w[3]+'/'+w[4])

# set allocation type as RIR in the corresponding dictionary
prefix_allocation_type = {prefix:'RIR' for prefix in cc_allocated_ipv6_prefix_list}

# initialise headers for html and txt outputs
output_table = HTML.Table(header_row=['Status','IPv6 prefix', 'Allocation','RRC visibility', 'Prefix AS number', 'First seen', 'Last seen', 'Prefix holder', 'Prefix description'])
txt_report_file.write('###\nDetailed IPv6 report for %s\n###\n' % cc_input)
txt_report_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %('ipv6_prefix', 'allocation', 'RRC_visibility', 'prefix_asn', 'first_seen', 'last_seen', 'prefix_holder', 'prefix_descr'))

# get information about cc allocated IPv6 prefixes
cc_announced_prefix_nb = 0
for ipv6_prefix in cc_allocated_ipv6_prefix_list:
	# verify if more specific prefixes are known 
	prefix_hierarchy_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/plugin/address-space-hierarchy/data.json?resource='+ipv6_prefix))
	if (prefix_hierarchy_json['data']['more_specific']):	
		# for each more specific prefix add it to the list of allocated prefixes per cc and set its type accordingly
		for i in range(len(prefix_hierarchy_json['data']['more_specific'])):
			added_prefix = prefix_hierarchy_json['data']['more_specific'][i]['inet6num']
			cc_allocated_ipv6_prefix_list.append(added_prefix)
			prefix_allocation_type[added_prefix] = 'More specific'
	
	# get prefix holder and announcing AS number
	prefix_overview_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/plugin/prefix-overview/data.json?resource='+ipv6_prefix))
	if (prefix_overview_json['data']['asns']):
		prefix_holder = prefix_overview_json['data']['asns'][0]['holder']
		prefix_asn = prefix_overview_json['data']['asns'][0]['asn']
	
	# get prefix description
	if (prefix_hierarchy_json['data']['exact']):
		prefix_descr = prefix_hierarchy_json['data']['exact'][0]['descr']

	# routing-status and visibility widgets are not working properly => get a mix of both
	visibility_seen_nb_RRC = 0
	visibility_total_nb_RRC = 0
	
	# routing-status extraction
	prefix_routing_status_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/data/routing-status/data.json?resource='+ipv6_prefix))
	routing_status_seen_nb_RRC = prefix_routing_status_json['data']['visibility']['v6']['ris_peers_seeing']
 	routing_status_total_nb_RRC = prefix_routing_status_json['data']['visibility']['v6']['total_ris_peers']
	
	# visibility extraction
	# Commented for RIPE unavailability
	# prefix_visibility_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/data/visibility/data.json?resource='+ipv6_prefix)) 
# 	for i in range(len(prefix_visibility_json['data']['visibilities'])):
# 		visibility_total_nb_RRC = visibility_total_nb_RRC + int(prefix_visibility_json['data']['visibilities'][i]['ipv6_full_table_peer_count'])
# 		visibility_seen_nb_RRC = visibility_seen_nb_RRC + int(prefix_visibility_json['data']['visibilities'][i]['ipv6_full_table_peer_count']) - len(prefix_visibility_json['data']['visibilities'][i]['ipv6_full_table_peers_not_seeing'])
		
	
	# looking-glass extraction => too slow !
	# prefix_looking_glass_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/data/looking-glass/data.json?resource='+ipv6_prefix))
 	# for RRC_key in prefix_looking_glass_json['data']['rrcs'].keys():
 	#	looking_glass_seen_nb_RRC = visible_nb_RRC + len(prefix_looking_glass_json['data']['rrcs'][RRC_key]['entries'])
	
	# get the best of routing-status and visibility widgets 
	if routing_status_seen_nb_RRC > visibility_seen_nb_RRC:
		seen_nb_RRC = routing_status_seen_nb_RRC
		total_nb_RRC = routing_status_total_nb_RRC
	else:
		seen_nb_RRC = visibility_seen_nb_RRC
		total_nb_RRC = visibility_total_nb_RRC
	
	# put RRC visibility in a readable format	
	RRC_visibility = str(seen_nb_RRC) + '/' + str(total_nb_RRC)
	
	# get first and last seen dates
	if prefix_routing_status_json['data']['first_seen']:
		first_seen_time = prefix_routing_status_json['data']['first_seen']['time'].replace('T', ' at ') 
	else: 
		first_seen_time = None
	if prefix_routing_status_json['data']['last_seen']:
		last_seen_time = prefix_routing_status_json['data']['last_seen']['time'].replace('T', ' at ') 
	else: 
		last_seen_time = None
	
	# set a nice graphic status for prefix visibility
	if int(seen_nb_RRC) == 0: 
		prefix_status = '<img src=%s alt="NOK"/>' %(rel_figure_folder+'nok_icon.png')
	elif int(seen_nb_RRC) == int(total_nb_RRC): 
		prefix_status = '<img src=%s alt="OK"/>' %(rel_figure_folder+'ok_icon.png')
	else: 
		prefix_status = '<img src=%s alt="MID_OK"/>' %(rel_figure_folder+'mid_ok_icon.png')

	# put everything in a table row in the output files
	output_table.rows.append([prefix_status, ipv6_prefix, prefix_allocation_type[ipv6_prefix], RRC_visibility, str(prefix_asn), first_seen_time, last_seen_time, str(prefix_holder), prefix_descr])
	txt_report_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %(ipv6_prefix, prefix_allocation_type[ipv6_prefix], RRC_visibility, prefix_asn, first_seen_time, last_seen_time, prefix_holder, prefix_descr))
 
	if seen_nb_RRC > 0:
		cc_announced_prefix_nb = cc_announced_prefix_nb +1

# put global statistics and insert html headers
htmltable = str(output_table)
#html_file.write('<h1>IPv6 report for %s</h1>' %country_name)
html_file.write('<h2>Prefix statistics</h2>')
htmlcode =  HTML.list(['Total number of allocated prefixes: %s' %len(cc_allocated_ipv6_prefix_list), 'Number of announced prefixes: %s' %cc_announced_prefix_nb])
html_file.write(htmlcode)
html_file.write('<h2>Allocation and visibility report</h2>')
html_file.write('<p>This report was last updated on %s</p>' %time.strftime('%X %x %Z'))	
html_file.write(htmltable)
html_file.close()

# put global statistics in txt file
txt_report_file.write('###\nSummary IPv6 report for %s\n###\n' % cc_input)
txt_report_file.write('%s\t%s\t%s\n' %('Country Code', 'Total Number of Allocated Prefixes', 'Number of Announced Prefixes'))
txt_report_file.write('%s\t%s\t%s\n' %(cc_input, len(cc_allocated_ipv6_prefix_list), cc_announced_prefix_nb))