from infrastruct import Helio_struct
from infrastruct.algorithms import *

pickle_EW1 = "/home/nelson/PycharmProjects/Heliostat/infrastruct/2019-06-21 12:10:19.581719.pickle"
pickle_EW2_54 = "/home/nelson/PycharmProjects/Heliostat/infrastruct/2019-06-21 22:29:48.278477.pickle"
pickle_EW2_29 = "/home/nelson/PycharmProjects/Heliostat/infrastruct/worthy_rlt/06-21 EW_algo2 CableCost29.pickle"
pickle_EW2_14 = "/home/nelson/PycharmProjects/Heliostat/infrastruct/worthy_rlt/06-21 EW_algo2 CableCost14.pickle"

load_model = False
sol_file = ""
"""
Structure Definition
"""
helio = Helio_struct(cable_price=29)

"""
Initialization / loading
"""
if load_model == True:
    helio.load_solution(load_file=sol_file)
else:
    EW_algo3(helio)

"""
Feasibility Checking
"""
# print(helio.is_overdeg())
# print(helio.is_overlength())
# print(helio.is_overlap())
# print(helio.is_st())
print("Solution is feasible: {}".format(str(helio.is_feasible())))
"""
Solution evaluation
"""
print("Length: {} m".format(str(helio.get_cabel_length())))
print("Cost: {}".format(str(helio.get_cost())))