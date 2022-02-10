import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from qgraph import Node, Graph


def plot_node_count_by_query_count():
    queries = ["bloomberg", "nasa", "007", "something else there", "dude"]

    query_count = 5
    g = Graph()
    for (i, q) in enumerate(queries):
        g.add(q)
    x = np.arange(g.query_count)
    y = []
