
import datetime
import serial
import sys
import time
import threading
from threading import Lock
import encodings
import sqlite3
import struct
import socket
import random
import string
import binascii
import os
import logging
import random
flag=0

def get_timenow():
    time_now = datetime.datetime.now()
    date_time = time_now.strftime("%d/%m/%Y %H:%M:%S")
    tim = int(date_time.split(' ')[1].split(':')[0], 10) * 3600 + int(date_time.split(' ')[1].split(':')[1], 10)*60 + int(date_time.split(' ')[1].split(':')[2], 10)
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
        ts=ts-30
        print(ts, te)
        tim = get_timenow()
        if tim < ts:
            s_tim = str(datetime.timedelta(seconds=(ts)))
            print("before time set:", tim)
            os.system("sudo timedatectl set-time " + "'" + s_tim + "'")
            tim = get_timenow()
            print("<ts.........after time set:", s_tim, tim)
            while True:
#                print(get_timenow())
                if get_timenow() > ts:
                    break
        tim = get_timenow()
        print("current time ", tim, "ts te", ts, te)
        if tim < te and tim >= ts:
            tim = get_timenow()
            print(">ts.........")
            while True:
 #               print(get_timenow())
                if get_timenow() > te:
                    break


def gsu(gsu_no,lora,lock):
    flag = 0
    no_bcn_rcv = 0
    no_data_pkt_rcv = 0
    # logging.basicConfig(filename='gsu'+str(gsu_no)+'.log', filemode='w',format='%(gsu_no)-%(asctime)s - %(message)s', level=logging.INFO)
    data_send_info=[]
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
            if temp2 == gsu_no or temp3 == gsu_no:
                tim.append((temp1, temp1 + temp4))
        return tim

    def nodeid(node):
        no = 33554432 + node
        ID = hex(no)
        return ID

    t1 = access_time()
    print(get_timenow(),":",gsu_no,":","access_time:",t1)

    gsu_id = nodeid(gsu_no)

    connected_obcs = []

    def packet_handler(pkt,te):  # pkt is the received packet in hexadecimal format
        arr_headers = struct.unpack_from('!s', pkt)  # data packet
        pkt_type = arr_headers[0].decode('utf-8')  # checks the packet type
        if pkt_type == "1":
            # no_data_pkt_rcv += 1
            print(get_timenow(),":",gsu_no,":","\nPacket is data type..............................................................................",no_data_pkt_rcv)
            data_packet_store(pkt)

        if pkt_type == "3":
            print(get_timenow(),":",gsu_no,":","\nPacket is beacon packet")
            unpacked_beacon = struct.unpack("!1si4s1s", pkt)
            src_id = binascii.hexlify(unpacked_beacon[2]).decode()
            src_id = src_id[0] + 'x' + src_id[1:]
            src_id_int = int(src_id, 16)
            obc_no=src_id_int-33554432
            print(get_timenow(),":",gsu_no,":","checking connected ids", connected_obcs, obc_no)
            if not obc_no in connected_obcs:
                print(get_timenow(),":",gsu_no,":","obu connected.......sending control packets")
                connected_obcs.append(obc_no)
                control_packet_sender(obc_no,te)
            else:
                print(get_timenow(),":",gsu_no,":","connected obc beacon")

    # function to store the packets
    def data_packet_store(pkt):
        connection1 = sqlite3.connect("data_packets_database"+str(gsu_no)+".db")
        cursor1 = connection1.cursor()
        arr_headers = struct.unpack_from('!1si4s4si', pkt)  # data packet
        data_len = arr_headers[4]
        arr = struct.unpack('!1si4s4si' + str(data_len) + 's', pkt)
        send_time=arr[1]
        cursor1.execute("INSERT INTO data_packets VALUES(?,?,?)", (pkt,get_timenow(),send_time))
        connection1.commit()
        print(get_timenow(),":",gsu_no,":","Data Packet Stored")
        connection1.close()



    def packet_receiver(gsu_id):
        time.sleep(30)
        for p in range(len(t1)):
            ts, te = t1[p]
            print(gsu_no,":Receiver access time- ",ts, te)
            tim = get_timenow()
            if tim < ts:
                connected_obcs.clear()
                flag = 0
                print(get_timenow(),":",gsu_no,":","conneceted obu", connected_obcs)
                print(get_timenow(),":",gsu_no,":","waiting", (ts - tim))
                while True:
                    # time.sleep((ts - tim) * 60 + 60)
                    tim = get_timenow()
                    if tim > ts:
                        break
            if te > tim >= ts:
                while True:
                    tim = get_timenow()
                    if tim > te:
                        break
                    lock.acquire()
                    lora.write(b'radio rx 50\r\n')  # radio in receive mode
                    value = lora.readline().strip()
                    print(get_timenow(),":",gsu_no,":","value:", value)
                    if value == "ok" or "radio_tx_ok":
                        raw = str(lora.readline().strip())
                        lock.release()
                        p = raw.split(' ')[0].split("'")[1]
                        if p == 'radio_rx':  # a packet is received by the radio
                            print(get_timenow(),":",gsu_no,":","packet received")
                            packet = ((raw.split(' '))[2]).strip().split("'")[0]
                            decode_packet = bytearray.fromhex(packet)  # decodes packet from hex format to string
                            packet_handler(decode_packet,te)
                        else:
                            print(get_timenow(),":",gsu_no,":","No packet received")

    def send(packet):  # packet is struct type
        r = packet.hex()
        temp = 'radio tx ' + r + '\r\n'
        cmd = bytes(temp, 'utf8')
        lock.acquire()
        lora.write(cmd)
        print(get_timenow(),":",gsu_no,":",str(lora.readline()))
        print(get_timenow(),":",gsu_no,":",str(lora.readline()))
        lock.release()
        return 0

    def bytes_id(id):
        ID = id.replace('x', '')
        bytes_id = bytes.fromhex(ID)
        return bytes_id

    def get_sec(time_str):
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)

    def control_packet_sender(obc_no,te):
        global flag
        j = 0
       
        if obc_no <= 11 or obc_no > 44:
            print(get_timenow(),":",gsu_no,":","unknown obc connected")
        while True:
            if get_timenow()>te:
                break
            fil = open("control_packets_" + str(obc_no) + ".txt", 'r+')
            all_lines = fil.readlines()
            fil.seek(0, 0)
            line = fil.readline()
            print(get_timenow(),":",gsu_no,":",line)
            if line.strip() == "":  # if line is empty, end of file is reached
                print(get_timenow(),":",gsu_no,":","\nFinished sending the control packets", bytes(line, 'utf-8'))
                flag = 1
                break
            packet = str(line.strip())
            print(get_timenow(),":",gsu_no,":","Line in the file:", packet)
            pkt_type, time1, time2, src_id, dest_id, op_id,prm_next_id,sec_next_id,act = packet.split(',')
            pkt_type = bytes(pkt_type, 'utf-8')
            time1 = get_sec(time1)
            time2 = get_sec(time2)
            src_id =bytes_id(src_id)
            dest_id = bytes_id(dest_id)
            prm_next_id=bytes_id(prm_next_id)
            sec_next_id=bytes_id(sec_next_id)
            op_id = bytes(str(op_id), 'utf-8')
            act = bytes(act, 'utf-8')
            control_packet = struct.pack('!1sii4s4s1s4s4s1s', pkt_type, time1, time2, src_id, dest_id, op_id,prm_next_id,sec_next_id,act)
            print(get_timenow(),":",gsu_no,":","\nSending control packet-", j)
            print(get_timenow(),":",gsu_no,":","\nSending data-", control_packet)
            # conn.send(control_packet)
            send(control_packet)
            time.sleep(1)
            send(control_packet)
            fil.close()
            del all_lines[0]
            open("control_packets_" + str(obc_no) + ".txt", 'w').close()
            fil = open("control_packets_" + str(obc_no) + ".txt", 'w')
            for i in range(len(all_lines)):
                fil.write(str(all_lines[i]))
            j += 1
        data_send_info.append((obc_no,j,get_timenow()))
        return 0

    def beacon_sender(gsu_id):
        time.sleep(30)
        global flag
        for p in range(len(t1)):
            ts, te = t1[p]
            print(gsu_no,":beacon sender acces time",ts, te)
            tim = get_timenow()
            if tim < ts:
                connected_obcs.clear()
                flag = 0
                print(get_timenow(),":",gsu_no,":","conneceted obu", connected_obcs)
                print(get_timenow(),":",gsu_no,":","waiting", (ts - tim) )
                while True:
                    # time.sleep((ts - tim) * 60 + 60)
                    tim = get_timenow()
                    if tim>ts:
                        break
            if te > tim >= ts:
                no_bcn_snd = 0
                print(get_timenow(),":",gsu_no,":","Sending beacons...")
                pkt_type = bytes("3", 'utf-8')
                ID = gsu_id.replace('x', '')
                src_id = bytes.fromhex(ID)
                while True:  # while loop for periodic transmission
                    if get_timenow()>te:
                        flag=0
                        break
                    clk_time = get_timenow()
                    beacon = struct.pack("!1si4s1s", pkt_type, clk_time, src_id, bytes(str(flag),'utf-8'))
                    r = beacon.hex()
                    temp = 'radio tx ' + r + '\r\n'
                    cmd = bytes(temp, 'utf8')
                    lock.acquire()
                    lora.write(cmd)
                    print(get_timenow(),":",gsu_no,":",str(lora.readline()))
                    print(get_timenow(),":",gsu_no,":",str(lora.readline()))
                    lock.release()
                    # no_bcn_snd += 1
                    print(get_timenow(),":",gsu_no,":","beacon sent with flag",flag)
                    time.sleep(random.choice([3,5,7]))


          # ----- connecting and creating database --------------
   # connection1 = sqlite3.connect("data_packets_database"+str(gsu_no)+".db")
   # cursor1 = connection1.cursor()
   # cursor1.execute("CREATE TABLE data_packets (data_packet BLOB,reception_time INTEGER,send_time INTEGER )")
   # connection1.close()
    # -----------------------------------------------------
    print(get_timenow(),":",gsu_no,":","Created Database")

    # -----------Threads---------
    t6 = threading.Thread(target=beacon_sender, args=(gsu_id,))
    t6.start()
    t2 = threading.Thread(target=packet_receiver, args=(gsu_id,))
    t2.start()
    f = open('pslv_12_reduced_21.dat', 'r')
    data = f.readlines()
    last_link = data[-1].strip().split(',')
    last_link_time = int(last_link[0], 10) + int(last_link[3], 10)
    print(gsu_no, ":", "Last link time", last_link_time)
    while True:
        time.sleep(120)
        if get_timenow() > last_link_time:
            file=open("results"+ str(gsu_no) +".txt",'w')
            for ele in data_send_info:
                file.write(str(ele)+",")
            print(gsu_no, ":", "Send info:::", data_send_info)
            file.close()
            print("finished..........................................")
            break

    # ---------------------------


def main():
    lock = Lock()
    lora = serial.Serial(port="/dev/ttyS0", baudrate=57600)
    while True:
        # radio commands for setting up the LoRa radio
        try:
            print('cmd> radio cw off')
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
    gsu_no = [11 ,9 ,8 ,3 ,6]
    t3 = threading.Thread(target=time_manager)
    t3.start()
    t4 = threading.Thread(target=gsu, args=(gsu_no[0],lora,lock,))
    t4.start()
    t5 = threading.Thread(target=gsu, args=(gsu_no[1],lora,lock,))
    t5.start()
    t6 = threading.Thread(target=gsu, args=(gsu_no[2],lora,lock,))
    t6.start()
    t7 = threading.Thread(target=gsu, args=(gsu_no[3],lora,lock,))
    t7.start()
    t8 = threading.Thread(target=gsu, args=(gsu_no[4], lora, lock,))
    t8.start()


if __name__ == "__main__":
    main()
