import random
import pandas as pd
import csv
import numpy as np


def iou(set1, set2):
    intersection = len(set1.intersection(set2))
    print(f"intersection: {intersection}")

    union = len(set1.union(set2))
    print(f"union: {union}")

    return intersection / union


def get_random():
    # returns a set of 5 random numbers from 1 to 40
    return set(random.sample(range(0, 41), 5))


# now create matrix of 12 kids and 40 cartoons, where 1 is on the index from set and 0 if index is not in set
def matrix_of_kids_and_cartooons(values):
    # create matrix of 12 kids and 40 cartoons, where 1 is on the index from set and 0 if index is not in set
    return [[int(i in child) for i in range(40)] for child in values]


# first child
children = [get_random()]

# the next 11 children which are weakly connected
for i in range(11):
    while True:
        current = get_random()
        for existing in children:
            jaccard = iou(current, existing)
            if jaccard == 0 or jaccard > 0.4:
                break
        else:
            children.append(current)
            break


# the next 11 children which are strongly connected
for i in range(11):
    while True:
        current = get_random()
        for existing in children:
            jaccard = iou(current, existing)
            if 0.6 < jaccard < 0.9:
                break
        else:
            children.append(current)
            break

matrix_of_all_values = matrix_of_kids_and_cartooons(children)

rows = matrix_of_all_values

np.savetxt("jaccard46jaccard9.csv", rows, delimiter=";", fmt='%d')

