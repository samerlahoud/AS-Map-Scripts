#/bin/sh

current_date=$(date +%Y%m%d)
#current_date=20130416
def_hour=0800

base_dir='/Users/simurgh/Documents/IRISA/Simulations/Internet-Graph/AS-Map-Scripts'

cd $base_dir/data

wget ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest -O delegated-afrinic-latest
wget ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest -O delegated-apnic-latest
wget ftp://ftp.arin.net/pub/stats/arin/delegated-arin-latest -O delegated-arin-latest
wget ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest -O delegated-lacnic-latest
#wget ftp://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-latest -O delegated-ripencc-latest
wget http://ftp.apnic.net/stats/ripe-ncc/delegated-ripencc-latest -O delegated-ripencc-latest 

cat delegated-afrinic-latest delegated-apnic-latest delegated-arin-latest delegated-lacnic-latest delegated-ripencc-latest > delegated-rir-latest 
python parse-rir-delegations.py

wget -4 http://bgp.potaroo.net/as2.0/asconn.txt -O asconn-v4-as2.0.txt
wget -4 http://bgp.potaroo.net/as6447/asconn.txt -O asconn-v4-as6447.txt

wget -4 http://bgp.potaroo.net/v6/as2.0/asconn.txt -O asconn-v6-as2.0.txt
wget -4 http://bgp.potaroo.net/v6/as6447/asconn.txt -O asconn-v6-as6447.txt

cat asconn-v4-as2.0.txt asconn-v4-as6447.txt > asconn-v4-$current_date.txt
cat asconn-v6-as2.0.txt asconn-v6-as6447.txt > asconn-v6-$current_date.txt

python parse-asconn-undir.py asconn-v4-$current_date.txt
python parse-asconn-undir.py asconn-v6-$current_date.txt

cd $base_dir
python script-as-graph-v4.py ip 4 cc FR date $current_date
python script-as-graph-v4.py ip 6 cc FR date $current_date

cd $base_dir/data
#wget http://data.ris.ripe.net/rrc00/$(date +%Y.%m)/bview.$current_date.$def_hour.gz -O bview.tmp
wget http://data.ris.ripe.net/rrc00/latest-bview.gz -O bview00.tmp
wget http://data.ris.ripe.net/rrc03/latest-bview.gz -O bview03.tmp
wget http://data.ris.ripe.net/rrc06/latest-bview.gz -O bview06.tmp
wget http://data.ris.ripe.net/rrc11/latest-bview.gz -O bview11.tmp

cat bview00.tmp bview03.tmp bview06.tmp bview11.tmp > bview.tmp
# watch for the zcat bug on OSX http://od-eon.com/blogs/calvin/zcat-bug-mac-osx/
zcat bview.tmp | bgpdump -m - > routes.tmp
 
cd $base_dir
python script-cc-routing-report-v8.py $current_date.$def_hour FR

# cd $base_dir/data
# rm routes.tmp
# rm bview.tmp

cd $base_dir
python script-cc-ipv6-report-v3.py cc FR
