import csv,time,re,fileinput,argparse
from fuzzywuzzy import process, fuzz
from collections import Counter
import pandas as pd


def MachineLearning(input,output):
	PerR = 75 # Percent Ratio
	MLNL = 10 # Minimun local_name length
	MC = 4 # Number of Minimum Count to loop by. 4 means 5 and above.
	MC2 = 3 # Number of Minimum Count to loop by. 4 means 5 and above.
	df = pd.read_csv(input,delimiter="*")
	df = df.fillna('')

	adva_list = df["AdvA"].tolist()
	strip_list = [item.strip() for item in adva_list]
	items = Counter(strip_list).keys()
	words_to_count = (word for word in strip_list if word[:1])
	ca = Counter(words_to_count)
	all_list = ca.most_common(len(items))


	scana_list = df["ScanA"].tolist()
	strip_list2 = [item.strip() for item in scana_list]
	items2 = Counter(strip_list2).keys()
	words_to_count2 = (word2 for word2 in strip_list2 if word2[:1])
	ca2 = Counter(words_to_count2)
	all_list2 = ca2.most_common(len(items2))

	local_name_list = df["local_name"].tolist()
	strip_list3 = [item.strip() for item in local_name_list]
	items3 = Counter(strip_list3).keys()
	words_to_count3 = (word3 for word3 in strip_list3 if word3[:1])
	ca3 = Counter(words_to_count3)
	all_list3 = ca3.most_common(len(items3))

	l = []
	s = []
	for i in all_list:
		if i[1] > MC:
			l.append(i)
		else:
			s.append(i)
	l.reverse()
	l2 = []
	s2 = []
	for i in all_list2:
		if i[1] > MC2:
			l2.append(i)
		else:
			s2.append(i)
	l2.reverse()
	l3 = []
	s3 = []
	for i in all_list3:
		if i[1] > MC2:
			l3.append(i)
		else:
			s3.append(i)
	l3.reverse()
	rep = []
	new_l = []
	for i in l:
		a = process.extract(i[0], l, limit=2)
		if a[1][1] > PerR:
			top_current = (a[0][0][1])
			top_check = (a[1][0][1])
			if top_current <= top_check:
				chge = ("{}*{}".format(a[0][0][0],a[1][0][0]))
				rep.append(chge)
				new_l.append(a[1][0])
			else:
				new_l.append(a[0][0])
		else:
			new_l.append(a[0][0])
	rep2 = []
	new_l2 = []
	if len(l2) > 10:
		for i in l2:
			a2 = process.extract(i[0], l2, limit=2)
			if a2[1][1] > PerR:
				top_current2 = (a2[0][0][1])
				top_check2 = (a2[1][0][1])
				if top_current2 <= top_check2:
					chge2 = ("{}*{}".format(a2[0][0][0],a2[1][0][0]))
					rep2.append(chge2)
					new_l2.append(a2[1][0])
				else:
					new_l2.append(a2[0][0])
			else:
				new_l2.append(a2[0][0])

	###############################################################
	for i in s:
		if i in new_l:
			print("Usually there won't be anything here")
	for i in s2:
		if i in new_l2:
			print("Usually there won't be anything here")

	for i in s:
		a = process.extract(i[0], new_l, limit=2)
		if a[1][1] > PerR:
			top_current = (i[1])
			top_check = (a[1][0][1])
			if top_current <= top_check:
				chgea = ("{}*{}".format(i[0],a[0][0][0]))
				rep.append(chgea)

	if len(s2) > 10:
		if len(new_l2) > 2:
			for i in s2:
				a2 = process.extract(i[0], new_l2, limit=2)
				if a2[1][1] > PerR:
					top_current2 = (i[1])
					top_check2 = (a2[1][0][1])
					if top_current2 <= top_check2:
						chge2b = ("{}*{}".format(i[0],a2[0][0][0]))
						rep2.append(chge2b)


	cleanlist = (list(dict.fromkeys(strip_list3)))
	skip_over = []
	rep3 = []
	tc = []
	for i in cleanlist:
		if i in skip_over:
			continue
		for x in cleanlist:
			local_name_ratio = fuzz.ratio(i, x)
			if local_name_ratio > PerR:
				toChange = ("{}*{}".format(x,i))
				skip_over.append(x)
				rep3.append(toChange)
				tc.append(i)

	rep3b = []
	tc = (list(dict.fromkeys(tc)))
	for i in rep3:
		i = i.split("*")[0]
		a3 = process.extract(i, tc, limit=3)
		if a3[1][1] > PerR:
			try:
				top_current3 = (i[1])
				top_check3 = (a3[1][0][1])

				if top_current3 <= top_check3:
					chge2c = ("{}*{}".format(i,a3[0][0]))
					rep3b.append(chge2c)
			except:
				pass

	rep = (list(dict.fromkeys(rep))) # Possible dups, very rare. AdvA
	rep2 = (list(dict.fromkeys(rep2))) # Possible dups, very rare. ScanA
	rep3 = (list(dict.fromkeys(rep3))) # Possible dups, very rare. LN
	rep3b = (list(dict.fromkeys(rep3b))) # Possible dups, very rare. LN2
	rep = rep+rep2+rep3+rep3b

	fout = open(output, "w")
	d="*"
	header = ("packet_number"+d+"date"+d+"freq"+d+"addr"+d+"delta_t"+d+"rssi"+d+"channel"+d+"pdu_type"+d+"AdvA"+d+"data_flags"+d+"InitA"+d+"ScanA"+d+"Manufacturer"+d+"TxPowerlvl"+d+"local_name"+d+"local_name_ml"+d+"AdvA_ml"+d+"InitA_ml"+d+"ScanA_ml")
    
	fout.write("{}\n".format(header))
	u=[]
	print("Working on it...")
	with open(input) as z:
		csvReader = csv.reader(z, delimiter='*')
		next(csvReader)
		for row in csvReader:
			line_num = str(row[0])
			date = str(row[1])
			freq = str(row[2])
			addr = str(row[3])
			delta_t = str(row[4])
			rssi = str(row[5])
			channel = str(row[6])
			pdu_type = str(row[7])
			AdvA = str(row[8])
			data_flags = str(row[9])
			InitA = str(row[10])
			ScanA = str(row[11])
			Manufacturer = str(row[12])
			TxPowerlvl = str(row[13])
			local_name = str(row[14])

			local_name_ml = ''
			AdvA_ml = ''
			InitA_ml = ''
			ScanA_ml = ''
			###############################################################
			if any(AdvA.strip() in s for s in rep):
				x = [s for s in rep if AdvA.strip() in s][0]

				changing = x.split("*")[0]
				changeWith = x.split("*")[1]

				if AdvA.strip() == changeWith:
					pass
				AdvA = AdvA.strip()
				AdvA_ml = changeWith.strip()

			else:
				AdvA = AdvA.strip()
			if len(AdvA_ml) < 4:
				AdvA_ml = AdvA.strip()
			###############################################################

			###############################################################
			if len(InitA.strip()) > 5:
				if any(InitA.strip() in s for s in rep):
					x = [s for s in rep if InitA.strip() in s][0]
					changing = x.split("*")[0]
					changeWith = x.split("*")[1]

					if InitA.strip() == changeWith:
						pass
					InitA = InitA.strip()
					InitA_ml = changeWith.strip()

			else:
				InitA = InitA.strip()
			if len(InitA_ml) < 4:
				InitA_ml = InitA.strip()
			###############################################################

			###############################################################
			if len(ScanA.strip()) > 5:
				#print(ScanA.strip())
				if any(ScanA.strip() in s for s in rep):
					x = [s for s in rep if ScanA.strip() in s][0]
					#print(x)
					changing = x.split("*")[0]
					changeWith = x.split("*")[1]

					if ScanA.strip() == changeWith:
						pass
					ScanA = ScanA.strip()
					ScanA_ml = changeWith.strip()

			else:
				ScanA = ScanA.strip()
			if len(ScanA_ml) < 4:
				ScanA_ml = ScanA.strip()
			###############################################################

			###############################################################
			if local_name.strip():
				if len(local_name.strip()) > 4:
					if any(local_name.strip() in s for s in rep3b):
						x = [s for s in rep if local_name.strip() in s][0]
						changing = x.split("*")[0]
						changeWith = x.split("*")[1]

						if local_name.strip() == changeWith:
							pass
						local_name = local_name.strip()
						local_name_ml = changeWith.strip()

			else:
				local_name = local_name.strip()
			if len(local_name_ml) < 4:
				local_name_ml = local_name.strip()
			###############################################################

			d = "*" #delimiter
			all = "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(line_num,d,date,d,freq,d,addr.strip(),d,delta_t.strip(),d,rssi.strip(),d,channel.strip(),d,pdu_type.strip(),d,AdvA.strip(),d,data_flags.strip(),d,InitA.strip(),d,ScanA.strip(),d,Manufacturer.strip(),d,TxPowerlvl.strip(),d,local_name.strip(),d,local_name_ml.strip(),d,AdvA_ml.strip(),d,InitA_ml.strip(),d,ScanA_ml.strip())
			#u.append(all)
			fout.write("{}\n".format(all))
	print("Finished!")
	#for i in u:
	#	fout.write("{}\n".format(i))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str,
                    help=" -> input file")
    parser.add_argument("output", type=str,
                        help=" -> output file")
    args = parser.parse_args()
    input=args.input
    output=args.output

    print("Reading file: {}...".format(input))
    MachineLearning(input,output)
    print("Output Written to: {}...".format(output))