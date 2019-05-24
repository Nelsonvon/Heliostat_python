from typing import Dict,List
import math as m
import numpy as np
import numpy.linalg as LA
import matplotlib.pyplot as plt

CABLE_ID = int
HELIO_ID = int
MAX_BRANCH = 16
MAX_LENGTH = 128

filename = ''

class POS:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        return
    x:float
    y:float

class CABLE:
    h1: HELIO_ID # ID of heliostat
    h2: HELIO_ID

class heliostat:
    def __init__(self, pos:POS):
        self.pos.x = pos.x
        self.pos.y = pos.y
        self.parent = -1
        self.child = []
        self.size_subtree = 1
        return
    pos:POS
    parent: HELIO_ID
    child: List[HELIO_ID]
    size_subtree: int

class Helio_struct: # TODO: 将中心点排除在所有点遍历之外
    cable_dict: Dict[CABLE_ID, CABLE]
    helio_dict: Dict[HELIO_ID, heliostat]
    center:heliostat
    center_id:HELIO_ID
    def __init__(self):
        self.get_data()
        self.center_id = 0
        p0 = POS(0,0)
        h0 = heliostat(p0)
        self.helio_dict[0] = h0
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

    def is_st(self)->bool:
        num_nodes = len(self.helio_dict)
        if(self.helio_dict[self.center_id].size_subtree == num_nodes) and (len(self.cable_dict) == num_nodes -1):
            return True
        else:
            return False

    def is_overlap_c2c(self, c1:CABLE_ID, c2:CABLE_ID)->bool:
        A:POS = self.helio_dict[self.cable_dict[c1].h1].pos
        B:POS = self.helio_dict[self.cable_dict[c1].h2].pos
        C:POS = self.helio_dict[self.cable_dict[c2].h1].pos
        D:POS = self.helio_dict[self.cable_dict[c2].h2].pos
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
        if(m.sin(LA.norm(AC*AD))*m.sin(LA.norm(BC*BD))<=0 and m.sin(LA.norm(DA*DB))*m.sin(LA.norm(CA*CB))<=0):
            return True
        else:
            return False

    def is_overlap_c(self, c:CABLE_ID)->List[CABLE_ID]:
        overlap_cable: List[CABLE_ID] = []
        for cable_id in self.cable_dict:
            if(self.is_overlap_c2c(cable_id,c)):
                overlap_cable.append(cable_id)
        return overlap_cable

    def is_overlap(self)->List:
        overlap_cable_pair: List = []
        for cable1 in self.cable_dict:
            for cable2 in self.cable_dict:
                if cable1 < cable2:
                    if self.is_overlap_c2c(cable1,cable2):
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
                new_hs = heliostat(POS = p)
                self.helio_dict[max(self.helio_dict.keys())+1]= new_hs
        return

    def save_solution(self):
        pass

    def visualise(self):
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

    def connect_hs(self,a: HELIO_ID, b: HELIO_ID):
        if self.helio_dict[self.helio_dict[b].parent] != -1:
            if(not self.set_root_st(b)):
                print("b is connected to the center can't set b as root")
                return False
        self.helio_dict[a].child.append(b)
        self.helio_dict[b].parent = a
        cur_helio:HELIO_ID = a
        while (cur_helio != self.center_id):
            self.helio_dict[cur_helio].size_subtree += self.helio_dict[b].size_subtree
            cur_helio = self.helio_dict[cur_helio].parent
        new_cable:CABLE
        new_cable.h1 = a
        new_cable.h2 = b
        self.cable_dict[max(self.cable_dict.keys())+1] = new_cable
        return True

    def disconnect_hh(self, a:HELIO_ID, b:HELIO_ID):
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

        for cable_id in self.cable_dict:
            if(self.cable_dict[cable_id].h1==a and self.cable_dict[cable_id].h2 ==b) or (self.cable_dict[cable_id].h2==a and self.cable_dict[cable_id].h1==b):
                del self.cable_dict[cable_id]

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








