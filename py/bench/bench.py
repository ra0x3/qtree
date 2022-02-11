import os
import sys
import time

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm

from qgraph.qgraph import Node, Graph


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


@timeit
def graph_space_raw_vs_actual():
    g = Graph()
    data = []
    queries = load_queries_txt()
    for q in tqdm(range(len(queries))):
        g.add(q)

        data.append(
            {
                "query_count": g.query_count,
                "node_count": g.node_count,
                "raw_size": g.stats.queries_size_raw_bytes,
                "actual_size": g.stats.queries_size_actual_bytes,
            }
        )

    fig = plt.figure()
    ax = fig.subplots()
    ax.set_title("Stats")
    ax.set_xlabel("Query count")
    ax.set_ylabel("Node count & Raw/Actual size")

    df = pd.DataFrame(data)
    df.plot(ax=ax, colormap="Dark2")

    print(df.tail(10))

    plt.show()


if __name__ == "__main__":

    graph_space_raw_vs_actual()
