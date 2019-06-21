from infrastruct import Helio_struct
from infrastruct.algorithms import *

load_model = False
sol_file:str = "/home/nelson/PycharmProjects/Heliostat/infrastruct/2019-06-21 12:10:19.581719.pickle"
"""
Structure Definition
"""
helio = Helio_struct(cable_price=54)

"""
Initialization / loading
"""
if load_model == True:
    helio.load_solution(load_file=sol_file)
else:
    EW_algo2(helio)

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
print(helio.get_cabel_length())
print(helio.get_cost())