from typing import Dict,List
import math as m
import numpy as np
import numpy.linalg as LA
import matplotlib.pyplot as plt
import pickle
import datetime
import random



CABLE_ID = int
HELIO_ID = int
MAX_BRANCH = 16
MAX_LENGTH = 128

OverBranchPunish = 500000
OverLengthPunish = 500000
OverlapPunish = 500000

conductor_price = 100
oct_switch_price = 800
hex_switch_price = 1500
filename = 'positions-PS10.csv'