from infrastruct import *
from infrastruct.Helio_struct import POS, CABLE, Helio_struct, heliostat

def EW_algo(helio:Helio_struct):
    # connnect to the center
    gates: List= []
    # helio = Helio_struct()
    for i in helio.helio_dict.keys():
        if i != helio.center_id:
            helio.connect_hs(helio.center_id, i)
            gates.append(i)
    # helio.visualise()

    #algo
    have_change = True
    epoch = 0
    while have_change:
        have_change = False
        t_max= 0
        k = -1
        k_j = -1

        # get t_max
        for i in gates:
            def find_cloest(i: HELIO_ID)->HELIO_ID:
                min_j = -1
                min_distance = 10000
                for j in helio.helio_dict.keys():
                    if j != helio.center_id and j!= i and helio.is_different_subtree(i,j):
                        if helio.distance(i,j)<min_distance:
                            min_distance = helio.distance(i,j)
                            min_j = j
                return min_j

            j = find_cloest(i)
            g_i = helio.distance(i,helio.center_id)
            c_ij = helio.distance(i,j)
            if g_i - c_ij > t_max and ((helio.helio_dict[helio.root_tracer(i)].size_subtree + helio.helio_dict[helio.root_tracer(j)].size_subtree<= MAX_LENGTH)) and len(helio.is_overlap_c(CABLE(j,i)))==0:
                t_max = g_i - c_ij
                k = i
                k_j = j
        if k!= -1 and k_j != -1:
            have_change = True
            helio.disconnect_hs(k, helio.center_id)
            helio.connect_hs(k_j,k)
            gates.remove(k)
        epoch +=1
        print("finish epoch {}".format(str(epoch)))
    helio.visualise(save_fig=True)
    helio.save_solution("{}.pickle".format(datetime.datetime.now()))

def EW_algo2(helio:Helio_struct):
    # connnect to the center
    gates: List= []
    # helio = Helio_struct()
    for i in helio.helio_dict.keys():
        if i != helio.center_id:
            helio.connect_hs(helio.center_id, i)
            gates.append(i)
    # helio.visualise()

    #algo
    have_change = True
    epoch = 0
    while have_change:
        have_change = False
        t_max= 0
        k = -1
        k_j = -1

        # get t_max
        for i in gates:
            def find_cloest(i: HELIO_ID)->HELIO_ID:
                min_j = -1
                min_distance = 10000
                for j in helio.helio_dict.keys():
                    if j != helio.center_id and j!= i and helio.is_different_subtree(i,j):
                        if helio.distance(i,j)<min_distance:
                            min_distance = helio.distance(i,j)
                            min_j = j
                return min_j

            j = find_cloest(i)
            g_i = helio.distance(i,helio.center_id)
            c_ij = helio.distance(i,j)

            control_cost = 0
            j_child_num = len(helio.helio_dict[j].child)
            if j_child_num == 0:
                control_cost = 100
            elif j_child_num == 1:
                control_cost = 700  # update price from conductor to 8-port
            elif j_child_num == 8:
                control_cost = 700  # update price from 8-port to 16-port

            tradeoff = (g_i - c_ij) * helio.cable_price - control_cost
            if tradeoff > t_max and \
                    ((helio.helio_dict[helio.root_tracer(i)].size_subtree + helio.helio_dict[
                        helio.root_tracer(j)].size_subtree <= MAX_LENGTH)) and \
                    len(helio.is_overlap_c(CABLE(j, i))) == 0 and j_child_num < 16:
                t_max = tradeoff
                k = i
                k_j = j

        if k!= -1 and k_j != -1:
            have_change = True
            helio.disconnect_hs(k, helio.center_id)
            helio.connect_hs(k_j,k)
            gates.remove(k)
        epoch +=1
        print("finish epoch {}".format(str(epoch)))
    helio.visualise(save_fig=True)
    helio.save_solution("{}.pickle".format(datetime.datetime.now()))
