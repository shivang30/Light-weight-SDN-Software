import datetime


def takesec(elem):
    return elem[1]


nodes_on_earth = [11,9,8,2,4,1,5,0,10,6,7]
path_table = []


def earliest_arrival_time_for_nodes1(tx, src, data, dest):
    nodes1 = []
    eat_nodes = []
    eat_nodes_with_path = []
    for i in range(len(data)):
        if data[i][0] > tx:
            if data[i][1] == src:
                if data[i][2] in nodes_on_earth:
                    pass
                else:
                    nodes1.append(data[i][2])
                    eat_nodes.append(data[i])
                    n1 = data[i][2]
                    tx1 = data[i][0]
                    print(n1, tx1)
                    for j in range(len(data)):
                        if data[j][0] > tx1:
                            if data[j][1] == n1:
                                if data[j][2] == dest:
                                    eat_nodes_with_path.append([data[i], data[j]])
                            elif data[j][2] == n1:
                                if data[j][1] == dest:
                                    eat_nodes_with_path.append([data[i], data[j]])

            elif data[i][2] == src:
                if data[i][1] in nodes_on_earth:
                    pass
                else:
                    nodes1.append(data[i][1])
                    eat_nodes.append(data[i])

                    n2 = data[i][1]
                    tx2 = data[i][0]
                    for k in range(len(data)):
                        if data[k][0] > tx2:
                            if data[k][1] == n2:
                                if data[k][2] == dest:
                                    eat_nodes_with_path.append([data[i], data[k]])
                            elif data[k][2] == n2:
                                if data[k][1] == dest:
                                    eat_nodes_with_path.append([data[i], data[k]])
    return eat_nodes, nodes1, eat_nodes_with_path


def earliest_arrival_time_for_nodes(tx, src, data, dest):
    nodes1 = []
    eat_nodes = []
    for i in range(len(data)):
        if data[i][0] > tx:
            if data[i][1] == src:
                if data[i][2] in nodes_on_earth:
                    pass
                else:
                    nodes1.append(data[i][2])
                    n1 = data[i][2]
                    tx1 = data[i][0]
                    print(n1, tx1)
                    for j in range(len(data)):
                        if data[j][0] > tx1:
                            if data[j][1] == n1:
                                if data[j][2] == dest:
                                    eat_nodes.append([data[i], data[j]])
                            elif data[j][2] == n1:
                                if data[j][1] == dest:
                                    eat_nodes.append([data[i], data[j]])

            elif data[i][2] == src:
                if data[i][1] in nodes_on_earth:
                    pass
                else:
                    nodes1.append(data[i][1])
                    n2 = data[i][1]
                    tx2 = data[i][0]
                    for k in range(len(data)):
                        if data[k][0] > tx2:
                            if data[k][1] == n2:
                                if data[k][2] == dest:
                                    eat_nodes.append([data[i], data[k]])
                            elif data[k][2] == n2:
                                if data[k][1] == dest:
                                    eat_nodes.append([data[i], data[k]])

            # elif data[i][2] == src:
            #     if data[i][1] in nodes1:
            #         temp_time = data[i][0] + data[i][3] - tx
            #         for k in range(len(eat_nodes)):
            #             if data[i][1] == eat_nodes[k][0]:
            #                 if temp_time < eat_nodes[k][1]:
            #                     eat_nodes[k] = [data[i][1], temp_time, data[i]]
            #                 else:
            #                     pass
            #     else:
            #         nodes1.append(data[i][1])
            #         eat_nodes.append([data[i][1], data[i][0] + data[i][3] - tx, data[i]])
    return eat_nodes, nodes1


# def check_for_paths():


def shortest_temporal_path_eap(data, src_node, dest_node, tx):
    nodes = []
    paths = []
    temp_path = []
    x1=0
    for i in range(len(data)):
        if data[i][1] == src_node or data[i][2] == src_node:
            x1 = 1
    if x1 != 1:
        print("src node not available")
        return 0
    else:
        eap_nodes, nodes1, eat_nodes_with_path = earliest_arrival_time_for_nodes1(tx, src_node, data, dest_node)
        if eat_nodes_with_path:
            for b in range(len(eat_nodes_with_path)):
                paths.append(eat_nodes_with_path[b])
        print("eapnodes:", eap_nodes, nodes1, not len(eap_nodes))
        if len(nodes1) == 0:
            print("no possible path available")
        else:
            print("checking if possible path exist using ", nodes1)
            for j in range(len(eap_nodes)):
                if eap_nodes[j][1] == src_node:
                    eap_nodes1, nodes1 = earliest_arrival_time_for_nodes(eap_nodes[j][0], eap_nodes[j][2], data,
                                                                         dest_node)
                    if len(eap_nodes1):
                        for k in range(len(eap_nodes1)):
                            m = len(eap_nodes1[k])
                            if m == 1:
                                paths.append([eap_nodes[j], eap_nodes1[k][0]])
                            if m == 2:
                                paths.append([eap_nodes[j], eap_nodes1[k][0], eap_nodes1[k][1]])
                            if m == 3:
                                paths.append([eap_nodes[j], eap_nodes1[k][0], eap_nodes1[k][1], eap_nodes1[k][2]])
                            if m == 4:
                                paths.append([eap_nodes[j], eap_nodes1[k][0], eap_nodes1[k][1], eap_nodes1[k][2],
                                              eap_nodes1[k][3]])
                            if m == 5:
                                paths.append([eap_nodes[j], eap_nodes1[k][0], eap_nodes1[k][1], eap_nodes1[k][2],
                                              eap_nodes1[k][3], eap_nodes1[k][4]])

            #         print("eapnodes1:", eap_nodes1, nodes1)
            #         print("paths1",paths)
            # for r in range(len(eap_nodes1)):
            #     for q in range(len(eap_nodes1[r])):
            #         if not eap_nodes1[r][q][1] in nodes_on_earth:
            #             if not eap_nodes1[r][q][2] in nodes_on_earth:
            #                 eap_nodes2, nodes2 = earliest_arrival_time_for_nodes(eap_nodes1[r][q][0], eap_nodes1[r][q][1], data,
            #                                                                      dest_node)
            #                 eap_nodes3, nodes3 = earliest_arrival_time_for_nodes(eap_nodes1[r][q][0], eap_nodes1[r][q][2], data,  dest_node)
            #
            #                 if eap_nodes2:
            #                     print("sec iteration",eap_nodes2,nodes2)
            #                 if eap_nodes3:
            #                     print("tghirfdd",eap_nodes3,nodes3)
    return paths


def takeelement(elem):
    return elem[-1]


path_table = {}


def uniquelines(lineslist):
    unique = {}
    result = []
    for item in lineslist:
        if item.strip() in unique: continue
        unique[item.strip()] = 1
        result.append(item)
    return result


def nodeid(node):
    obc_no = 33554432 + node
    OBC_ID = hex(obc_no)
    return OBC_ID


def main():
    data = []
    f = open('pslv_12_reduced_22.dat', 'r')
    data = f.readlines()
    f.close()
    for i in range(len(data)):
        data[i] = data[i].strip()
        temp1, temp2, temp3, temp4 = data[i].split(',')
        temp1 = int(temp1)
        temp2 = int(temp2)
        temp3 = int(temp3)
        temp4 = int(temp4)
        data[i] = [temp1, temp2, temp3, temp4]
    print("data:", data)
    src_node = [1, 5, 0, 10, 6, 7]
    dest_node = [11, 9, 8, 2, 4]
    tx = 0
    all_nodes = []
    for q in range(len(src_node)):
        for w in range(len(dest_node)):
            print("for source destination", src_node[q], dest_node[w])
            paths = shortest_temporal_path_eap(data, src_node[q], dest_node[w], tx)
            if paths==0:
                pass
            else:
                for j in range(len(paths)):
                    tim = 0
                    var1 = 0
                    temp_key = ",".join([str(src_node[q]), str(dest_node[w]), str(paths[j][0])])
                    rem_path = paths[j]
                    for key, value in path_table.copy().items():
                        if key == temp_key:
                            value.append(rem_path)
                            var1 = 1
                    if not var1 == 1:
                        path_table[temp_key] = [rem_path]
                    for k in range(len(paths[j])):
                        print(paths[j])
                        if k == 0:
                            t1 = paths[j][k][0]
                            tim = t1
                        if k == len(paths[j]) - 1:
                            t2 = paths[j][k][0]
                        tim += paths[j][k][3]
                    paths[j].append(tim)
                    paths[j].append(t2 - t1)
                    print("paths", paths)
                for key in path_table:
                    value = path_table[key]
                    value.sort(key=takeelement, reverse=False)
                    for lis in range(len(value) - 1):
                        if value[lis][-1] == value[lis + 1][-1]:
                            if value[lis][-2] < value[lis + 1][-2]:
                                temp = value[lis]
                                value[lis] = value[lis + 1]
                                value[lis + 1] = temp

    print("path table:")
    for key in path_table:
        print(key, ":", path_table[key], "\n")
    nodes = []
    secd_nodes = []
    u = 0
    for key, value in path_table.copy().items():
        split_key = key.split(',')
        src_node = int(split_key[0], 10)
        dest_node = int(split_key[1], 10)
        path = value[0]
        path = path[:-2]
        if len(value) > 1:
            sec_path = value[1]
            sec_path = sec_path[:-2]
        # else:
        #     sec_path=[]
        #     sec_node_id = "0x0000000"

        print("primary path:", path)
        print("secondary path", sec_path)
        for c in range(len(path)):
            if c == 0:
                if path[c][1] == src_node:
                    nodes.append(path[c][2])
                else:
                    nodes.append(path[c][1])
            elif c == len(path) - 1:
                pass
            else:
                if path[c][1] == nodes[-1]:
                    nodes.append(path[c][2])
                else:
                    nodes.append(path[c][1])
        print("nodes on path:", nodes)
        for op in range(len(nodes)):
            all_nodes.append(nodes[op])
        if len(sec_path) == 0:
            print("no secondary path available")
        else:
            for g in range(len(sec_path)):  # [[15611, 1, 37, 145], [36953, 36, 37, 88], [39507, 11, 36, 99]]
                if g == 0:
                    if sec_path[g][1] == src_node:
                        secd_nodes.append(sec_path[g][2])
                    else:
                        secd_nodes.append(sec_path[g][1])
                elif g == len(sec_path) - 1:
                    pass
                else:
                    if sec_path[g][1] == secd_nodes[-1]:
                        secd_nodes.append(sec_path[g][2])
                    else:
                        secd_nodes.append(sec_path[g][1])
            print("nodes on secondary path:", secd_nodes)
        # for op1 in range(len(sec_nodes)):
        #     all_nodes.append(sec_nodes[op1])
        if secd_nodes:
            if nodes == secd_nodes:
                print("no secondary path")
                sec_node_id = "0x0000000"
            else:
                for le in range(len(secd_nodes)):
                    print(secd_nodes[le])
                    print(secd_nodes[le] in nodes)
                    if not secd_nodes[le] in nodes :
                        sec_node_id = nodeid(secd_nodes[le])
                        print("hey")
        else:
            sec_node_id = "0x0000000"
        for z in range(len(path)):
            if z == 0:
                pass
            elif z == len(path) - 1:
                if path[z][1] == nodes[z - 1]:
                    node = path[z][1]
                else:
                    node = path[z][2]
                f = open("control_packets_" + str(node) + ".txt", 'a')
                f.write("2," + str(datetime.timedelta(seconds=path[z][0])) + "," + str(
                    datetime.timedelta(seconds=path[z][0] + path[z][3])) + "," + str(nodeid(src_node)) + "," + str(
                    nodeid(dest_node)) + "," + "1" + "," + str(nodeid(dest_node)) + "," + str(sec_node_id) + ",1\n")
                f.close()
            else:
                if path[z][1] == nodes[z - 1]:
                    node = path[z][1]
                else:
                    node = path[z][2]
                f = open("control_packets_" + str(node) + ".txt", 'a')
                f.write("2," + str(datetime.timedelta(seconds=path[z][0])) + "," + str(
                    datetime.timedelta(seconds=path[z][0] + path[z][3])) + "," + str(nodeid(src_node)) + "," + str(
                    nodeid(dest_node)) + "," + "1," + str(nodeid(nodes[z])) + "," + str(sec_node_id) + ",1\n")
                f.close()
        nodes.clear()
        secd_nodes.clear()
    print(all_nodes)
    for n in all_nodes:
        file1 = open("control_packets_" + str(n) + ".txt", "r")
        filelines = file1.readlines()
        file1.close()
        output = open("control_packets_" + str(n) + ".txt", "w")
        output.writelines(uniquelines(filelines))
        output.close()


if __name__ == "__main__":
    main()
