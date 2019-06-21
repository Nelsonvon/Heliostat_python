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

def EW_algo2(helio:Helio_struct): #revised tradeoff
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

"""
remove the limitation that each node can only be reconnected once('gates' are actually useless now)
add upper bound of iteration. print result every 200 epochs

TODO:
The trade of should now consider also the control unit of i's parent node, since it's not always the center point
"""
def EW_algo3(helio:Helio_struct, max_epoch = 2000):
    # connnect to the center
    # helio = Helio_struct()
    for i in helio.helio_dict.keys():
        if i != helio.center_id:
            helio.connect_hs(helio.center_id, i)
    # helio.visualise()

    #algo
    have_change = True
    epoch = 0
    while have_change and epoch<max_epoch:
        have_change = False
        t_max= 0
        k = -1
        k_j = -1

        # get t_max
        for i in helio.helio_dict:

            def find_cloest(i: HELIO_ID)->HELIO_ID:
                min_j = -1
                min_distance = 10000
                for j in helio.helio_dict.keys():
                    if j != helio.center_id and j!= i and helio.is_different_subtree(i,j):
                        if helio.distance(i,j)<min_distance:
                            min_distance = helio.distance(i,j)
                            min_j = j
                return min_j

            if i != helio.center_id:
                j = find_cloest(i)
                g_i = helio.distance(i,helio.helio_dict[i].parent)
                c_ij = helio.distance(i,j)

                control_cost = 0
                j_child_num = len(helio.helio_dict[j].child)
                if j_child_num == 0:
                    control_cost += 100
                elif j_child_num == 1:
                    control_cost += 700  # update price from conductor to 8-port
                elif j_child_num == 8:
                    control_cost += 700  # update price from 8-port to 16-port

                if helio.helio_dict[i].parent != helio.center_id:
                    # i's parent is not the center, need to consider the control cost here
                    num_bro = len(helio.helio_dict[helio.helio_dict[i].parent].child)
                    if num_bro == 1:
                        control_cost -= 100 # from conductor to nothing
                    elif num_bro == 2:
                        control_cost -= 700 # from 8-port to conductor
                    elif num_bro == 9:
                        control_cost -= 700 # from 16-port to 8-port

                tradeoff = (g_i - c_ij) * helio.cable_price - control_cost
                if tradeoff > t_max and \
                        ((helio.helio_dict[helio.root_tracer(i)].size_subtree + helio.helio_dict[
                            helio.root_tracer(j)].size_subtree <= MAX_LENGTH)) and \
                        len(helio.is_overlap_c(CABLE(j, i))) == 0 and j_child_num < 16 and \
                        j != helio.helio_dict[i].parent:
                    t_max = tradeoff
                    k = i
                    k_j = j

        if k!= -1 and k_j != -1:
            have_change = True
            helio.disconnect_hs(k, helio.helio_dict[k].parent)
            helio.connect_hs(k_j,k)
        epoch +=1
        if epoch % 40 == 0:
            print("finish epoch {}".format(str(epoch)))
            print("\tLength: {} m".format(str(helio.get_cabel_length())))
            print("\tCost: {}".format(str(helio.get_cost())))
            helio.visualise()
    helio.visualise(save_fig=True)
    helio.save_solution("{}.pickle".format(datetime.datetime.now()))

