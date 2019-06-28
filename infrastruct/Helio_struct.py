from infrastruct import *



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


class Helio_struct:
    cable_dict: Dict[CABLE_ID, CABLE] = {}
    helio_dict: Dict[HELIO_ID, heliostat] = {}
    center_id:HELIO_ID
    def __init__(self, cable_price:float=0):
        self.cable_price = cable_price
        self.center_id = 0
        p0 = POS(0,0)
        h0 = heliostat(p0)
        self.helio_dict[self.center_id] = h0
        self.get_data()
        print("structure initialize complete\n")
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
        rlt = True
        sum_nodes = 1
        for h_id in self.helio_dict:
            h = self.helio_dict[h_id]
            if h.parent == -1 and h_id != self.center_id:
                rlt = False
                print("non-connected subtree: {}".format(str(h_id)))
            if h.parent == self.center_id:
                sum_nodes += h.size_subtree
        if sum_nodes != num_nodes:
            rlt = False
        if(len(self.cable_dict) != num_nodes -1):
            rlt = False

        return rlt

    def is_overlap_c2c(self, c1:CABLE, c2:CABLE)->bool:
        def equal(p1:POS, p2:POS)->bool:
            if p1.x == p2.x and p1.y == p2.y:
                return True
            else:
                return False

        A:POS = self.helio_dict[c1.h1].pos
        B:POS = self.helio_dict[c1.h2].pos
        C:POS = self.helio_dict[c2.h1].pos
        D:POS = self.helio_dict[c2.h2].pos

        if (equal(A,C) and equal(B,D)) or (equal(A,D) and equal(B,C)):
            print("cable 1 = cable 2!")
            return False
        if equal(A, C) or equal(A, D) or equal(B, C) or equal(B, D):
            return False
        x1 = A.x
        y1 = A.y
        x2 = B.x
        y2 = B.y
        x3 = C.x
        y3 = C.y
        x4 = D.x
        y4 = D.y
        # print(x1,y1,x2,y2,x3,y3,x4,y4)
        def lineIntersectside(A,B,C,D):
            fc = (C.y-A.y)*(A.x-B.x)-(C.x-A.x)*(A.y-B.y)
            fd = (D.y-A.y)*(A.x-B.x)-(D.x-A.x)*(A.y-B.y)
            if fc*fd >0:
                return False
            else:
                return True
        denom = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
        if denom == 0: # parallel
            # print("case1")
            return False
        else:
           if (not lineIntersectside(A,B,C,D)) or (not lineIntersectside(C,D,A,B)):
               return False
           else:
               return True

        # def vec(p1:POS,p2:POS):
        #     return np.array([p2.x-p1.x, p2.y-p1.y])
        # AC = vec(A,C)
        # AD = vec(A,D)
        # BC = vec(B,C)
        # BD = vec(B,D)
        # DA = vec(D,A)
        # DB = vec(D,B)
        # CA = vec(C,A)
        # CB = vec(C,B)
        #
        #
        # if equal(A,C) or equal(A,D) or equal(B,C) or equal(B,D):
        #     return False
        # else:
        #     #if(m.sin(LA.norm(AC*AD))*m.sin(LA.norm(BC*BD))<=0 and m.sin(LA.norm(DA*DB))*m.sin(LA.norm(CA*CB))<=0):
        #     if np.dot(AC,AD)*np.dot(BC,BD)<=0 and np.dot(DA,DB)*np.dot(CA,CB)<=0:
        #         return True
        #     else:
        #         return False

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
            if len(self.helio_dict[h_id].child)>MAX_BRANCH and h_id != self.center_id:
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

    def save_solution(self, save_file: str):
        cables = []
        for c in self.cable_dict.keys():
            h1 = self.cable_dict[c].h1
            h2 = self.cable_dict[c].h2
            cables.append([h1, h2])
        with open(save_file, 'wb') as fout:
            pickle.dump(cables,fout,pickle.HIGHEST_PROTOCOL)
        return

    def visualise(self, save_fig:bool= False):
        for h in self.helio_dict.values():
            if isinstance(h, int):
                print(h)
        x = [h.pos.x for h in self.helio_dict.values()]
        y = [h.pos.y for h in self.helio_dict.values()]
        ids = self.helio_dict.keys()
        #subtree = [h.size_subtree for h in self.helio_dict.values()]
        #ax.plot([0,0],[0,800],c='g') plot cable
        for c in self.cable_dict.values():
            pos1 = self.helio_dict[c.h1].pos
            pos2 = self.helio_dict[c.h2].pos
            x_list = [pos1.x, pos2.x]
            y_list = [pos1.y, pos2.y]
            plt.plot(x_list, y_list,linewidth = 0.1,c='g')
        plt.scatter(x,y,s=1 ,c='b')

        # for x,y,id in zip(x,y,ids):
        #     plt.annotate('%s' %id, xy=[x,y])
        plt.scatter([0], [0], [25], c='r')
        if save_fig:
            plt.savefig('{}.eps'.format(datetime.datetime.now()), format='eps', dpi=1000)
        plt.show()
        pass

    def load_solution(self, load_file:str):
        with open(load_file,'rb') as fin:
            cables = pickle.load(fin)
        for pair in cables:
            h1 = pair[0]
            h2 = pair[1]
            self.connect_hs(h1,h2)
        return


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

        del_id = -1
        for cable_id in self.cable_dict:
            if(self.cable_dict[cable_id].h1==a and self.cable_dict[cable_id].h2 ==b) or (self.cable_dict[cable_id].h2==a and self.cable_dict[cable_id].h1==b):
                del_id = cable_id
        if del_id != -1:
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
        parent = self.helio_dict[h].parent
        self.helio_dict[parent].size_subtree = cap_parent - cap_child
        self.helio_dict[parent].child.remove(h)
        self.helio_dict[parent].parent = h
        self.helio_dict[h].child.append(parent)
        self.helio_dict[h].size_subtree = cap_parent
        pass

    def set_root_st(self,h:HELIO_ID)->bool:
        if(self.is_connect_center(h)):
            return False
        else:
            self.convert_root(h)
            self.helio_dict[h].parent = -1
            return True

    def root_tracer(self, h:HELIO_ID):
        cur_h = h
        while (self.helio_dict[cur_h].parent!= self.center_id and self.helio_dict[cur_h].parent != -1):
            cur_h = self.helio_dict[cur_h].parent
        return cur_h

    def is_different_subtree(self, h1: HELIO_ID, h2: HELIO_ID)-> bool:
        # get the root of the subtrees and compare
        cur_h = h1
        while (self.helio_dict[cur_h].parent!= self.center_id and self.helio_dict[cur_h].parent != -1):
            cur_h = self.helio_dict[cur_h].parent
        h1_root = cur_h
        cur_h = h2
        while (self.helio_dict[cur_h].parent != self.center_id and self.helio_dict[cur_h].parent != -1):
            cur_h = self.helio_dict[cur_h].parent
        h2_root = cur_h
        if h1_root == h2_root:
            return False
        else:
            return True

    def get_cabel_length(self)->float:
        sum_length = 0
        for c_id in self.cable_dict:
            h1 = self.cable_dict[c_id].h1
            h2 = self.cable_dict[c_id].h2
            p1 = self.helio_dict[h1].pos
            p2 = self.helio_dict[h2].pos
            length = m.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2)
            sum_length += length
        return sum_length

    def get_cost(self)->float:
        def get_cost_iter(h:HELIO_ID)->float:
            if self.helio_dict[h].size_subtree==1:
                return conductor_price
            else:
                child_size = len(self.helio_dict[h].child)
                # TODO: So far no checking on the number of child
                sum_subtree_size = 1
                for h_child in self.helio_dict[h].child:
                    sum_subtree_size += self.helio_dict[h_child].size_subtree
                if sum_subtree_size != self.helio_dict[h].size_subtree:
                    print("ERROR: Sum of size from children doesn't match subtree size, h={}"
                          "Sum = {}, subtree_size={}".format(str(h),str(sum_subtree_size),str(self.helio_dict[h].size_subtree)))
                # finished checking

                # control unit cost
                if  child_size <= 1:
                    sum_cost = conductor_price
                elif child_size <= 8:
                    sum_cost = oct_switch_price
                elif child_size <= 16:
                    sum_cost = hex_switch_price
                else:
                    print("Warnning: Heliostat {} over branching".format(str(h)))
                    sum_cost = OverBranchPunish

                for h_child in self.helio_dict[h].child:
                    sum_cost += get_cost_iter(h_child)
                    sum_cost += self.cable_price*self.distance(h_child,h)
                return sum_cost
        cost = 0
        for gate in self.helio_dict[self.center_id].child:
            cost += get_cost_iter(gate)
            cost += self.cable_price * self.distance(gate, self.center_id)
        return cost




