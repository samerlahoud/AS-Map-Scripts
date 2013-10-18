#### This is a first draft of the IPv6 report per cc in script-cc-ipv6-report.py

#!/usr/local/bin/python

import simplejson
import urllib
import sys
import math

asn_input = sys.argv[1]

asn2cc_file = open('./data/delegated-rir-latest-parsed', 'r')
rir_file=open("./data/delegated-rir-latest",'r')
output_as_info_file=open('./output/as-info-'+asn_input+'.txt','w')

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
	
# Get a list of allocated prefixes for input cc
cc_allocated_ipv4_prefix_list=[]
cc_allocated_ipv6_prefix_list=[]
cc_input = asn2cc_list[asn_input] 
for line in rir_file:
	if line.startswith('#'):
 		continue 
 	w=line.split('|')
 	if (w[1] == cc_input and w[2] == 'ipv6'):
 		cc_allocated_ipv6_prefix_list.append(w[3]+'/'+w[4]) 
 	if (w[1] == cc_input and w[2] == 'ipv4'):
 		cc_allocated_ipv4_prefix_list.append(w[3]+'/'+str(32-int(math.log(int(w[4]),2)))) 

output_as_info_file.write(str(len(cc_allocated_ipv4_prefix_list))+' allocated IPv4 prefixes for %s:\n' % cc_input)
output_as_info_file.write('\n'.join(cc_allocated_ipv4_prefix_list))

output_as_info_file.write('\n'+str(len(cc_allocated_ipv6_prefix_list))+' allocated IPv6 prefixes for %s:\n' % cc_input)
output_as_info_file.write('\n'.join(cc_allocated_ipv6_prefix_list))

# Get the number of announced prefixes
nb_ipv4_prefixes = 0
nb_ipv6_prefixes = 0
prefix_size_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/plugin/prefix-size-distribution/data.json?resource='+asn_input))

for i in range(len(prefix_size_json['data']['ipv4'])):
	nb_ipv4_prefixes = nb_ipv4_prefixes + prefix_size_json['data']['ipv4'][i]['count']
	
for i in range(len(prefix_size_json['data']['ipv6'])):
	nb_ipv6_prefixes = nb_ipv6_prefixes + prefix_size_json['data']['ipv6'][i]['count']

# Get a list of announced prefixes
announced_ipv4_prefixes=[]
announced_ipv6_prefixes=[]
announced_prefixes_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/plugin/as-routing-consistency/data.json?resource='+asn_input))

for i in range(len(announced_prefixes_json['data']['prefixes'])):
	if ':' in announced_prefixes_json['data']['prefixes'][i]['prefix']:
		announced_ipv6_prefixes.append(announced_prefixes_json['data']['prefixes'][i]['prefix'])
	else:
	 	announced_ipv4_prefixes.append(announced_prefixes_json['data']['prefixes'][i]['prefix'])
	if announced_prefixes_json['data']['prefixes'][i]['in_bgp'] and not announced_prefixes_json['data']['prefixes'][i]['in_whois']:
		print 'prefix', announced_prefixes_json['data']['prefixes'][i]['prefix'], 'has no whois information'
	if announced_prefixes_json['data']['prefixes'][i]['in_whois'] and not announced_prefixes_json['data']['prefixes'][i]['in_bgp']:
		print 'prefix', announced_prefixes_json['data']['prefixes'][i]['prefix'], 'is not announced in bgp'

output_as_info_file.write('\n'+str(len(announced_ipv4_prefixes))+' Announced IPv4 prefixes for %s:\n' % asn_input)
output_as_info_file.write('\n'.join(announced_ipv4_prefixes))

output_as_info_file.write('\n'+str(len(announced_ipv6_prefixes))+' Announced IPv6 prefixes for %s:\n' % asn_input)
output_as_info_file.write('\n'.join(announced_ipv6_prefixes))
						
# Get the visibility of announced IPv6 prefixes
for ipv6_prefix in announced_ipv6_prefixes:
	visible_nb_RRC = 0
	prefix_visibility_json = simplejson.load(urllib.urlopen('https://stat.ripe.net/plugin/visibility/data.json?resource='+ipv6_prefix))
	total_nb_RRC = len(prefix_visibility_json['data'])
	for i in range(len(prefix_visibility_json['data'])):
		if prefix_visibility_json['data'][i]['path']:
			visible_nb_RRC = visible_nb_RRC + 1
	print visible_nb_RRC, total_nb_RRC