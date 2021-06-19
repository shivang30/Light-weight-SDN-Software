import binascii
import socket
import serial
from threading import Lock
import threading
import time
import struct
import datetime
import sys
import os
import random
import string
import logging


def get_timenow():
    time_now = datetime.datetime.now()
    date_time = time_now.strftime("%d/%m/%Y %H:%M:%S")
    tim = int(date_time.split(' ')[1].split(':')[0], 10) * 3600 + int(date_time.split(' ')[1].split(':')[1],
                                                                      10) * 60 + int(
        date_time.split(' ')[1].split(':')[2], 10)
    return tim


def time_manager():
    time.sleep(15)
    time_range = []
    f = open('pslv_6_reduced_2.dat', 'r')
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
        temp = temp1 + temp4
        time_range.append((temp1, temp))
    os.system("sudo timedatectl set-time '00:00:00'")
    time_now = datetime.datetime.now()
    date_time = time_now.strftime("%d/%m/%Y %H:%M:%S")
    clk_time = date_time.split(' ')[1]
    print("Starting time:", clk_time)
    print(time_range)
    time.sleep(13)
    for q in range(len(time_range)):
        ts, te = time_range[q]
        print(ts, te)
        tim = get_timenow()
        if tim < ts:
            print(datetime.timedelta(seconds=(ts)))
            os.system("sudo timedatectl set-time " + "'" + str(datetime.timedelta(seconds=(ts))) + "'")
            tim = get_timenow()
            print(tim)
        if te > tim >= ts:
            tim = get_timenow()
            print("time now", tim)
            print("time manager sleeping for", te - tim)
            time.sleep(te - tim)


def end_user(user_no, lora, lock):
    connected_obcs = []

    def nodeid(node):
        no = 33554432 + node
        ID = hex(no)
        return ID

    def access_time():
        tim = []
        f = open('pslv_6_reduced_2.dat', 'r')
        data = f.readlines()
        f.close()
        for i in range(len(data)):
            data[i] = data[i].strip()
            temp1, temp2, temp3, temp4 = data[i].split(',')
            temp1 = int(temp1)
            temp2 = int(temp2)
            temp3 = int(temp3)
            temp4 = int(temp4)
            if temp2 == user_no or temp3 == user_no:
                tim.append((temp1, temp1 + temp4))
        return tim

    t1 = access_time()

    def send(packet):  # packet is struct type
        r = packet.hex()
        temp = 'radio tx ' + r + '\r\n'
        cmd = bytes(temp, 'utf8')
        lock.acquire()
        lora.write(cmd)
        print(user_no, ":", str(lora.readline()))
        print(user_no, ":", str(lora.readline()))
        lock.release()
        return 0

    def packet_handler(pkt, te):  # pkt is the received packet in hexadecimal format
        arr_headers = struct.unpack_from('!s', pkt)  # data packet
        pkt_type = arr_headers[0].decode('utf-8')  # checks the packet type
        if pkt_type == "3":
            print(user_no, ":", "\nPacket is beacon packet")
            unpacked_beacon = struct.unpack("!1si4s1s", pkt)
            src_id = binascii.hexlify(unpacked_beacon[2]).decode()
            src_id = src_id[0] + 'x' + src_id[1:]
            src_id_int = int(src_id, 16)
            obc_no = src_id_int - 33554432
            print(user_no, ":", "checking connected ids", connected_obcs, obc_no)
            if not obc_no in connected_obcs:
                print(user_no, ":", "obu connected.......sending data packets")
                connected_obcs.append(obc_no)
                data_packet_sender(obc_no, te)
            else:
                print(user_no, ":", "connected obc beacon")
        else:
            print("not a beacon packet")

    def get_timenow():
        time_now = datetime.datetime.now()
        date_time = time_now.strftime("%d/%m/%Y %H:%M:%S")
        tim = int(date_time.split(' ')[1].split(':')[0], 10) * 3600 + int(date_time.split(' ')[1].split(':')[1],
                                                                          10) * 60 + int(
            date_time.split(' ')[1].split(':')[2], 10)
        return tim

    def packet_receiver(user_no):
        time.sleep(30)
        print(user_no, ":", "receievr")
        for p in range(len(t1)):
            ts, te = t1[p]
            print(user_no, ":", ts, te)
            tim = get_timenow()
            if tim < ts:
                connected_obcs.clear()
                print(user_no, ":", "conneceted obu", connected_obcs)
                while True:
                    # time.sleep((ts - tim) * 60 + 60)
                    tim = get_timenow()
                    print(tim, ts)
                    if tim > ts:
                        break
            if te > tim >= ts:
                while True:
                    print(user_no, ":", "receive mode", user_no)
                    tim = get_timenow()
                    if tim > te:
                        break
                    lock.acquire()
                    lora.write(b'radio rx 50\r\n')  # radio in receive mode
                    value = lora.readline().strip()
                    print(user_no, ":", "value:", value)
                    if value == "ok" or "radio_tx_ok":
                        raw = str(lora.readline().strip())
                        lock.release()
                        p = raw.split(' ')[0].split("'")[1]
                        if p == 'radio_rx':  # a packet is received by the radio
                            print(user_no, ":", "packet received")
                            packet = ((raw.split(' '))[2]).strip().split("'")[0]
                            decode_packet = bytearray.fromhex(packet)  # decodes packet from hex format to string
                            print("sending to packet handler")
                            packet_handler(decode_packet, te)
                        else:
                            print(user_no, ":", "No packet received")

    def send(packet):  # packet is struct type
        r = packet.hex()
        temp = 'radio tx ' + r + '\r\n'
        cmd = bytes(temp, 'utf8')
        lock.acquire()
        lora.write(cmd)
        print(user_no, ":", str(lora.readline()))
        print(user_no, ":", str(lora.readline()))
        lock.release()
        return 0

    def data_packet_sender(obc_no, te):
        gsu_table = {"5": [3, 8, 9, 11], "1": [11, 9, 8, 3, 6], "0": [3, 8, 9, 11], "2": [3, 9, 11]}
        for key, value in gsu_table.items():
            node = int(key, 10)
            if node == user_no:
                gsus = value
        no_pkt = 1
        var1 = 0
        while True:
            if var1 >= len(gsus):
                var1 = 0
            letters = string.ascii_lowercase
            pkt_type = bytes("1", 'utf-8')
            time_stamp = get_timenow()
            ID = nodeid(user_no).replace('x', '')
            src_id = bytes.fromhex(ID)
            GSU_ID = nodeid(var1)
            ID = GSU_ID.replace('x', '')
            dest_id = bytes.fromhex(ID)
            size = 140 - len(str(no_pkt))
            content = bytes(str(no_pkt) + ''.join(random.choice(letters) for i in range(len(str(no_pkt)) + size)),
                            'utf-8')
            data_len = len(content)
            data_packet = struct.pack('!1si4s4si' + str(data_len) + 's', pkt_type, time_stamp, src_id, dest_id,
                                      data_len, content)  # 15 bytes header ..rest data bytes
            print(user_no, ":", "\nSending data packet-", no_pkt)
            print(user_no, ":", "\nSending data-", data_packet, " till ", te)
            send(data_packet)
            no_pkt += 1
            var1 += 1
            tim = get_timenow()
            if tim > te:
                print("breaking time out")
                break
        send_info.append((obc_no, no_pkt, datetime.datetime.now()))
        return 0

    send_info = []
    t2 = threading.Thread(target=packet_receiver, args=(user_no,))
    t2.start()
    f = open('pslv_6_reduced_2.dat', 'r')
    data = f.readlines()
    last_link = data[-1].strip().split(',')
    last_link_time = int(last_link[0], 10) + int(last_link[3], 10)
    print(user_no, ":", "Last link time", last_link_time)
    while True:
        if get_timenow() > last_link_time:
            print(user_no, ":", "Send info:::", send_info)
            break


def main():
    lock = Lock()
    lora = serial.Serial(port="/dev/ttyAMA0", baudrate=57600)

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
    user_no = [5, 1, 0, 2]
    t3 = threading.Thread(target=time_manager)
    t3.start()
    t4 = threading.Thread(target=end_user, args=(user_no[0], lora, lock,))
    t4.start()
    t5 = threading.Thread(target=end_user, args=(user_no[1], lora, lock,))
    t5.start()
    t6 = threading.Thread(target=end_user, args=(user_no[2], lora, lock,))
    t6.start()
    t7 = threading.Thread(target=end_user, args=(user_no[3], lora, lock,))
    t7.start()


if __name__ == "__main__":
    main()

# Exceptions to consider:
# exception struct.error
# Runtime error
