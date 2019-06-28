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
            if j_child_num == 1:
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

The trade of should now consider also the control unit of i's parent node, since it's not always the center point
"""
def EW_algo3(helio:Helio_struct, max_epoch = 1000):
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
                if j_child_num == 1:
                    control_cost += 700  # update price from conductor to 8-port
                elif j_child_num == 8:
                    control_cost += 700  # update price from 8-port to 16-port

                if helio.helio_dict[i].parent != helio.center_id:
                    # i's parent is not the center, need to consider the control cost here
                    num_bro = len(helio.helio_dict[helio.helio_dict[i].parent].child)
                    if num_bro == 2:
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
        if epoch % 100 == 0:
            print("finish epoch {}".format(str(epoch)))
            print("\tLength: {} m".format(str(helio.get_cabel_length())))
            print("\tCost: {}".format(str(helio.get_cost())))
            helio.visualise()
    helio.visualise(save_fig=True)
    helio.save_solution("{}.pickle".format(datetime.datetime.now()))


# TODO: Randomize EW_algo3

# TODO: Randomized local search disconnect-reconnect
# TODO: Disconnect-Reconnect with simulated annealing
def dis_reconnnect(helio:Helio_struct, max_epoch:int=1000):
    # TO*DO: discard simulated annealing parameters
    # alpha = 0.8
    # t_max = 200000 # approximation of Delta_C_max
    # t_min = 1
    # l_b = 40 # Not determined yet
    # c_min = helio.get_cost()
    # c_max = c_min
    # t = t_max
    epoch = 0
    epoch_no_improve = 0
    terminate = False
    while epoch<max_epoch and not terminate: # TO*DO: change terminate condition
        # select disconnect point randomly
        disconnect_point = random.choice(list(helio.helio_dict.keys()))
        while disconnect_point == helio.center_id:
            disconnect_point = random.choice(list(helio.helio_dict.keys()))
        parent = helio.helio_dict[disconnect_point].parent
        helio.disconnect_hs(disconnect_point,parent)

        # get list of reconnect candidates
        candidate_list = [disconnect_point]
        for child in helio.helio_dict[disconnect_point].child:
            candidate_list.append(child)
            for grandchild in helio.helio_dict[child].child:
                candidate_list.append(grandchild)

        # calculate cost for each candidates
        # !! Avoid the original solution
        candidate_cost:Dict = {}
        """
        for every candidate reconnection node, find the optimal feasible solution, if no solution is feasible, return id = -1
        """
        def get_reconnect_cost(root:HELIO_ID, reconnect_point:HELIO_ID)->(float,HELIO_ID): # TO*DO: cost of neighbours
            min_cost = 10000
            reconnect_parent = -1
            reconnect_control_cost = 0
            num_child_reconnect = len(helio.helio_dict[reconnect_point].child)+1
            if num_child_reconnect ==2:
                reconnect_control_cost = 700 # reconnection: from conductor to 8-port
            if num_child_reconnect == 9:
                reconnect_control_cost = 700 # from 8-port to 16-port
            for h in helio.helio_dict:
                is_feasible = False
                if helio.distance(reconnect_point,h)*helio.cable_price<min_cost:  # possible better solution
                    if len(helio.helio_dict[h].child)<16 or h == helio.center_id: # not overbranch
                        if helio.is_different_subtree(h,reconnect_point):         # not in the same subtree
                            cable:CABLE = CABLE(h,reconnect_point)
                            if not helio.is_overlap_c(cable):                     # new cable do not overlap with others
                                if h == helio.center_id:                          # h is the center, don't need to consider over-length/branch problem
                                    is_feasible = True
                                elif helio.helio_dict[helio.root_tracer(h)].size_subtree + helio.helio_dict[root].size_subtree <= 128:
                                    is_feasible = True
                if is_feasible:
                    """
                    cable_cost
                    control_cost
                    """
                    cable_cost = helio.distance(reconnect_point,h)*helio.cable_price
                    h_child_num = len(helio.helio_dict[h].child)
                    control_cost = 0
                    if h_child_num==1:
                        control_cost = 700 # from conductor to 8-port
                    if h_child_num == 8:
                        control_cost = 700 # from 8-port to 16-port
                    curr_cost = cable_cost+control_cost
                    if curr_cost < min_cost:
                        min_cost = curr_cost
                        reconnect_parent = h
            return min_cost+reconnect_control_cost, reconnect_parent

        for candidate in candidate_list:
            if len(helio.helio_dict[candidate].child)<16:
                cost,new_parent = get_reconnect_cost(disconnect_point,candidate)
                if (candidate != disconnect_point or new_parent != parent) and new_parent != -1:
                    candidate_cost[candidate] = [cost,new_parent]


        # TO*DO: restrict the candidates list and randomly select solution
        alpha = 0.2 # restrict coefficient of GRASP
        if len(candidate_cost)>0:
            minus_dist = helio.distance(disconnect_point, parent)
            minus_control_parent = 0
            if len(helio.helio_dict[parent].child) == 1:
                minus_control_parent = 700  # from 8-port to conductor
            if len(helio.helio_dict[parent].child) == 8:
                minus_control_parent = 700  # from 16-port to 8-port
            # TODO: Fix the computation of cost change
            minus_control_stroot = 0
            if len(helio.helio_dict[disconnect_point].child)==2:
                minus_control_stroot = 700 # root from 8-port to 16-port
            if len(helio.helio_dict[disconnect_point].child) == 9:
                minus_control_stroot = 700
            minus_cost = minus_control_parent + minus_dist*helio.cable_price + minus_control_stroot

            c_min = min([l[0] for l in candidate_cost.values()])
            c_max = max([l[0] for l in candidate_cost.values()])
            c_th = min([c_min + alpha*(c_max-c_min),minus_cost])
            restricted_candidate_list = {}
            for candidate in candidate_cost:
                if candidate_cost[candidate][0] <= c_th:
                    new_parent = candidate_cost[candidate][1]
                    restricted_candidate_list[candidate] = new_parent
            if len(restricted_candidate_list) >0:
                decision = random.choice(list(restricted_candidate_list.keys()))
            # TO*DO: Update tree structure
                # perform update
                # print("reconnect:{}-{}".format(str(restricted_candidate_list[decision]),str(decision)))
                # print(helio.helio_dict)
                helio.connect_hs(restricted_candidate_list[decision],decision)
                # print(helio.helio_dict)
                epoch_no_improve = 0
            else:
                epoch_no_improve +=1
                # print("epoch {} has no improvement".format(str(epoch)))
                helio.connect_hs(parent,disconnect_point)
        else:
            epoch_no_improve +=1
            helio.connect_hs(parent,disconnect_point)
            # print("epoch {} has no feasible solution".format(str(epoch)))

        # TO9DO: update parameter
        if epoch_no_improve == 100:
            terminate = True

        if epoch % 40 == 0:
            helio.visualise()
            print("finish epoch {}".format(str(epoch)))
            print("\tLength: {} m".format(str(helio.get_cabel_length())))
            print("\tCost: {}".format(str(helio.get_cost())))
        # print("is feasible: {}".format(str(helio.is_feasible())))
        epoch += 1
    helio.save_solution("{}.pickle".format(datetime.datetime.now()))
    helio.visualise(save_fig=True)



