##................. main program ........................
import logging
import sys
import socket
import time
from threading import Lock
import serial
import threading
from threading import Lock
import encodings
import struct
import errno
import socketserver
import time
from socket import error as socket_error
import sys
import binascii
import ctypes
import sqlite3
import os
import datetime
import random
buffer_overflow_status=0
lost_overflow=0
flag=0
def get_timenow():
    time_now = datetime.datetime.now()
    date_time = time_now.strftime("%d/%m/%Y %H:%M:%S")
    tim = int(date_time.split(' ')[1].split(':')[0], 10) * 3600 + int(date_time.split(' ')[1].split(':')[1], 10)*60 +int(date_time.split(' ')[1].split(':')[2],10)
    return tim


def time_manager():
    time.sleep(15)
    time_range = []
    f = open('pslv_12_reduced_21.dat', 'r')
    data = f.readlines()
    f.close()
    for i in range(len(data)):
        data[i] = data[i].strip()
        temp1, temp2, temp3, temp4 = data[i].split(',')
        temp1 = int(temp1)
        temp2 = int(temp2)
        temp3 = int(temp3)
        temp4 = int(temp4)
        # if temp2 == gsu_no or temp3 == gsu_no:
        time_range.append((temp1, temp1 + temp4))
    os.system("sudo timedatectl set-time '00:00:00'")
    time_now = datetime.datetime.now()
    date_time = time_now.strftime("%d/%m/%Y %H:%M:%S")
    clk_time = date_time.split(' ')[1]
    print("Starting time:", clk_time)
    print(time_range)
    time.sleep(13)
    for p in range(len(time_range)):
        ts, te = time_range[p]
        ts = ts-30
        print(ts, te)
        tim = get_timenow()
        if tim < ts:
            s_tim=str(datetime.timedelta(seconds=(ts)))
            print("before time set:",tim)
            os.system("sudo timedatectl set-time " + "'" + s_tim + "'")
         #   tim = get_timenow()
            print("<ts.........after time set:",s_tim)
            while True:
             #  print(get_timenow())
               if get_timenow()>ts:
                   break 
        tim = get_timenow()
        print("current time ",tim,"ts te",ts,te)
        if tim < te and tim >= ts:
            tim = get_timenow()
            print(">ts.........")
            while True:
             #  print(get_timenow())
               if get_timenow()>te:
                   break

def obc(obc_no, lora, lock):
    global lost_overflow
#    logging.basicConfig(filename='obc'+str(obc_no)+'.log', filemode='w',format='%(gsu_no)-%(asctime)s - %(message)s', level=logging.INFO)
    table = {}  # flow table dict
    copy = {}
    event_beacon_recep = 'Beacon_Reception'
    event_buffer_overflow='Buffer_Overflow'
    received_beacon_id=[]
    def nodeid(node):
        no = 33554432 + node
        ID = hex(no)
        return ID

    def access_time():
        tim = []
        f = open('pslv_12_reduced_21.dat', 'r')
        data = f.readlines()
        f.close()
        for i in range(len(data)):
            data[i] = data[i].strip()
            temp1, temp2, temp3, temp4 = data[i].split(',')
            temp1 = int(temp1)
            temp2 = int(temp2)
            temp3 = int(temp3)
            temp4 = int(temp4)
            if temp2 == obc_no or temp3 == obc_no:
                tim.append((temp1, temp1 + temp4))
        return tim
   

    def beacon_reception(pkt,te):
        global buffer_overflow_status
        beacon = struct.unpack("!1si4s1s", pkt)
        src_id = binascii.hexlify(beacon[2]).decode()
        src_id = src_id[0] + 'x' + src_id[1:]
        src_id_int = int(src_id, 16)
        node_no = src_id_int - 33554432
        flag = beacon[3].decode('utf-8')
        ind = src_id + flag
        received_beacon_id.append(ind)
        l=len(received_beacon_id)
        print("Event called beacon reception")
        print(received_beacon_id)
        if len(received_beacon_id)==1:
            if node_no in [1,8]:
                print(get_timenow(),":",obc_no,":","ground station connected")
            elif node_no in [9,3,4,11]:
                print(get_timenow(),":",obc_no,":","end-user connected")
            else:
                print(get_timenow(),":",obc_no,":","obu connected",node_no)
                if buffer_overflow_status==0: 
                    data_packets_sender(src_id,te,1)
                else:
                    event_table[event_buffer_overflow](src_id,te)

        elif received_beacon_id[l-2] == received_beacon_id[l-1]:
            print("same beacon as before received")
            pass
        elif received_beacon_id[l-2][:-1] == received_beacon_id[l-1][:-1]:
            print(get_timenow(),":",obc_no,":","Same beacon as before..checking status for transmission",flag)
            if flag == '1':
                if buffer_overflow_status==0:
                    print("checking for any data to send")
                    data_packets_sender(src_id,te,0)
                else:
                    print("overflow situation checking for sending any data")
                    event_table[event_buffer_overflow](src_id,te)
        else:
            if node_no in [11,9,8,6]:
                print(get_timenow(),":",obc_no,":","ground station connected")
            elif node_no in [5,1,0]:
                print(get_timenow(),":",obc_no,":","end-user connected")
            else:
                print(get_timenow(),":",obc_no,":","obu connected",node_no)
                if buffer_overflow_status==0: 
                    data_packets_sender(src_id,te,1)
                else:
                    event_table[event_buffer_overflow](src_id,te)

    def data_packets_sender(obu_id,te,var):
#        buffer_handler()
        k=0
        print(obc_no,":","checking for any stored data packets to send")
        while True:
            con1 = sqlite3.connect("Store"+str(obc_no)+".db")
            cur1 = con1.cursor()
            cur1.execute('SELECT COUNT(*) FROM data_packets')
            cur_result = cur1.fetchone()
            rows = cur_result[0]
            i = 0
          #  print("hey",rows)
            temp=0
            if get_timenow()>te:
                break
            if rows==0:
                print("no data in store")
                return 0
            for row in cur1.execute("SELECT * FROM data_packets"):
                # print(get_timenow(),":",obc_no,":","buffer_handler:checking for any matches")
                unpacked_pkt = row[0]
                next_hop_id = row[3]
                destination_id = row[5]
       #         print("next hop id",next_hop_id,"obu id",obu_id)
                i += 1
                if obu_id == next_hop_id or obu_id == destination_id:
                    print("match found sending packet")
                    send(unpacked_pkt)
                    buff_time.append((get_timenow(),obc_no,row[1]))
                 #   print(unpacked_pkt)
                    cur1.execute("DELETE FROM data_packets WHERE data_packet = ?", (unpacked_pkt,))
                    break
            cur1.execute('SELECT COUNT(*) FROM data_packets')
         #   print("hey",cur1.fetchone())
            con1.commit()
            con1.close()
            if var==1:
                time.sleep(random.choice([0,1,2]))
        print("finsih checking the buffer")
        return 0

    def packet_receiver(obc_no):
        time.sleep(30)
        for p in range(len(t1)):
           ts, te = t1[p]
           tim = get_timenow()
           print(get_timenow(),":",obc_no,":","Receiver:",t1[p])
           if tim < ts:
               # print(get_timenow(),":",obc_no,":","radio is sleeping for ", (ts - tim) * 60 + 60)
               # time.sleep((ts - tim) * 60 + 60)
               print(get_timenow(),":",obc_no,":","waiting",tim)
               while True:
                  # time.sleep((ts - tim) * 60 + 60)
                  tim = get_timenow()
                  if tim > ts:
                      break
           if te > tim >= ts:
               while True:
                  if get_timenow()>te:
                      break
                  lock.acquire()
                  lora.write(b'radio rx 0\r\n')  # continous reception mode
                  print(get_timenow(),":",obc_no,":","radio is on...")
                  if lora.readline().strip() == "ok" or "radio_tx_ok":
                      raw = str(lora.readline().strip())
                      lock.release()
                      p = raw.split(' ')[0].split("'")[1]

                      if p == ('radio_rx'):  # a packet is received by the radio
                          print(get_timenow(),":",obc_no,":","received packet")
                          packet = ((raw.split(' '))[2]).strip().split("'")[0]
                          decode_packet = bytearray.fromhex(packet)
                          print(get_timenow(),":",obc_no,":","sending to packet handler")
                          packet_handler(decode_packet, obc_id,te)
                      elif p == ("radio_err"):
                          print(get_timenow(),":",obc_no,":","reception was not successful, reception time-out occurred")
                  else:
                      print(get_timenow(),":",obc_no,":",lora.readline().strip())
 
 


    def packet_handler(pkt, OBU_ID,te):  # pkt is the received packet in hexadecimal format
        arr_header = struct.unpack_from('!1s', pkt)  # data packet
        pkt_type = arr_header[0].decode('utf-8')
        pkt_type= int(pkt_type,10)
        if pkt_type == 2:
            print(get_timenow(),":",obc_no,":","\nPacket is control packet")
            update_rule(pkt)
        elif pkt_type == 1 :
            print(get_timenow(),":",obc_no,":","\nPacket is data type")
            data_handler(pkt, OBU_ID)
        elif pkt_type == 3:
            print(get_timenow(),":",obc_no,":","\nPacket is beacon packet")
            event_table[event_beacon_recep](pkt,te)
        else:
            print(get_timenow(),":",obc_no,":","unknown packet",pkt_type,type(pkt_type))
            print(get_timenow(),":",obc_no,":","unknown packet:",pkt)
            print(get_timenow(),":",obc_no,":",pkt_type,"doicoifdod",pkt_type)

    def update_rule(pkt):
        # extract src_id, dest_id, start_time,stop_time,action of array
        arr = struct.unpack('!1sii4s4s1s4s4s1s', pkt)
        k = len(table)
        src_id = binascii.hexlify(arr[3]).decode()
        src_id = src_id[0] + 'x' + src_id[1:]
        dest_id = binascii.hexlify(arr[4]).decode()
        dest_id = dest_id[0] + 'x' + dest_id[1:]
        prem_id = binascii.hexlify(arr[6]).decode()
        prem_id = prem_id[0] + 'x' + prem_id[1:]
        sec_id = binascii.hexlify(arr[7]).decode()
        sec_id = sec_id[0] + 'x' + sec_id[1:]
        start_time = arr[1]
        stop_time = arr[2]
        temp = ":".join([str(k), src_id, dest_id])
        op_id = arr[5].decode('utf-8')
        act = arr[8].decode('utf-8')
        temp = ":".join([src_id, dest_id])

        if op_id == "1":  ## ADD packets
            k += 1
            print(get_timenow(),":",obc_no,":","Adding rules in flow tables")
            key = ":".join([str(k), src_id, dest_id])  # join src_id, dest_id
            value = [start_time, stop_time, prem_id, sec_id, act]
            table[key] = value
            copy[key] = value
        else:
            print(get_timenow(),":",obc_no,":","unknown control packet",arr)
            # print(get_timenow(),":",obc_no,":","\nDisplaying Table:")
            # for key in table:
            #     print(get_timenow(),":",obc_no,":",key, table[key])
        #
        # elif op_id == "0":  ##DELETE Packets
        #     print(get_timenow(),":",obc_no,":","Deleting the rule in flow table")
        #     for l in table.copy():
        #         value = table[l]
        #         if l == temp:
        #             if [start_time, stop_time, act] == value:
        #                 del table[l]
        #     print(get_timenow(),":",obc_no,":","\nDisplaying Table:")
        #     for key in table:
        #         print(get_timenow(),":",obc_no,":","\n", key, table[key])

    def data_handler(pkt, OBU_ID):
        arr_headers = struct.unpack_from('!1si4s4si', pkt)  # data packet
        data_len = arr_headers[4]
        arr = struct.unpack('!1si4s4si' + str(data_len) + 's', pkt)
        data_len = arr[4]
        print(get_timenow(),":",obc_no,":","In Data Handler")
        src_id = binascii.hexlify(arr[2]).decode()
        src_id = src_id[0] + 'x' + src_id[1:]
        # src_id of the packet
        dest_id = binascii.hexlify(arr[3]).decode()
        dest_id = dest_id[0] + 'x' + dest_id[1:]
        print(get_timenow(),":",obc_no,":","Destination:", dest_id)
        i = 0
        if str(dest_id) == str(OBU_ID):  # if dest_id is the switch address
            print(get_timenow(),":",obc_no,":","Data packet consists of control packet")
            data = arr[5]
            print(get_timenow(),":",obc_no,":","\nData:", data)
            #    data = data[:-31]# control packets have fixed size of 66 so deleting the additional x00
            packet_handler(data, OBU_ID)
        else:
            data = arr[5].decode()
            print(get_timenow(),":",obc_no,":","Checking data packets for any matches with flow rules")
            if not bool(table):
                print(get_timenow(),":",obc_no,":","NO flow rules ,adding to storeTodecide")
                # time_now = datetime.datetime.now()
                # date_time = time_now.strftime("%d/%m/%Y %H:%M:%S")
                # clk_time = int(date_time.split(' ')[1].replace(':', ''), 10)
                # arr = arr + (clk_time,)
                pkt_StoreToDecide(pkt,dest_id)
                return 0
            for key,value in table.items():
                i += 1
                temp = ":".join([str(i), src_id, dest_id])
                if key == temp:
                    print(get_timenow(),":",obc_no,key,":",value)
                    print(obc_no, ":", "Match Found in flow table")
                    if key in copy:
                        copy[key].append(1)
                    
                    clk_time=get_timenow()
                    if clk_time > value[0]:
                        if clk_time < value[1]:
                            act = value[4]
                            if act == "1":  ## Forward
                                # if x == 1:
                                send(pkt)
                              #  buff_time.append((get_timenow(),obc_no,))
                                print(get_timenow(),":",obc_no,":","Sending directly")
                                return 0
                    else:
                        print(obc_no, ":", "Storing to forward")
                        prm_id = value[2]
                        sec_id = value[3]
                        pkt_StoreToForward(pkt, prm_id,sec_id,dest_id)
                        return 0

                elif len(table) == i:
                        print(get_timenow(),":",obc_no,":","NO matches found in flow tale ...")
                        pkt_StoreToDecide(pkt,dest_id)
                        return 0

    def flow_table_checker():
        while True:
            for key in table.copy():
                val = table[key]
                stop_time = val[1]
                clk_time=get_timenow()
                if clk_time > stop_time:
                    print(get_timenow(),":",obc_no,":","\nRule deleting due to timeout: ", key, val)
                    del table[key]
                    print(get_timenow(),":",obc_no,":","\nDisplaying Table:")
                    for key in table:
                        print(get_timenow(),":",obc_no,":","\n", key, table[key])
                    time.sleep(5)

    def send(pkt):  # packet is struct type
        r = pkt.hex()
        temp = 'radio tx ' + r + '\r\n'
        cmd = bytes(temp, 'utf8')
        lock.acquire()
        lora.write(cmd)
        print(get_timenow(),":",obc_no,"Radio:",str(lora.readline()))
        print(get_timenow(),":",obc_no,"Radio:",str(lora.readline()))
        lock.release()
        return 0

    def pkt_StoreToDecide(pkt,desti_id):
        global buffer_overflow_status
        global lost_overflow
        if buffer_overflow_status==1:
            lost_overflow+=1
            pass
        else:            
            connection1 = sqlite3.connect("Store"+str(obc_no)+".db")
            cursor1 = connection1.cursor()
            cursor1.execute("INSERT INTO data_packets VALUES (?,?,?,NULL,NULL,?)", (pkt, get_timenow(), 0,desti_id))
            cursor1.close()
            connection1.commit()
            connection1.close()
            print(get_timenow(),":",obc_no,":","Packet Stored in Store- To Decide")

    def pkt_StoreToForward(pkt, prm_hop_id , sec_hop_id,desti_id):
        global buffer_overflow_status
        global lost_overflow
        if buffer_overflow_status==1:
            lost_overflow+=1
            pass
        else:      
            connection2 = sqlite3.connect("Store"+str(obc_no)+".db")
            cursor2 = connection2.cursor()
            forw=1
     #   print(pkt,type(pkt),forw,type(forw),prm_hop_id,type(prm_hop_id),sec_hop_id,type(sec_hop_id),type(datetime.datetime.now()))
            cursor2.execute("INSERT INTO data_packets VALUES (?,?,?,?,?,?)", (pkt, get_timenow(),forw, prm_hop_id,sec_hop_id,desti_id))
            connection2.commit()
            connection2.close()
            print(get_timenow(),":",obc_no,":","Packet Stored in Store- To Forward")

    def takeelement(elem):
        return elem[1]

    def beacon_generater(beacon_time, obc_id,access_time):  # def beacon_generater(t1,OBC_ID):
        time.sleep(30)
        global flag      
        for q in range(len(access_time)):
            ts, te = access_time[q]
          #  ts = ts-120
            tim = get_timenow()
            print(get_timenow(),":",obc_no,":","beacon generator", t1[q])
            if tim < ts:
                received_beacon_id.clear()
                # print(get_timenow(),":",obc_no,":","radio is sleeping for ", (ts - tim) * 60 + 60)
                # time.sleep((ts - tim) * 60 + 60)
                print(get_timenow(),":",obc_no,":","waiting", tim)
                while True:
                    # time.sleep((ts - tim) * 60 + 60)
                    tim = get_timenow()
                    if tim > ts:
                        break
            if te > tim >= ts:
                received_beacon_id.clear()
                print(get_timenow(),":",obc_no,":",obc_no,":","sending beacons")
                while 1:
                     
                    print(get_timenow(),":",obc_no,":","beacon send")

                    if get_timenow()>te:
                        break
                    clk_time=get_timenow()
                    pkt_type = bytes("3", 'utf-8')
                    ID = obc_id.replace('x', '')
                    src_id = bytes.fromhex(ID)
                    beacon = struct.pack("!1si4s1s", pkt_type, clk_time, src_id,bytes(str(flag),'utf-8'))
                    # if x == 1:
                    send(beacon)
                    time.sleep(random.choice([2,3,4,5,6,7]))

    def buffer_handler():
       while True:
            time.sleep(5)
            con2 = sqlite3.connect("Store"+str(obc_no)+".db")
            cursor1 = con2.cursor()
            temp2=0
#            print("buff handler")
            for row in cursor1.execute("SELECT * FROM data_packets"):
                # print(get_timenow(),":",obc_no,":","buffer_handler:checking for any matches")
                unpacked_pkt = row[0]
                arr_headers = struct.unpack_from('!1si4s4si', unpacked_pkt)  # data packet
                data_len = arr_headers[4]
                pkt = struct.unpack('!1si4s4si' + str(data_len) + 's', unpacked_pkt)
                src_id = binascii.hexlify(pkt[2]).decode()
                src_id = src_id[0] + 'x' + src_id[1:]
                # src_id of the packet
                dest_id = binascii.hexlify(pkt[3]).decode()
                dest_id = dest_id[0] + 'x' + dest_id[1:]
                i=0
                temp=0
                temp2+=1
                fwd=row[2]
                if fwd==1:
                    pass
                else:
                    if not bool(table):
                        break
                    for key, value in table.items():
                        i += 1
                        # print(get_timenow(),":",obc_no,":",src_id,dest_id)
                        temp = ":".join([str(i), str(src_id), str(dest_id)])
    #                    print(get_timenow(),":",obc_no,":key:",key,"temp:",temp)
                        if key == temp:
                            # print(get_timenow(),":",obc_no,":","yo")
                            print(obc_no,key,":", value[0:3])
                            print(obc_no, ":", "Match Found in flow table buffer handler")
                            clk_time = get_timenow()
                            if key in copy:
                                copy[key].append(1)
                            clk_time=get_timenow()
                            if clk_time > value[0]:
                                if clk_time < value[1]:
                                    act = value[4]
                                    if act == "1":  ## Forward
                                        # if x == 1:
                                        print("within time sending now")
                                        send(unpacked_pkt)
                                        buff_time.append((get_timenow(),obc_no,row[1]))
                                        print(obc_no, ":", "Sending directly")
                                        cursor1.execute("DELETE FROM data_packets WHERE data_packet = ?", (unpacked_pkt,))
                                        con2.commit()
                                        break
                            else:
                  #              print(obc_no, ":", "Storing to forward from buffer handler")
                                prm_id = value[2]
                                sec_id = value[3]
                                cursor1.execute("UPDATE data_packets SET forward = ? ,primary_next_Hop_ID = ?, secondary_next_hop_id = ? WHERE data_packet = ?", (1,prm_id,sec_id,unpacked_pkt,))
                                con2.commit()
                            #    pkt_StoreToForward(unpacked_pkt, prm_id, sec_id)
                                break
                        elif len(table) == i:
                            pass

            con2.close()

    def buffer_state_check(buffer_limit):
        global buffer_overflow_status
        while True:
            con = sqlite3.connect("Store"+str(obc_no)+".db")
            cur = con.cursor()
            cur.execute('SELECT COUNT(*) FROM data_packets')
            cur_result = cur.fetchone()
            rows = cur_result[0]
            buffer_status.append((get_timenow(), rows))
            if rows >= buffer_limit:
                buffer_overflow_status=1
            else:
                buffer_overflow_status=0
            buffer_overflow_status_info.append((get_timenow(),buffer_overflow_status))
#            print(obc_no,":buffer overflow status:",buffer_overflow_status)
            time.sleep(3)
    
    def buffer_overflow_handler(obu_id,te):
        k = 0
        while True:
            connection1 = sqlite3.connect("Store" + str(obc_no) + ".db")
            cursor1 = connection1.cursor()
            cursor1.execute('SELECT COUNT(*) from data_packets')
            cur_result = cursor1.fetchone()
            rows = cur_result[0]
            if get_timenow()>te:
                break
            i = 0
            for row in cursor1.execute("SELECT * FROM data_packets"):
                # print(get_timenow(),":",obc_no,":","buffer_handler:checking for any matches")
                unpacked_pkt = row[0]
                next_hop_id = row[4]
                fwd=row[2]
                i += 1
                if obu_id == next_hop_id or fwd==0:
                    sec_shortest_path.append((get_timenow(),obc_no,obu_id,row[3],row[4]))
                    send(unpacked_pkt)
                    buff_time.append((get_timenow(),obc_no,row[1]))
                    cursor1.execute("DELETE from data_packets where data_packet = ?", [row[0]])
                    break
                
            connection1.commit()
            connection1.close()
            break
        return 0

    def get_timenow():
        time_now = datetime.datetime.now()
        date_time = time_now.strftime("%d/%m/%Y %H:%M:%S")
        tim = int(date_time.split(' ')[1].split(':')[0], 10) * 3600 + int(date_time.split(' ')[1].split(':')[1], 10)*60+int(date_time.split(' ')[1].split(':')[2], 10)
        return tim

    buffer_status=[]
    buffer_overflow_status_info=[]
    sec_shortest_path=[]
    buff_time=[]
    buffer_limit=35
    obc_id = nodeid(obc_no)
    # ----- connecting and creating database --------------
#    connection1 = sqlite3.connect("Store"+str(obc_no)+".db")
 #   cursor1 = connection1.cursor()
  #  cursor1.execute("CREATE TABLE data_packets(data_packet BLOB,store_time timestamp,forward INTEGER,primary_next_Hop_ID TEXT,secondary_next_hop_id TEXT,destination_id TEXT)")
   # connection1.close()
    # -----------------------------------------------------
    event_table = {"Buffer_Overflow": buffer_overflow_handler, "Beacon_Reception": beacon_reception}
    t1=access_time()
    t8 = threading.Thread(target=packet_receiver,args=(obc_no,))
    t8.start()
    t6 = threading.Thread(target=buffer_handler)
    t6.start()
    t3 = threading.Thread(target=flow_table_checker)
    t3.start()
    beacon_time = 5
    t4 = threading.Thread(target=beacon_generater, args=(beacon_time, obc_id,t1,))
    t5 = threading.Thread(target=buffer_state_check,args=(buffer_limit,))
    t5.start()
    t4.start()
   
   
    # print(get_timenow(),":",obc_no,":","Access time for end-user and ",obc_name)
    # print(get_timenow(),":",obc_no,":",t1)
    while True:
       time.sleep(120)
       if get_timenow()> 42747:
          file1=open("results" +str(obc_no) + ".txt",'w')
          file1.write("Buffer State:\n")
          for ele in buffer_status:
              file1.write(str(ele) + "\n")
          file1.write("Buffer Overflow status:\n")
          for ele1 in buffer_overflow_status_info:
              file1.write(str(ele1) + "\n")
          file1.write("Buffer time:\n")
          for ele3 in buff_time:
              file1.write(str(ele3) + "\n")
          file1.write("Secondary path usage :\n")
          for ele2 in sec_shortest_path:
              file1.write(str(ele2) + "\n") 
          file1.write("Flow table:\n")
          for key,value in copy.items():
              file1.write(str(key) + ":" + str(value) + "\n")
          file1.write("Lost Overflow:"+str(lost_overflow))
          file1.close()
          print("finshed...........................")
          break



def main():
    lock = Lock()
    lora = serial.Serial(port="/dev/ttyAMA0", baudrate=57600)
    print("hello")
    while True:
        # radio commands for setting up the LoRa radio
        try:
            print('cmd> radio cw off')
            print("yo ")
            lora.write(b'radio cw off\r\n')
            print(str(lora.readline()))

            print('cmd> radio set pwr 14')
            lora.write(b'radio set pwr 14\r\n')
            print(str(lora.readline()))

            print('cmd> radio set rxbw 10.4')
            lora.write(b'radio set rxbw 10.4\r\n')
            print(str(lora.readline()))

            print('cmd> radio sf 12')
            lora.write(b'radio set sf sf12\r\n')
            print(str(lora.readline()))

            print('cmd> radio set freq 868000000')
            lora.write(b'radio set freq 868000000\r\n')
            print(str(lora.readline()))

            print('cmd> radio set cr 4/5')
            lora.write(b'radio set cr 4/5\r\n')
            print(str(lora.readline()))

            print('cmd> mac pause')
            lora.write(b'mac pause\r\n')
            print(str(lora.readline()))
            break
            # ---- radio is now set ---------------
        except serial.SerialException or serial.serialutil.SerialException:
            pass
    obc_no = [22, 37]
    t1 = threading.Thread(target=obc, args=(obc_no[0], lora, lock,))
    t2 = threading.Thread(target=obc, args=(obc_no[1], lora, lock,))
    t3 = threading.Thread(target=time_manager)
    # t4 = threading.Thread(target=obc, args=(obc_no[3],))
    t3.start()
   # t1.start()
    t2.start()

    # t4.start()


if __name__ == "__main__":
    main()
