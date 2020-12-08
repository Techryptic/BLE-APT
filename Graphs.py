import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly,re,sys,time,statistics,csv,xlwt,argparse
import plotly.graph_objects as go
from statistics import median
from collections import Counter

def PreqGraph(input):
	ML = 0 # 0 = off, 1 = on

	######################### 
	df = pd.read_csv(input,delimiter="*")
	df = df.fillna('')

	G = nx.Graph()
	for i, row in df.iterrows():
		adva = str(row['AdvA'])
		inita = str(row['InitA'])
		scana = str(row['ScanA'])

		if adva != '':
			G.add_node(adva)
		
		if inita != '':
			G.add_node(inita)
			G.add_edge(inita, adva)
			G.add_edge(adva, inita)

		if scana != '':
			G.add_node(scana)
			G.add_edge(scana, adva)
			G.add_edge(adva, scana)

	Unique2 = (G.nodes()) # Unique
	Edges2 = (G.edges()) # Split 


	#########################
	# Transactions
	al = df["AdvA"].tolist()
	sal = [item.strip() for item in al]
	il = df["InitA"].tolist()
	sil = [item.strip() for item in il]
	sl = df["ScanA"].tolist()
	ssl = [item.strip() for item in sl]

	rssi = df["rssi"].tolist()

	pdu = df["pdu_type"].tolist()
	pdu_type = [item.strip() for item in pdu]

	man = df["Manufacturer"].tolist()
	manufacturer = [item.strip() for item in man]

	ln = df["local_name"].tolist()
	local_name = [item.strip() for item in ln]

	if ML:
		ln_ml = df["local_name_ml"].tolist()
		local_name = [item.strip() for item in ln_ml]
		al_ml = df["AdvA_ml"].tolist()
		sal = [item.strip() for item in al_ml]
		il_ml = df["InitA_ml"].tolist()
		sil = [item.strip() for item in il_ml]
		sl_ml = df["ScanA_ml"].tolist()
		ssl = [item.strip() for item in sl_ml]

	fl = sal+sil+ssl
	fl = [x.strip() for x in fl if x.strip()] # Be gone dups
	fl = list(dict.fromkeys(fl))
	################################
	# Order of Operations
	edges = [] #pair
	for p, i in enumerate(sal):
		if sil[p]:
			edges.append("{}*{}".format(i,sil[p]))
		if ssl[p]:
			edges.append("{}*{}".format(i,ssl[p]))

	nodes = [] #straight down
	for p, i in enumerate(edges):
		i1 = i.split("*")[0]
		i2 = i.split("*")[1]
		if i1 not in nodes:
			nodes.append(i1)
		if i2 not in nodes:
			nodes.append(i2)

	occurrences = fl.count("a")

	ayo = []
	ayo.append("TransactionAmt*Source*Target")
	for x in edges:
		occurrences = edges.count(x)
		a = "{}*{}".format(occurrences,x)
		if a not in ayo:
			ayo.append(a)

	out_edge = "graph-Edges.csv"
	f = open(out_edge, "w")
	for i in ayo:
		f.write("{}\n".format(i))
	print("Output Written to: {}...".format(out_edge))


	#########################
	# Nodes
	u=[]
	u.append("Mac*Rssi*PDU*Manufacturer*Local_Name")
	for f in nodes:
		lines=[]
		rssi_list=[]
		pdu_type_list=[]
		pdu_type_list2=[]
		Manufacturer_list=[]
		local_name_list=[]

		if len(f) < 5:
			continue
		for p, i in enumerate(sal):
			if f.strip() == i:
				lines.append(p)
		for p, i in enumerate(sil):
			if f.strip() == i:
				lines.append(p)
		for p, i in enumerate(ssl):
			if f.strip() == i:
				lines.append(p)

		lines = list(dict.fromkeys(lines))

		for x in lines:
			rssi_list.append(rssi[x])
			pdu_type_list.append(pdu_type[x])
			Manufacturer_list.append(manufacturer[x])
			local_name_list.append(local_name[x])
		
		rssi_median = median(rssi_list)

		ca = Counter(pdu_type_list)
		pdu_type_list = ca.most_common(len(pdu_type_list))
		for i in pdu_type_list:
			p = "{}:{}".format(i[0],i[1])
			pdu_type_list2.append(p)
		pdu_type_list2 = (', '.join(pdu_type_list2))

		Manufacturer_list = list(dict.fromkeys(Manufacturer_list))
		Manufacturer_list =[x for x in Manufacturer_list if x]
		Manufacturer_list = (', '.join(Manufacturer_list))

		local_name_list = list(dict.fromkeys(local_name_list))
		local_name_list =[x for x in local_name_list if x]
		local_name_list = (', '.join(local_name_list))

		all = "{}*{}*{}*{}*{}".format(f,rssi_median,pdu_type_list2,Manufacturer_list,local_name_list) 
		u.append(all)
	out_nodes = "graph-Nodes.csv"
	f = open(out_nodes, "w")
	for i in u:
		f.write("{}\n".format(i))
	print("Output Written to: {}...".format(out_nodes))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str,
                    help=" -> input file")
    #parser.add_argument("output", type=str,
    #                    help=" -> output file name")
    args = parser.parse_args()
    input=args.input
    #output=args.output
    print("Reading file: {}...".format(input))
    PreqGraph(input)
    #print("Output Written to: {}...".format(output))
