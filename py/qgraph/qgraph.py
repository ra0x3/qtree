import collections
from typing import *

Primitive = Union[float, str, int, bool]


def str_to_binary(s: str) -> str:
    return "".join([format(item, "b") for item in bytearray(s, "utf-8")])


def is_binary(s: str) -> bool:
    set_ = {"0", "1"}
    s_set = set(s)
    return s_set == set_ or str(s) in {"0", "1"}


class QueryKey:
    def __init__(self, query: str):
        self._bin = str_to_binary(query) if not is_binary(query) else query
        self.char = "-1" if not query else str_to_binary(query)[-1]

    @property
    def bin(self):
        return self._bin

    def prune(self):
        del self._bin

    def __len__(self):
        return len(self.bin)

    def __eq__(self, other: object):
        if not isinstance(other, (QueryKey, str)):
            raise NotImplementedError
        if isinstance(other, QueryKey):
            return self.bin == other.bin
        return other == self.bin

    def __str__(self):
        return self.bin

    def __iter__(self):
        for ch in self.bin:
            yield ch


Metadata = collections.namedtuple("Metadata", "visits bottiness count")


class Node:
    def __init__(self, query: str):
        self.query = QueryKey(query)
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    @property
    def char(self):
        return "-1" if self.is_root() else self.query.bin[-1]

    def add_child(self, node: "Node"):
        if node.query.bin[-1] == "1":
            self.right = node
            return
        self.left = node

    def is_root(self):
        return self.query == ""

    def is_leaf(self):
        return self.right == self.left == None


default_start_query = ""


class Graph:
    def __init__(self):
        self.root = Node(default_start_query)
        self.curr = self.root
        self._node_count: int = 1
        self._query_count: int = 0
        self._last_seek: Optional[Node] = None
        self._stats: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "seeks": 0,
            "queries_size_raw_bytes": 0,
            "queries_size_actual_bits": 0,
        }

    @property
    def hits(self) -> int:
        return self._stats["hits"]

    @property
    def misses(self) -> int:
        return self._stats["misses"]

    @property
    def seeks(self) -> int:
        return self._stats["seeks"]

    @property
    def queries_size_raw_bytes(self) -> int:
        return self._stats["queries_size_raw_bytes"]

    @property
    def queries_size_actual_bits(self) -> int:
        return self._stats["queries_size_actual_bits"]

    @property
    def node_count(self) -> int:
        return self._node_count

    @property
    def query_count(self) -> int:
        return self._query_count

    def add(self, query: str):
        qkey = QueryKey(query)
        self._stats["queries_size_raw_bytes"] += len(query)
        self._build_path(qkey)

    def get(self, query: str) -> Optional[Node]:
        qkey = QueryKey(query)
        return self._traverse_dfs(qkey)

    def delete(self, query: str):

        _end = self.get(query)

        raise NotImplementedError

    def reset_root_node(self):
        self.curr = self.root

    def print(self):
        raise NotImplementedError

    def _traverse_level(self) -> List[List[str]]:

        result: List[List[str]] = []

        def _traverse(node: Node, level=0):
            if len(result) <= level:
                result.append([])

            result[level].append(str(node))
            if node.left:
                _traverse(node.left, level + 1)
            if node.right:
                _traverse(node.right, level + 1)

        _traverse(self.curr, 0)
        return result

    def _traverse_dfs(self, qkey: QueryKey, path: str = "") -> Optional[Node]:
        if len(path) == len(qkey):
            if qkey and qkey == path:
                node: Node = self.curr
                return node
            return None

        if not self.curr:
            return None

        ch = qkey.bin[len(path)]
        if ch == "1":
            self.curr = self.curr.right
        else:
            self.curr = self.curr.left

        return self._traverse_dfs(qkey, path + ch)

    def _build_path(self, qkey: QueryKey, pos=0, curr: Optional[Node] = None) -> Optional[int]:
        curr = curr or self.root
        if pos == len(qkey):
            self._query_count += 1
            self.reset_root_node()
        elif pos < len(qkey):
            ch = qkey.bin[pos]
            path = qkey.bin[: pos + 1]
            if ch == "1":
                if curr.right is None:
                    self._node_count += 1
                    curr.right = Node(path)
                    self._stats["queries_size_actual_bits"] += 1
                curr = curr.right
            else:
                if curr.left is None:
                    self._node_count += 1
                    curr.left = Node(path)
                    self._stats["queries_size_actual_bits"] += 1
                curr = curr.left
            return self._build_path(qkey, pos + 1, curr)
        return None

    def __contains__(self, query: str):
        self._stats["seeks"] += 1
        qkey = QueryKey(query)
        node = self._traverse_dfs(qkey)

        if node is not None:
            self._stats["hits"] += 1
            self._last_seek = node
            return True

        self._stats["misses"] += 1
        return False
