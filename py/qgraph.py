import json
from typing import *

from binarytree import build

Primitive = Union[float, str, int, bool]


class Stat:
    def __init__(self, key: str):
        self.key = key
        self._count = 0.0

    def increment(self):
        self.count += 1.0

    def decrement(self):
        self.count -= 1.0

    def percent_of(self, x: float) -> float:
        return self.count / x

    @property
    def count(self) -> float:
        return self._count


def str_to_binary(s: str) -> str:
    return "".join([format(item, "b") for item in bytearray(s, "utf-8")])


class QueryKey:
    def __init__(self, query: str):
        self.query = query
        self.bin = str_to_binary(self.query) if not self._is_binary() else self.query

    def _is_binary(self) -> bool:
        set_ = {"0", "1"}
        s_set = set(self.query)
        return s_set == set_ or s_set in {"0", "1"}

    def __hash__(self):
        return hash(self.bin)

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


class Metadata:
    def __init__(self):
        self.visits = 0
        self.bottiness = 0.0
        self.count = 0

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def __eq__(self, other: object):
        if not isinstance(other, Metadata):
            raise NotImplementedError
        return self.visits == other.visits and self.bottiness == other.bottiness

    def __getitem__(self, key: str) -> Optional[Primitive]:
        return self.__dict__.get(key)

    def __setitem__(self, key: str, value: Primitive):
        self.__dict__[key] = value

    def __str__(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return f"<{json.dumps(self.__dict__)}>"


class QueryObject:
    def __init__(self, key: str):
        self.key = QueryKey(key)
        self.value = Metadata()

    def __len__(self):
        return len(self.key)

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other: object):
        if not isinstance(other, QueryObject):
            raise NotImplementedError
        return other.key == self.key and other.value == self.value

    def __repr__(self):
        return f"({self.key} - {self.value})"


class Node:
    def __init__(self, query: QueryObject):
        self.query = query
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def add_child(self, node: "Node"):
        if node.query.key.bin[-1] == "1":
            self.right = node
            return
        self.left = node

    def is_leaf(self):
        return self.right == self.left == None

    def update_metadata(self, **kwargs):
        self.query.value.update(**kwargs)

    def __repr__(self):
        return f"{self.query.key}"


default_start_key = ""


class GraphStats:
    def __init__(self):
        self.hits: float = 0.0
        self.misses: float = 0.0
        self.seeks: float = 0.0

    @property
    def total(self) -> float:
        return self.hits + self.misses

    def hit(self):
        self.hits += 1.0

    def miss(self):
        self.misses += 1.0

    def seek(self):
        self.seeks += 1.0

    def hit_rate(self):
        return self.hits / self.seeks if self.seeks > 0.0 else 0.0

    def miss_rate(self):
        return self.misses / self.seeks if self.seeks > 0.0 else 0.0


class Graph:
    def __init__(self):
        self.root = Node(QueryObject(default_start_key))
        self.curr = self.root
        self._node_count: int = 1
        self._query_count: int = 0
        self._stats: GraphStats = GraphStats()
        self._last_seek: Optional[Node] = None

    @property
    def node_count(self) -> int:
        return self._node_count

    @property
    def stats(self) -> GraphStats:
        return self._stats

    @property
    def query_count(self) -> int:
        return self._query_count

    def add(self, query: str):
        self._build_path(QueryObject(query))

    def get(self, query: str) -> Optional[Node]:
        qobj = QueryObject(query)
        return self._dfs(qobj)

    def delete(self, query: str):

        _end = self.get(query)

        raise NotImplementedError

    def update_node_metadata(self, query: str, **kwargs):
        node = self.get(query)
        if node:
            node.update_metadata(**kwargs)
        return self.reset_root_node()

    def reset_root_node(self):
        self.curr = self.root

    def level_order(self):
        return self._traverse_level_order()

    def print(self):
        order = self.level_order()
        nodes = [item[1] for item in order]
        keys = [int(key[-1]) if len(key) > 0 else -1 for key in nodes]
        print(build(keys))

    def _traverse_level_order(self) -> List[Tuple[int, str]]:
        result = []
        queue = [(0, self.curr)]

        while queue:
            level, node = queue.pop(0)
            if node is None:
                continue
            result.append((level, str(node.query.key)))
            queue.append((level + 1, node.left))
            queue.append((level + 1, node.right))

        return result

    def _dfs(self, qobj: QueryObject, path: str = "") -> Optional[Node]:
        if len(path) == len(qobj):
            if qobj.key and qobj.key == path:
                node: Node = self.curr
                return node
            return None

        if not self.curr:
            return None

        ch = qobj.key.bin[len(path)]
        if ch == "1":
            self.curr = self.curr.right
        else:
            self.curr = self.curr.left

        return self._dfs(qobj, path + ch)

    def _build_path(self, qobj: QueryObject, pos=0) -> Optional[int]:
        if pos == len(qobj):
            self._query_count += 1
            self.reset_root_node()
        elif pos < len(qobj):
            ch = qobj.key.bin[pos]
            path = QueryObject(qobj.key.bin[: pos + 1])
            if ch == "1":
                if self.curr.right is None:
                    self.curr.right = Node(path)
                self.curr = self.curr.right
            else:
                if self.curr.left is None:
                    self.curr.left = Node(path)
                self.curr = self.curr.left
            self._node_count += 1

            return self._build_path(qobj, pos + 1)
        return None

    def __contains__(self, query: str):
        self._stats.seek()
        qobj = QueryObject(query)
        node = self._dfs(qobj)

        if node is not None:
            self._stats.hit()
            self._last_seek = node
            return True

        self._stats.miss()
        return False
