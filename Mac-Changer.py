import csv,time,argparse,os
# Mac address vendor database CSV format, located here: https://macaddress.io/database-download/csv

#TODO: Thread this file, takes way to long.
#TODO: Change the fuction check to read list from memory.

def check(search_string):
    with open('macaddress.io-db.csv', 'r') as f:
        csvReader = csv.reader(f, delimiter=',')
        for row in csvReader:
            MAC = str(row[0])
            CompanyName = str(row[2])
            if search_string in MAC:
                return CompanyName[0:8].strip()
        return False

def Mac(input,output):
    fout = open(output, "w")
    d="*"
    header = ("packet_number"+d+"date"+d+"freq"+d+"addr"+d+"delta_t"+d+"rssi"+d+"channel"+d+"pdu_type"+d+"AdvA"+d+"data_flags"+d+"InitA"+d+"ScanA"+d+"Manufacturer"+d+"TxPowerlvl"+d+"local_name"+d+"local_name_ml"+d+"AdvA_ml"+d+"InitA_ml"+d+"ScanA_ml")
    fout.write("{}\n".format(header))
    u=[]
    with open(input) as csvDataFile:
        csvReader = csv.reader(csvDataFile, delimiter='*')
        next(csvReader)
        print("Working on it...")
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
            local_name_ml = str(row[15])
            try:
                AdvA_ml = str(row[16])
                InitA_ml = str(row[17])
                ScanA_ml = str(row[18])
            except:
                TxPowerlvl=''
                AdvA_ml=''
                InitA_ml=''
                ScanA_ml=''

            matches = ["public"]
            if any([substring in AdvA for substring in matches]):
                search_string = AdvA[0:8].strip().upper()
                last_bit = AdvA[8:]
                line = check(search_string)
                if check(search_string):
                    AdvA = line.strip()+last_bit

            if any([substring in InitA for substring in matches]):
                search_string = InitA[0:8].strip().upper()
                last_bit = InitA[8:]
                line = check(search_string)
                if check(search_string):
                    InitA = line.strip()+last_bit


            if any([substring in ScanA for substring in matches]):
                search_string = ScanA[0:8].strip().upper()
                last_bit = ScanA[8:]
                line = check(search_string)
                if check(search_string):
                    ScanA = line.strip()+last_bit


            if any([substring in AdvA_ml for substring in matches]):
                search_string = AdvA_ml[0:8].strip().upper()
                last_bit = AdvA_ml[8:]
                line = check(search_string)
                if check(search_string):
                    AdvA_ml = line.strip()+last_bit

            if any([substring in InitA_ml for substring in matches]):
                search_string = InitA_ml[0:8].strip().upper()
                last_bit = InitA_ml[8:]
                line = check(search_string)
                if check(search_string):
                    InitA_ml = line.strip()+last_bit


            if any([substring in ScanA_ml for substring in matches]):
                search_string = ScanA_ml[0:8].strip().upper()
                last_bit = ScanA_ml[8:]
                line = check(search_string)
                if check(search_string):
                    ScanA_ml = line.strip()+last_bit

            d = "*" #delimiter
            all = "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(line_num,d,date,d,freq,d,addr.strip(),d,delta_t.strip(),d,rssi.strip(),d,channel.strip(),d,pdu_type.strip(),d,AdvA.strip(),d,data_flags.strip(),d,InitA.strip(),d,ScanA.strip(),d,Manufacturer.strip(),d,TxPowerlvl.strip(),d,local_name.strip(),d,local_name_ml.strip(),d,AdvA_ml.strip(),d,InitA_ml.strip(),d,ScanA_ml.strip())
            u.append(all)
    print("Finished!")
    for i in u:
        fout.write("{}\n".format(i))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str,
                    help=" -> input file")
    parser.add_argument("output", type=str,
                        help=" -> output file")
    args = parser.parse_args()
    input=args.input
    output=args.output
    if os.path.exists('macaddress.io-db.csv'):
        print("Reading file: {}...".format(input))
        Mac(input,output)
        print("Output Written to: {}".format(output))
    else:
        print("Can't find macaddress.io-db.csv.. ")
