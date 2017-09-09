# AS-Map-Scripts
Scripts for the daily report on the Internet routing in Lebanon

## Introduction
internettoday is a daily report on the Internet routing in Lebanon. 
Reports are based on freely available data taken from BGP routing tables at multiple vantage points in the world. 
Information available on internettoday includes:

- IPv4 and IPv6 autonomous system connectivity graphs
- IPv6 usage report
- BGP routing strategies report
- Sample reports

The following figure shows a graph of the IPv6 interconnection of Autonomous Systems (AS) in Lebanon. 
Orange rectangles represent ASes in Lebanon, such as national Internet service providers, and green ellipses represent international providers. 
Directed arrows represent the transit relationship between providers.

as-graph
The following table denotes the repartition of international transit providers for a lebanese AS, namely AS 24634. This repartition is obtained by computing the percentage of AS paths carrying prefixes for AS 24634 and transiting via each international provider.

International transit provider	Percentage of AS paths
LEVEL3	34.95
COGENT	31.07
GLOBEINTERNET	21.75
TELENOR-UK-LTD-AS	6.80
ASN-TBONE	3.11
PCH-AS	2.33

## Source code

All source code is made available for download. This work is distributed under the Creative Commons Attribution 2.5 License, which means that you are free to use and modify it for any purpose. Credits are welcome by including a link back to this website.
