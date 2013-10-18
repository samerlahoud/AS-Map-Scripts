# syntax: python script-cc-routing-report-v2.py 20120809-0800 LB
# preliminary:
# http://www.ripe.net/data-tools/stats/ris/ris-raw-data
# zcat bview.20120719.0800.gz | bgpdump -m - > routes.bview.20120719.0800
#!/usr/local/bin/python

# This version integrates HTML and google output => focus on HTML
import simplejson
import sys
import math
from collections import Counter
import HTML
import time
import math
import ipaddr
from pylab import *

date_input = sys.argv[1]
cc_input = sys.argv[2]
output_folder = './output/'
figure_folder = './output/figures/'
rel_figure_folder = './figures/'
data_folder = './data/' 

asn2cc_file = open(data_folder+'delegated-rir-latest-parsed', 'r')
ip2cc_file = open(data_folder+'delegated-rir-latest', 'r')
asn2name_file = open(data_folder+'autnums.txt', 'r')
routes_file=open(data_folder+'routes.tmp', 'r')
output_routing_report_file=open(output_folder+('routing-report-%s-%s.txt' %(cc_input, date_input)),'w')
html_file = open(output_folder+('routing-report-%s-%s.html' %(cc_input, date_input)), 'w')

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

# Get a list of IP address to country code conversion
ip2cc_list={}
for line in ip2cc_file:
	if line.startswith('#'):
		continue 
	w=line.split('|')
	if w[2] == 'ipv6':
		ip2cc_list[w[3]+'/'+w[4]] = w[1]
	if w[2] == 'ipv4':
		ip2cc_list[w[3]+'/'+str(int(math.log(int(w[4]),2)))] = w[1]

# Get a list of AS number to name conversions 
asn2name_list={}
for line in asn2name_file:
	if not line.startswith('AS'):
		continue 
	w=line.split()
	current_plain_asn = as_plain(w[0][2:])  
	asn2name_list[current_plain_asn] = w[1] 
asn2name_list['Other'] = 'Other'

matplotlib.rc('xtick', labelsize=11)
matplotlib.rcParams.update({'font.size': 12}) 

def plot_as_pie(labels, fracs, pie_title):
	figure(1, figsize=(8,8))
	#print labels, fracs
	labels = [asn2name_list[l] for l in labels]
	
	filter_fracs = [f for f in fracs  if f > 3]
	filter_labels= [labels[i] for i in range(0,len(labels)) if fracs[i] > 3]
	other_sum = sum([f for f in fracs  if f < 3])
	if other_sum:
		filter_fracs.append(other_sum)
		filter_labels.append('Other')
	pie(filter_fracs, labels=filter_labels, autopct='%.2f %%', pctdistance=0.75, labeldistance=1.04)
	title(pie_title)	
	fig_filename = pie_title.replace(' ','-') + ('-%s.png' %date_input) 
	savefig(figure_folder+fig_filename, format='png', transparent=False)
	close()
	return fig_filename

def network_in_rir(network_addr, prefix_list):
	for pref in prefix_list:
		if ipaddr.IPNetwork(network_addr) in ipaddr.IPNetwork(pref):
			return True
	return False		
		
# List of AS for CC
asn_list = [i for i in asn2cc_list if asn2cc_list[i] == cc_input]

# List of IP prefixes per CC
rir_prefix_list = [i for i in ip2cc_list if ip2cc_list[i] == cc_input]

# Dictionary with prefix lists indexed by ASNs
prefix_per_asn_dict = {}

# Dictionary of Upstream AS lists indexed by ASNs 
upstream_as_per_asn_dict = {}

# Dictionary of Upstream international AS lists indexed by ASNs 
international_as_per_asn_dict = {}

# List of international AS providers
global_international_as_list = []

for line in routes_file:
	if line.startswith('#'):
		continue 
	w=line.split('|')
	#if not(w[6]):
	#	break
	as_path = w[6].split(' ')
	origin_as = as_path[len(as_path)-1]
	
	for current_as in reversed(as_path):
		if current_as != origin_as:
			upstream_as = current_as
			break
					 	
	if origin_as in asn_list:
		if not(network_in_rir(w[5], rir_prefix_list)):
			#print origin_as, ipaddr.IPNetwork(w[5])
			continue
			
		if prefix_per_asn_dict.has_key(origin_as):
			if w[5] not in prefix_per_asn_dict[origin_as]:
				prefix_per_asn_dict[origin_as].append(w[5])
			upstream_as_per_asn_dict[origin_as].append(upstream_as)
			for current_as in reversed(as_path):
				if current_as not in asn_list:
					international_as_per_asn_dict[origin_as].append(current_as)
					global_international_as_list.append(current_as)
					break
		else: 
			prefix_per_asn_dict[origin_as] = [w[5]]
			upstream_as_per_asn_dict[origin_as]= [upstream_as]
			for current_as in reversed(as_path):
				if current_as not in asn_list:
					international_as_per_asn_dict[origin_as] = [current_as]
					global_international_as_list.append(current_as)
					break

global_international_as_counter = Counter(global_international_as_list)
total_nb_as_path = len(global_international_as_list)
total_country_nb_prefix = 0
for pref_list in prefix_per_asn_dict.values():
	total_country_nb_prefix = total_country_nb_prefix + len(pref_list)	

# Rounding the number of AS paths in global_international_as_counter
for as_name, as_path_nb in global_international_as_counter.items():
	global_international_as_counter[as_name] = float(as_path_nb)*100/total_nb_as_path

output_routing_report_file.write('### Routing report for %s based on RIS raw data %s\n### Samer Lahoud - July 2012\n' % (cc_input, date_input))
output_routing_report_file.write('\n### Summary routing report for %s\n' % cc_input)
output_routing_report_file.write('\n## Summary statistics\nTotal number of ASes: %s\nTotal number of prefixes: %s\nTotal number of AS paths: %s\n' %(len(asn_list), total_country_nb_prefix, total_nb_as_path)) 

#html_file.write('<h1>Routing report for Lebanon</h1>')
html_file.write('<h2>Global provider statistics</h2>')
html_file.write('<p>This report was last updated on %s based on RIS raw data %s</p>' %(time.strftime('%X %x %Z'), date_input))

htmlcode =  HTML.list(['Total number of ASes: %s' %len(asn_list), 'Total number of prefixes: %s' %total_country_nb_prefix, 'Total number of AS paths: %s' %total_nb_as_path])
html_file.write(htmlcode)

output_routing_report_file.write('\n## International transit provider distribution for %s\n' %cc_input)
all_transit_table = HTML.Table(header_row=['International transit provider', 'Percentage of AS paths'])

for all_global_inter_asn in global_international_as_counter.most_common():
	output_routing_report_file.write("%.2f %%\tvia\t AS%s\t%s\n" % (all_global_inter_asn[1], all_global_inter_asn[0], asn2name_list[all_global_inter_asn[0]]))
	all_transit_table.rows.append([asn2name_list[all_global_inter_asn[0]], "%.2f" %all_global_inter_asn[1]])

global_figname = plot_as_pie([elem[0] for elem in global_international_as_counter.most_common()], [elem[1] for elem in global_international_as_counter.most_common()], 'International transit provider distribution for %s' % cc_input)	

# html_file.write('<h4>Top 10 international transit providers</h4>')
# html_file.write('<img src=''%s'' alt="Top 10 international transit providers" width="450" height="450" />' %(rel_figure_folder+global_figname))
# htmlcode = str(top_transit_table)
# html_file.write(htmlcode)
#html_file.write('<h2>International transit provider distribution for %s</h2>' %cc_input)
htmlcode = str(all_transit_table)
html_file.write('<table><tr><td><img src=''%s'' alt="International transit providers" width="450" height="450" /></td><td>%s</td></tr></table>' %(rel_figure_folder+global_figname, htmlcode))

#html_file.write('<h2>Routing report for %s</h2>' % cc_input)
output_routing_report_file.write('\n### Detailed routing report for %s\n' %cc_input)

for asn, prefix_list in sorted(prefix_per_asn_dict.iteritems(), key=lambda (a,p): len(p), reverse=True):
	output_routing_report_file.write("\n## Routing for AS%s %s\n" % (asn, asn2name_list[asn]))	
	html_file.write("<h2>Routing for AS%s %s</h2>" % (asn, asn2name_list[asn]))	
	
	if international_as_per_asn_dict.has_key(asn):
		total_asn_nb_as_path = len(upstream_as_per_asn_dict[asn])
		
		output_routing_report_file.write("\n# List of %s routed prefix(es)\n%s\n" % (len(prefix_per_asn_dict[asn]), prefix_per_asn_dict[asn]))	
		html_file.write('<table><tr><td colspan="2"><p>List of %s routed prefix(es):\n<textarea>%s</textarea></p>\n<p>Total number of AS paths: %s</p></td></tr>' % (len(prefix_per_asn_dict[asn]), prefix_per_asn_dict[asn], total_asn_nb_as_path))
		
		up_count = Counter(upstream_as_per_asn_dict[asn])
		
		# Rounding the number of AS paths in up_count
		for as_name, as_path_nb in up_count.items():
			up_count[as_name] = float(as_path_nb)*100/total_asn_nb_as_path
	
		output_routing_report_file.write("\n# Direct upstream distribution\n") 
		#html_file.write("<h3>Provider distribution:</h3>") 
		direct_transit_table = HTML.Table(header_row=['Direct upstream AS', 'Percentage of AS paths'])
		
		up_count = sorted(up_count.iteritems(), key=lambda (a,p): p, reverse=True)
		
		for (up_asn, up_as_path_nb) in up_count:
			output_routing_report_file.write("%.2f %%\tvia AS%s\t%s\n" % (up_as_path_nb, up_asn, asn2name_list[up_asn]))
			direct_transit_table.rows.append([asn2name_list[up_asn], "%.2f" %up_as_path_nb])
		
		up_as_figname = plot_as_pie([elem[0] for elem in up_count], [elem[1] for elem in up_count], 'Direct upstream distribution for %s' %asn2name_list[asn])
		htmlcode = str(direct_transit_table)
		html_file.write('<tr><td><img src=''%s'' alt="Direct upstream distribution" width="400" height="400" /></td><td>%s</td></tr>' %(rel_figure_folder+up_as_figname, htmlcode))
		
		inter_count = Counter(international_as_per_asn_dict[asn])
		
		# Rounding the number of AS paths in inter_count
		for as_name, as_path_nb in inter_count.items():
			inter_count[as_name] = float(as_path_nb)*100/total_asn_nb_as_path
			
		output_routing_report_file.write("\n# International transit distribution:\n") 
		#html_file.write("<h3>International transit distribution:</h3>") 
		inter_transit_table = HTML.Table(header_row=['International transit provider', 'Percentage of AS paths'])
		
		inter_count = sorted(inter_count.iteritems(), key=lambda (a,p): p, reverse=True)
		
		for (inter_asn, inter_as_path_nb) in inter_count:
			output_routing_report_file.write("%.2f %%\tvia AS%s\t%s\n" % (inter_as_path_nb, inter_asn, asn2name_list[inter_asn]))
			inter_transit_table.rows.append([asn2name_list[inter_asn], "%.2f" %inter_as_path_nb])
		
		inter_as_figname = plot_as_pie([elem[0] for elem in inter_count], [elem[1] for elem in inter_count], 'International transit distribution for %s' %asn2name_list[asn])
		htmlcode = str(inter_transit_table)
		html_file.write('<tr><td><img src=''%s'' alt="International transit distribution" width="400" height="400" /></td><td>%s</td></tr></table>' %(rel_figure_folder+inter_as_figname, htmlcode))
 	
for asn in asn_list: 
	if not asn in prefix_per_asn_dict: 
		output_routing_report_file.write("\n## AS %s not visible in BGP tables\n" % asn) 
		html_file.write("<h2>AS %s not visible in BGP tables</h2>" % asn) 

html_file.close()