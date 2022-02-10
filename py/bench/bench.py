import os
import time

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# from qgraph import Node, Graph


def timeit(func):
    def _timeit(*args, **kwargs):
        s = time.time()
        response = func(*args, **kwargs)
        e = time.time()
        print("{}:\t{:.5f}s".format(func.__name__, e - s))
        return response

    return _timeit


def plot_node_count_by_query_count():
    queries = ["bloomberg", "nasa", "007", "something else there", "dude"]

    # query_count = 5
    # g = Graph()
    # for (i, q) in enumerate(queries):
    #     g.add(q)
    # x = np.arange(g.query_count)
    # y = []


@timeit
def load_queries_txt():
    data = []
    queries_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "queries.txt"
    )
    with open(queries_file, "r") as f:
        data = f.readlines()

    return [query.replace("\n", "") for query in data]


if __name__ == "__main__":

    data = load_queries_txt()

    # print(data)
