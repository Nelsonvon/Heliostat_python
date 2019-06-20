from typing import Dict,List
import math as m
import numpy as np
import numpy.linalg as LA
import matplotlib.pyplot as plt

CABLE_ID = int
HELIO_ID = int
MAX_BRANCH = 16
MAX_LENGTH = 128

filename = '/home/nelson/Dropbox/RWTH/Heuristic optimisation/Project/positions-PS10.csv'

class POS:
    x:float
    y:float
    def __init__(self,x,y):
        self.x = x
        self.y = y
        return


class CABLE:
    h1: HELIO_ID # ID of heliostat
    h2: HELIO_ID
    def __init__(self, h1: HELIO_ID, h2: HELIO_ID):
        self.h1 = h1
        self.h2 = h2
        return

class heliostat:
    pos: POS
    parent: HELIO_ID
    child: List[HELIO_ID]
    size_subtree: int
    def __init__(self, pos:POS):
        self.pos = POS(pos.x,pos.y)
        self.parent = -1
        self.child = []
        self.size_subtree = 1
        return


class Helio_struct: # TODO: 将中心点排除在所有点遍历之外
    cable_dict: Dict[CABLE_ID, CABLE] = {}
    helio_dict: Dict[HELIO_ID, heliostat] = {}
    center_id:HELIO_ID
    def __init__(self):
        self.center_id = 0
        p0 = POS(0,0)
        h0 = heliostat(p0)
        self.helio_dict[0] = h0
        self.get_data()
        print("structure initialize complete")
        return


    def is_feasible(self)->bool:
        if (not self.is_st()):
            return False
        if (self.is_overlap()):
            return False
        if (self.is_overlength()):
            return False
        if (self.is_overdeg()):
            return False
        return True

    def is_st(self)->bool: # check whether it is a spanning tree
        num_nodes = len(self.helio_dict)
        if(self.helio_dict[self.center_id].size_subtree == num_nodes) and (len(self.cable_dict) == num_nodes -1):
            return True
        else:
            return False

    def is_overlap_c2c(self, c1:CABLE, c2:CABLE)->bool:
        A:POS = self.helio_dict[c1.h1].pos
        B:POS = self.helio_dict[c1.h2].pos
        C:POS = self.helio_dict[c2.h1].pos
        D:POS = self.helio_dict[c2.h2].pos
        def vec(p1:POS,p2:POS):
            return np.array([p2.x-p1.x, p2.y-p1.y])
        AC = vec(A,C)
        AD = vec(A,D)
        BC = vec(B,C)
        BD = vec(B,D)
        DA = vec(D,A)
        DB = vec(D,B)
        CA = vec(C,A)
        CB = vec(C,B)

        def equal(p1:POS, p2:POS)->bool:
            if p1.x == p2.x and p1.y == p2.y:
                return True
            else:
                return False
        if equal(A,C) or equal(A,D) or equal(B,C) or equal(B,D):
            return False
        else:
            if(m.sin(LA.norm(AC*AD))*m.sin(LA.norm(BC*BD))<=0 and m.sin(LA.norm(DA*DB))*m.sin(LA.norm(CA*CB))<=0):
                return True
            else:
                return False

    def is_overlap_c(self, c:CABLE)->List[CABLE_ID]:
        overlap_cable: List[CABLE_ID] = []
        for cable_id in self.cable_dict:
            if(self.is_overlap_c2c(self.cable_dict[cable_id],c)):
                overlap_cable.append(cable_id)
        return overlap_cable

    def is_overlap(self)->List:
        overlap_cable_pair: List = []
        for cable1 in self.cable_dict:
            for cable2 in self.cable_dict:
                if cable1 < cable2:
                    if self.is_overlap_c2c(self.cable_dict[cable1],self.cable_dict[cable2]):
                        overlap_cable_pair.append([cable1,cable2])
        return overlap_cable_pair


    def is_overlength(self)->List[HELIO_ID]:
        root_list: List[HELIO_ID] = []
        for h_id in self.helio_dict[self.center_id].child:
            if self.helio_dict[h_id].size_subtree >MAX_LENGTH:
                root_list.append(h_id)
        return root_list

    def is_overdeg(self)->List[HELIO_ID]:
        node_list: List[HELIO_ID] = []
        for h_id in self.helio_dict:
            if len(self.helio_dict[h_id].child)>MAX_BRANCH:
                node_list.append(h_id)
        return node_list

    def is_connect_center(self,h:HELIO_ID):
        if self.helio_dict[h].parent == self.center_id:
            return True
        if self.helio_dict[h].parent == -1:
            return False
        else:
            parent_id = self.helio_dict[h].parent
            return self.is_connect_center(parent_id)

    def get_data(self):
        with open(filename,'r') as fin:
            for line in fin.readlines():
                data = line.split(';')
                x = float(data[0])
                y = float(data[1])
                p = POS(x,y)
                new_hs = heliostat(pos= p)
                self.helio_dict[max(self.helio_dict.keys())+1]= new_hs
        return

    def save_solution(self):
        pass

    def visualise(self):
        x = [h.pos.x for h in self.helio_dict.values()]
        y = [h.pos.y for h in self.helio_dict.values()]
        #ax.plot([0,0],[0,800],c='g') plot cable
        for c in self.cable_dict.values():
            pos1 = self.helio_dict[c.h1].pos
            pos2 = self.helio_dict[c.h2].pos
            x_list = [pos1.x, pos2.x]
            y_list = [pos1.y, pos2.y]
            plt.plot(x_list, y_list,c='g')
        plt.scatter(x,y,s=20 ,c='b')
        plt.scatter([0], [0], [50], c='r')
        plt.show()
        pass

    def load_solution(self):
        pass

    def cal_cost(self)->float:
        pass

    def distance(self, h1:HELIO_ID,h2:HELIO_ID):
        a = self.helio_dict[h1].pos
        b = self.helio_dict[h2].pos
        dist = m.sqrt((a.x-b.x)**2+(a.y-b.y)**2)
        return dist

    def connect_hs(self, a: HELIO_ID, b: HELIO_ID):
        #print(self.helio_dict[b].parent)
        #print("a: {}, b: {}".format(str(a),str(b)))
        if self.helio_dict[b].parent != -1:
            if(not self.set_root_st(b)):
                print("b is connected to the center can't set b as root")
                return False
        self.helio_dict[a].child.append(b)
        self.helio_dict[b].parent = a
        cur_helio:HELIO_ID = a
        while (cur_helio != self.center_id and cur_helio != -1):
            # print("current helio: {}".format(str(cur_helio)))
            self.helio_dict[cur_helio].size_subtree += self.helio_dict[b].size_subtree
            cur_helio = self.helio_dict[cur_helio].parent
        new_cable:CABLE = CABLE(a,b)
        if len(self.cable_dict):
            self.cable_dict[max(self.cable_dict.keys())+1] = new_cable
        else:
            self.cable_dict[1] = new_cable
        return True

    def disconnect_hs(self, a:HELIO_ID, b:HELIO_ID):
        parent_id:HELIO_ID
        child_id:HELIO_ID
        if(self.helio_dict[b].parent == a):
            parent_id = a
            child_id = b
        elif (self.helio_dict[a].parent == b):
            parent_id = b
            child_id = a
        else:
            print("ERROR: a and b are not connected!")
            return False
        self.helio_dict[parent_id].child.remove(child_id)
        cur_helio:HELIO_ID = parent_id
        while((cur_helio != self.center_id) and (cur_helio != -1)):
            self.helio_dict[cur_helio].size_subtree -= self.helio_dict[child_id].size_subtree
            cur_helio = self.helio_dict[cur_helio].parent
        self.helio_dict[child_id].parent = -1

        del_id = 0
        for cable_id in self.cable_dict:
            if(self.cable_dict[cable_id].h1==a and self.cable_dict[cable_id].h2 ==b) or (self.cable_dict[cable_id].h2==a and self.cable_dict[cable_id].h1==b):
                del_id = cable_id
        if del_id:
            del self.cable_dict[del_id]

        return True

    def disconnect_c(self, c:CABLE_ID):
        if c not in self.cable_dict:
            print("ERROR: cable c doesn't exist!")
            return False
        a = self.cable_dict[c].h1
        b = self.cable_dict[c].h2
        parent_id: HELIO_ID
        child_id: HELIO_ID
        if (self.helio_dict[b].parent == a):
            parent_id = a
            child_id = b
        elif (self.helio_dict[a].parent == b):
            parent_id = b
            child_id = a
        else:
            print("ERROR: a and b are not connected!")
            return False
        self.helio_dict[parent_id].child.remove(child_id)
        cur_helio: HELIO_ID = parent_id
        while ((cur_helio != self.center_id) and (cur_helio != -1)):
            self.helio_dict[cur_helio].size_subtree -= self.helio_dict[child_id].size_subtree
            cur_helio = self.helio_dict[cur_helio].parent
        self.helio_dict[child_id].parent = -1

        for cable_id in self.cable_dict:
            if (self.cable_dict[cable_id].h1 == a and self.cable_dict[cable_id].h2 == b) or (
                    self.cable_dict[cable_id].h2 == a and self.cable_dict[cable_id].h1 == b):
                del self.cable_dict[cable_id]

        return True

    def convert_root(self,h:HELIO_ID):
        if(self.helio_dict[h].parent == -1):
            return
        self.convert_root(self.helio_dict[h].parent)
        cap_parent = self.helio_dict[self.helio_dict[h].parent].size_subtree
        cap_child = self.helio_dict[h].size_subtree
        self.helio_dict[self.helio_dict[h].parent].size_subtree = cap_parent - cap_child
        self.helio_dict[self.helio_dict[h].parent].child.remove(h)
        self.helio_dict[self.helio_dict[h].parent].parent = h
        self.helio_dict[h].size_subtree = cap_parent
        pass

    def set_root_st(self,h:HELIO_ID)->bool:
        if(self.is_connect_center(h)):
            return False
        else:
            self.convert_root(h)
            self.helio_dict[self.helio_dict[h].parent] = -1
            return True


helio = Helio_struct()
# for i in helio.helio_dict:
#     if i >0:
#         helio.connect_hs(i-1,i)
# print(helio.is_feasible())
# print(helio.is_overlap())
# print(helio.is_overdeg())
# print(helio.is_overlength())
# print(helio.is_st())
while not helio.is_st():
    print("new epoch")
    for h_id,h in zip(helio.helio_dict.keys(),helio.helio_dict.values()):
        if h_id != helio.center_id and h.parent == -1: # don't handle center
            min_dist = 10000
            parent_id = -1
            for id in helio.helio_dict:
                dist = helio.distance(h_id, id)
                if dist<min_dist and (helio.helio_dict[id].parent != -1 or id == helio.center_id):
                    new_c = CABLE(h_id, id)
                    print("id:{},h_id:{}".format(str(id),str(h_id)))
                    if len(helio.is_overlap_c(new_c))==0:
                        min_dist = dist
                        parent_id = id
            if min_dist < 10000:
                helio.connect_hs(parent_id,h_id)
                # #print("id:{}, id parent:{}, h_id:{}, h_id parent:{}".format(str(parent_id),str(helio.helio_dict[parent_id].parent),
                #                                                             str(h_id), str(helio.helio_dict[h_id].parent)))
            else:
                print("can't find suitable parent")
                print("h_id:{}, h_id parent:{}".format(str(h_id),str(helio.helio_dict[h_id].parent)))

helio.visualise()







