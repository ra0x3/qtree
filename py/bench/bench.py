import os
import time
import string
import random

import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

from qtree.qtree import Tree, TreeNode


random.seed(49203)

chars = list(string.ascii_letters + string.digits)


def random_query(n=2, m=100):
    x = random.randint(n, m)
    return "".join([random.choice(chars) for _ in range(x)])


def timeit(func):
    def _timeit(*args, **kwargs):
        s = time.time()
        response = func(*args, **kwargs)
        e = time.time()
        print("{}:\t{:.5f}s".format(func.__name__, e - s))
        return response

    return _timeit


@timeit
def query_analysis():
    data = load_queries_random()
    unique = set(data)
    return {
        "count": {
            "total": len(data),
            "unique_count": len(unique),
            "unique_ratio": len(unique) / len(data),
        },
        "len": {
            "shortest": len(min(data, key=len)),
            "longest": len(max(data, key=len)),
            "average": sum([len(item) for item in data]) / len(data),
            "average_unique": sum([len(item) for item in unique]) / len(unique),
        },
    }


@timeit
def load_queries_random(n=1_000_000):
    return [random_query() for _ in range(n)]


@timeit
def load_queries_book():
    data = []
    queries_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "book.txt",
    )
    with open(queries_file, "r") as f:
        for line in f.readlines():
            words = line.split()
            data.extend(words)

    return [query.replace("\n", "") for query in data]


@timeit
def load_queries_txt():
    data = []
    queries_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "queries.txt",
    )
    with open(queries_file, "r") as f:
        data = f.readlines()

    return [query.replace("\n", "") for query in data]


@timeit
def graph_space_raw_vs_actual_tree():
    g = Tree()
    data = []
    queries = load_queries_book()
    unique_queries = set()
    for i in tqdm(range(len(queries))):
        q = queries[i]
        g.add(q.encode())

        unique_queries.add(q)

        data.append(
            {
                "node_count": g.node_count,
                "queries_size_raw_bytes": g.queries_size_raw_bytes,
                "queries_size_actual_bytes": g.queries_size_actual_bytes,
                # "graph_size": get_deep_size(g),
                "query_count": g.query_count,
                "unique_queries": len(unique_queries),
            }
        )

    fig = plt.figure()
    ax = fig.subplots()
    ax.set_title("Stats")
    ax.set_xlabel("Query count")
    ax.set_ylabel("Node count & Raw/Actual size")

    df = pd.DataFrame(data)
    df.plot(ax=ax, secondary_y="queries_size_raw_bytes")

    print(df.tail(10))

    plt.show()


if __name__ == "__main__":

    graph_space_raw_vs_actual_tree()
