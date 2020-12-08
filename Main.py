import time,re,datetime,sys,argparse,os,csv
# Anthony Last edited on 11-8-2020

# In a second terminal: ubertooth-btle -f | sed -e 's|["'\'']||g' | xargs | sed -e 's/systime/\nsystime/g' >> z2.txt
# Use: ubertooth-util -V -- To test that Ubertooth is up and working.
# Use: ubertooth-btle -fI -r test7.pcapng | sed -e 's|["'\'']||g' | xargs | sed -e 's/systime/\nsystime/g' >> test.txt


#TODO: Might need to set a pass/break on the PDU if statements so they aren't multiple entries.
#TODO: Might just join manufact and device name into one variable..

def follow(live_log, input_or_live):

    if "input" in input_or_live:
        #live_log.seek(0,0)
        while True:
            line = live_log.readline()
            if not line:
                break
            yield line

    else:
        live_log.seek(0,2)
        while True:
                line = live_log.readline()
                if not line:
                        time.sleep(0.1)
                        continue
                yield line

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("input_or_live", type=str,
                    help=" -> input or live")
    parser.add_argument("file", type=str,
                        help=" -> file path")
    parser.add_argument("outputfile", type=str,
                        help=" -> output file path")
    args = parser.parse_args()

    input_or_live=args.input_or_live
    file=args.file
    output=args.outputfile

    if any(item in input_or_live for item in ['input', 'live']):
        print("Starting {} parser...".format(input_or_live))
    else:
        print("Need to either specify input or live..")
        exit()

    # Check if file exist, if not, create it.
    if not os.path.exists(file):
        open(file, 'w').close()

    print("Reading file: {}...".format(file))

    logfile = open(file,"r")
    loglines = follow(logfile, input_or_live)
    line_num = 0

    #d="*"
    #print("packet_number"+d+"date"+d+"freq"+d+"addr"+d+"delta_t"+d+"rssi"+d+"channel"+d+"pdu_type"+d+"AdvA"+d+"data_flags"+d+"InitA"+d+"ScanA"+d+"Manufacturer"+d+"TxPowerlvl"+d+"local_name"+d+"local_name_ml"+d+"AdvA_ml"+d+"InitA_ml"+d+"ScanA_ml")

    fout = open(output, "w")
    d="*"
    header = ("packet_number"+d+"date"+d+"freq"+d+"addr"+d+"delta_t"+d+"rssi"+d+"channel"+d+"pdu_type"+d+"AdvA"+d+"data_flags"+d+"InitA"+d+"ScanA"+d+"Manufacturer"+d+"TxPowerlvl"+d+"local_name"+d+"local_name_ml"+d+"AdvA_ml"+d+"InitA_ml"+d+"ScanA_ml")
    fout.write("{}\n".format(header))
    for line in loglines:
        line_num += 1
        sl = line.strip()
        sl_len = len(sl)

        DEBUG = 0 #0 = off, 1 = on, prints all variables with \n

        if DEBUG:
            print("Line Number - {}".format(line_num))

        # Setting blank values to all variables that will be used
        date = freq = addr = delta_t = rssi = channel = '' # First part
        pdu_type = AdvA = data_flags = InitA = ScanA = '' # PDU part
        Manufacturer = TxPowerlvl = local_name = '' # Last part
        local_name_ml = AdvA_ml = InitA_ml = ScanA_ml = '' # 2nd to last

        # Making sure packet has Mac-Address
        p = re.compile(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})', re.IGNORECASE)
        found = re.findall(p, line)

        if not found:
            continue

        ########################
        ### Error handling start

        sl = sl.replace('*', '') #Using * as delimiter, getting rid of any false positivies.

        if "CRC:" not in sl: # Making sure packet has is completed with CRC ending..
            continue

        if "Early return due to" in sl: # Another error string
            continue

        if not sl.startswith('systime='): #If line doesn't start with systime=, move to the next.
            continue

        if "Error:" in sl: #Remove all malformed packets, 'Error: attempt to read past end of buffer...'
            continue

        if "UNKNOWN Data:" in sl: #Remove all malformed packets
            continue

        if (sl_len < 220): #Half written packets, no good anyways. grep -x '.\{1,200\}' -n
            continue

        ### Error handling end
        ######################


        #Dropping all data packets for now.
        matches = ["LL_FEATURE_REQ", "L2CAP", "LL Control PDU"]
        if any([substring in sl for substring in matches]):
            continue

        else:
            try:
                date = re.findall('systime=(.*?) freq=', sl)
                date = int(date[0])
                date = datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d %I:%M:%S")
                if DEBUG:
                    print(date)
            except:
                data=''
            
            try:
                freq = re.findall('freq=(.*?) addr=',sl)
                freq = int(freq[0])
                if DEBUG:
                    print(freq)
            except:
                freq=''
            
            try:
                addr = re.findall('addr=(.*?) delta_t=',sl) #The AccessAddress property defines the 32-bit unique connection address between two devices. The default value is '8E89BED6'.
                addr = str(addr[0])
                if DEBUG:
                    print(addr)
            except:
                addr=''

            try:
                delta_t = re.findall('delta_t=(.*?) ms rssi=',sl)
                delta_t = str(delta_t[0])
                if DEBUG:
                    print(delta_t)
            except:
                delta_t=''
            
            try:
                rssi = re.findall('rssi=(.*?)\s',sl)
                rssi = str(rssi[0])
                rssi = rssi.split(" ")[:1][0]
                if DEBUG:
                    print(rssi)
            except:
                rssi=''
            
            try:
                channel = re.findall('Channel Index: (.*) Type:',sl)
                channel = str(channel[0])
                if DEBUG:
                    print(channel)
            except:
                channel=''
            

            # Checking for PDU types
            # http://j2abro.blogspot.com/2014/06/understanding-bluetooth-advertising.html
            # https://www.novelbits.io/bluetooth-low-energy-sniffer-tutorial-advertisements/

            if "ADV_IND" in sl: #Known as Advertising Indications (ADV_IND), where a peripheral device requests connection to any central device (i.e., not directed at a particular central device). Example:  A smart watch requesting connection to any central device.
                try:
                    pdu_type = re.findall('Type: (.*?) AdvA: ',sl)
                    pdu_type = str(pdu_type[0])
                    if DEBUG:
                        print(pdu_type)
                except:
                    pdu_type=''

                if "AdvData" in sl:
                    try:
                        AdvA = re.findall('AdvA: (.*?) AdvData: ',sl)
                        AdvA = str(AdvA[0])
                        if DEBUG:
                            print(AdvA)
                    except:
                        AdvA=''

                else:
                    try:
                        AdvA = re.findall('AdvA: (.*?) Data: ',sl)
                        AdvA = str(AdvA[0])
                        if DEBUG:
                            print(AdvA)
                    except:
                        AdvA=''

                if "Type 01 (Flags)" in sl: #Are included when an advertising packet is connectable. 
                # https://devzone.nordicsemi.com/f/nordic-q-a/29083/ble-advertising-data-flags-field-and-discovery
                    split_flags = sl.split("(Flags)")[1] #Getting second half after split for better coverage

                    if "Early return due" in split_flags: #Fixed error with Early warning.
                        try:
                            data_flags = re.findall('Flags\) \d\d\d\d\d\d\d\d (.*?) Early',sl)
                            data_flags = str(data_flags[0])
                            if DEBUG:
                                print(data_flags)
                        except:
                            data_flags=''

                    if "Type 0a" in split_flags:
                        try:
                            data_flags = re.findall('Flags\) \d\d\d\d\d\d\d\d (.*?) Type 0a',sl)
                            data_flags = str(data_flags[0])
                            if DEBUG:
                                print(data_flags)
                        except:
                            data_flags=''

                    if ("Type: " or "Reserved Data:") in split_flags:
                        try:
                            data_flags = re.findall('Flags\) \d\d\d\d\d\d\d\d (.*?) (Type:|Reserved Data:)',sl)
                            data_flags = str(data_flags[0])
                            if DEBUG:
                                print(data_flags)
                        except:
                            data_flags=''

                    #elif "Data:" in split_flags:
                    #   data_flags = re.findall('Flags\) \d\d\d\d\d\d\d\d (.*?) Data: ',sl)
                    #   data_flags = str(data_flags[0])
                    #   print(data_flags)

            if "ADV_DIRECT_IND" in sl: #Connectable directed advertising. Directed advertising is used when a device needs to quickly connect to another device. An initiating device immediately sends a connection request upon receiving this. This PDU has the following payload. Example: A smart watch requesting connection to a specific central device.
                try:
                    pdu_type = re.findall('Type: (.*?) AdvA: ',sl)
                    pdu_type = str(pdu_type[0])
                    if DEBUG:
                        print(pdu_type)
                except:
                    pdu_type=''
                
                try:
                    AdvA = re.findall('AdvA: (.*?) InitA: ',sl)
                    AdvA = str(AdvA[0])
                    if DEBUG:
                        print(AdvA)
                except:
                    AdvA=''
                
                try:
                    InitA = re.findall('InitA: (.*?) Data: ',sl)
                    InitA = str(InitA[0])
                    if DEBUG:
                        print(InitA)
                except:
                    InitA=''
            
            # Just like ADV_IND, need to figure out main portion..
            if "ADV_NONCONN_IND" in sl: #Non connectable undirected advertising. Used by devices that want to broadcast and don't want to be connected to or scannable. This is the only option for a device that is only a transmitter. Example:  Beacons in museums defining proximity to specific exhibits.
                try:
                    pdu_type = re.findall('Type: (.*?) AdvA: ',sl)
                    pdu_type = str(pdu_type[0])
                    if DEBUG:
                        print(pdu_type)
                except:
                    pdu_type=''

                if "AdvData" in sl:
                    try:
                        AdvA = re.findall('AdvA: (.*?) AdvData: ',sl)
                        AdvA = str(AdvA[0])
                        if DEBUG:
                            print(AdvA)
                    except:
                        AdvA=''

                else:
                    try:
                        AdvA = re.findall('AdvA: (.*?) Data: ',sl)
                        AdvA = str(AdvA[0])
                        if DEBUG:
                            print(AdvA)
                    except:
                        AdvA=''

            # Just like ADV_IND, need to figure out main portion..
            if "ADV_SCAN_IND" in sl: #Example:  A warehouse pallet beacon allowing a central device to request additional information about the pallet.

                try:
                    pdu_type = re.findall('Type: (.*?) AdvA: ',sl)
                    pdu_type = str(pdu_type[0])
                    if DEBUG:
                        print(pdu_type)
                except:
                    pdu_type=''

                if "AdvData" in sl:
                    try:
                        AdvA = re.findall('AdvA: (.*?) AdvData: ',sl)
                        AdvA = str(AdvA[0])
                        if DEBUG:
                            print(AdvA)
                    except:
                        AdvA=''

                else:
                    try:
                        AdvA = re.findall('AdvA: (.*?) Data: ',sl)
                        AdvA = str(AdvA[0])
                        if DEBUG:
                            print(AdvA)
                    except:
                        AdvA=''

                if "Type 01 (Flags)" in sl: #Are included when an advertising packet is connectable. 
                # https://devzone.nordicsemi.com/f/nordic-q-a/29083/ble-advertising-data-flags-field-and-discovery

                    if "Early return due" in sl: #Fixed error with Early warning.
                        try:
                            data_flags = re.findall('Flags\) \d\d\d\d\d\d\d\d (.*?) Early',sl)
                            data_flags = str(data_flags[0])
                            if DEBUG:
                                print(data_flags)
                        except:
                            data_flags=''
                    else:
                        try:
                            data_flags = re.findall('Flags\) \d\d\d\d\d\d\d\d (.*?) Type',sl)
                            data_flags = str(data_flags[0])
                            if DEBUG:
                                print(data_flags)
                        except:
                            data_flags=''

            # While not specifically an advertising PDU type, active scanning will involve the following additional
            if "SCAN_REQ" in sl: #Upon receiving and advertising packet and active scanner will issue this scan request packet
                try:
                    pdu_type = re.findall('Type: (.*?) ScanA: ',sl)
                    pdu_type = str(pdu_type[0])
                    if DEBUG:
                        print(pdu_type)
                except:
                    pdu_type=''

                try:
                    AdvA = re.findall('AdvA: (.*?) Data: ',sl)
                    AdvA = str(AdvA[0])
                    if DEBUG:
                        print(AdvA)
                except:
                    AdvA=''

                try:
                    ScanA = re.findall('ScanA: (.*?) AdvA: ',sl)
                    ScanA = str(ScanA[0])
                    if DEBUG:
                        print(ScanA)
                except:
                    ScanA=''
                
            if "SCAN_RSP" in sl:  #Upon receiving a scan request (SCAN_REQ) packet and advertiser can respond with this.
                try:
                    pdu_type = re.findall('Type: (.*?) AdvA: ',sl)
                    pdu_type = str(pdu_type[0])
                    if DEBUG:
                        print(pdu_type)
                except:
                    pdu_type=''
            
                try:
                    AdvA = re.findall('AdvA: (.*?) ScanRspData: ',sl)
                    AdvA = str(AdvA[0])
                    if DEBUG:
                        print(AdvA)
                except:
                    AdvA=''

            if "CONNECT_REQ" in sl: 

                matches = ["Type:", "InitA:", "AdvA:", "AA:"]
                if any([substring in sl for substring in matches]):
                #The Central device, « the initiator », sends the packet Connect_Req to a device with the connectable and discoverable mode to establish a connection link. This packet contains all the required data needed for the future connection between the two devices.

                # Can still parse out many of the fields, if necessary.
                # http://rfmw.em.keysight.com/wireless/helpfiles/n7606/Content/Main/PDU_Payload_Setting_4.htm#CRC

                    try:
                        pdu_type = re.findall('Type: (.*?) InitA: ',sl)
                        pdu_type = str(pdu_type[0])
                        if DEBUG:
                            print(pdu_type)
                    except:
                        pdu_type=''
                
                    try:
                        InitA = re.findall('InitA: (.*?) AdvA: ',sl)
                        InitA = str(InitA[0])
                        if DEBUG:
                            print(InitA)
                    except:
                        InitA=''

                    try:
                        AdvA = re.findall('AdvA: (.*?) AA: ',sl)
                        AdvA = str(AdvA[0])
                        if DEBUG:
                            print(AdvA)
                    except:
                        AdvA=''

            ### Finished with PDU stuff
            ###########################

            if "Manufacturer Specific Data" in sl: #Are included when an advertising packet is connectable. 
            # https://devzone.nordicsemi.com/f/nordic-q-a/29083/ble-advertising-data-flags-field-and-discovery

                if "(Manufacturer Specific Data) Wrong length" in sl:
                    pass

                else:
                    try:
                        Manufacturer = re.findall('Company: (.*?) Data:',sl)
                        Manufacturer = str(Manufacturer[0])
                        if DEBUG:
                            print(Manufacturer)
                    except:
                        Manufacturer=''

            if "Tx Power Level" in sl: #Tx Power Level 

                if "dBm" not in sl:
                    pass

                else:
                    try:
                        TxPowerlvl = re.findall('Tx Power Level\) (.*?) dBm',sl)
                        TxPowerlvl = str(TxPowerlvl[0])
                        if DEBUG:
                            print(TxPowerlvl)
                    except:
                        TxPowerlvl=''


            if ("Complete Local Name") in sl: #Are included when an advertising packet is connectable.
                try:
                    local_name = re.findall('\(Complete Local Name\) (.*?) Data: ',sl)
                    local_name = str(local_name[0])
                    if DEBUG:
                        print(local_name)

                    pattern = '.*Type \S\S '
                    result = re.match(pattern, local_name)
                    if result:
                      local_name = (result[0].split("Type")[0]) # Holy !@#$ this took awhile, works though.
                except:
                    local_name=''

            if "Type" in data_flags: # Cleaning up some more Type misplacements.
                try:
                    pattern = '.*Type \S\S '
                    result = re.match(pattern, data_flags)
                    if result:
                      data_flags = (result[0].split("Type")[0]) # Holy !@#$ this took awhile, works though.
                except:
                    data_flags=''

        # Joining everything up in one CSV line before plotting..    
        first_part = date,freq,addr,delta_t,rssi,channel #every packet will have this
        pdu_part =   pdu_type,AdvA,data_flags,InitA,ScanA #Some packets will have either data_flags,InitA,ScanA
        last_part =  Manufacturer,TxPowerlvl,local_name,local_name_ml,AdvA_ml,InitA_ml,ScanA_ml

        d = "*" #delimiter
        all = "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(line_num,d,date,d,freq,d,addr.strip(),d,delta_t.strip(),d,rssi.strip(),d,channel.strip(),d,pdu_type.strip(),d,AdvA.strip(),d,data_flags.strip(),d,InitA.strip(),d,ScanA.strip(),d,Manufacturer.strip(),d,TxPowerlvl.strip(),d,local_name.strip(),d,local_name_ml.strip(),d,AdvA_ml.strip(),d,InitA_ml.strip(),d,ScanA_ml.strip()) 
        fout.write("{}\n".format(all))
        if DEBUG:
            print("\n")
if input_or_live == "input":
   print("Finished!")
   print("Output Written to: {}".format(output))

"""
('2020-11-06 03:50:47', 2402, '8e89bed6', '29.145', '-87', '37', 'SCAN_REQ', 'f8:66:56:8f:ca:97 (random)', '', '', '5c:31:38:ce:73:95 (public)')


systime=1604706634 freq=2402 addr=8e89bed6 delta_t=6.983 ms rssi=-85 40 18 c9 87 f2 00 ff 76 02 01 1a 02 0a 0c 0b ff 4c 00 10 06 1e 1e d1 69 02 d2 6e a4 b6 Advertising / AA 8e89bed6 (valid)/ 24 bytes Channel Index: 37 Type: ADV_IND AdvA: 76:ff:00:f2:87:c9 (random) AdvData: 02 01 1a 02 0a 0c 0b ff 4c 00 10 06 1e 1e d1 69 02 d2 Type 01 (Flags) 00011010 LE General Discoverable Mode Simultaneous LE and BR/EDR to Same Device Capable (Controller) Simultaneous LE and BR/EDR to Same Device Capable (Host) Type 0a (Tx Power Level) 12 dBm Type ff (Manufacturer Specific Data) Company: Apple, Inc. Data: 10 06 1e 1e d1 69 02 d2 Data: c9 87 f2 00 ff 76 02 01 1a 02 0a 0c 0b ff 4c 00 10 06 1e 1e d1 69 02 d2 CRC: 6e a4 b6


systime=1604703856 freq=2402 addr=8e89bed6 delta_t=24.515 ms rssi=-87
00 25 99 01 71 ae 1c 64 02 01 1a 1b ff 75 00 42 04 01 01 6f 64 1c ae 71 01 99 66 1c ae 71 01 98 0b 00 00 00 00 00 00 c7 ec 7c 
Advertising / AA 8e89bed6 (valid)/ 37 bytes
        Channel Index: 37
        Type:  ADV_IND
        AdvA:  64:1c:ae:71:01:99 (public)
        AdvData: 02 01 1a 1b ff 75 00 42 04 01 01 6f 64 1c ae 71 01 99 66 1c ae 71 01 98 0b 00 00 00 00 00 00
                Type 01 (Flags)
                     00011010
                             LE General Discoverable Mode
                             Simultaneous LE and BR/EDR to Same Device Capable (Controller)
                             Simultaneous LE and BR/EDR to Same Device Capable (Host)

                Type ff (Manufacturer Specific Data)
                     Company: Samsung Electronics Co. Ltd.
                     Data: 42 04 01 01 6f 64 1c ae 71 01 99 66 1c ae 71 01 98 0b 00 00 00 00 00 00

        Data:  99 01 71 ae 1c 64 02 01 1a 1b ff 75 00 42 04 01 01 6f 64 1c ae 71 01 99 66 1c ae 71 01 98 0b 00 00 00 00 00 00
        CRC:   c7 ec 7c
"""