import json
from typing import *

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
        return s_set == set_ or s_set == {"0"} or s_set == {"1"}

    def __hash__(self):
        return hash(self.bin)

    def __len__(self):
        return len(self.bin)

    def __eq__(self, other: Union[str, "QueryKey"]):
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

    def __eq__(self, other: "Metadata"):
        return self.visits == other.visits and self.bottiness == other.bottiness

    def __getitem__(self, key: str) -> Optional[Primitive]:
        return self.__dict__.get(key)

    def __setitem__(self, key: str, value: Primitive):
        self.__dict__[key] = value

    def __str__(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return "<{}>".format(json.dumps(self.__dict__))


class QueryObject:
    def __init__(self, key: str):
        self.key = QueryKey(key)
        self.value = Metadata()

    def __len__(self):
        return len(self.key)

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other: "QueryObject"):
        return other.key == self.key and other.value == self.value

    def __repr__(self):
        return "({} - {})".format(self.key, self.value)


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

    def update_metadata(self, **kwargs):
        self.query.value.update(**kwargs)

    def __repr__(self):
        return "{}".format(self.query.key)


default_start_key = ""


def reset_root_node(func):
    def _wrapper(cls: "Graph", *args, **kwargs):
        result = func(cls, *args, **kwargs)
        cls.reset_curr()
        return result

    return _wrapper


class Graph:
    def __init__(self):
        self.root = Node(QueryObject(default_start_key))
        self.curr = self.root
        self._node_count = 1
        self._query_count = 0

    @property
    def node_count(self) -> int:
        return self._node_count

    @property
    def query_count(self) -> int:
        return self._query_count

    def add(self, query: str):
        self._build_path(QueryObject(query))

    def get(self, query: str) -> Optional[Metadata]:
        qobj = QueryObject(query)
        return self._dfs(qobj)

    def update_node_metadata(self, query: str, **kwargs):
        node = self.get(query)
        if node:
            node.update_metadata(**kwargs)
        return self.reset_root_node()

    def reset_root_node(self):
        self.curr = self.root

    def print(self):
        order = self._traverse_level_order()
        return order

    def _traverse_level_order(self) -> List[Node]:
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
                return self.curr
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

    def __contains__(self, query: str):
        qobj = QueryObject(query)
        node = self._dfs(qobj)
        return node is not None
