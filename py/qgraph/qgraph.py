import json
from typing import *

Primitive = Union[float, str, int, bool]


def str_to_binary(s: str) -> str:
    return "".join([format(item, "b") for item in bytearray(s, "utf-8")])


class QueryKey:
    def __init__(self, query: str):
        self.query = str(query)
        self.bin = str_to_binary(self.query) if not self._is_binary() else self.query

    def _is_binary(self) -> bool:
        set_ = {"0", "1"}
        s_set = set(self.query)
        x = s_set == set_ or self.query in {"0", "1"}
        return x

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
        return self.key


class Node:
    def __init__(self, query: QueryObject):
        self.query = query
        self.char = "-1" if self.is_root() else self.query.key.bin[-1]
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def add_child(self, node: "Node"):
        if node.query.key.bin[-1] == "1":
            self.right = node
            return
        self.left = node

    def is_root(self):
        return self.query.key.query == ""

    def is_leaf(self):
        return self.right == self.left == None

    def update_metadata(self, **kwargs):
        self.query.value.update(**kwargs)

    def __repr__(self):
        return f"{self.query.key}"


default_start_key = ""


class Graph:
    def __init__(self):
        self.root = Node(QueryObject(default_start_key))
        self.curr = self.root
        self._node_count: int = 1
        self._query_count: int = 0
        self._last_seek: Optional[Node] = None
        self._stats: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "seeks": 0,
            "queries_size_raw_bytes": 0,
            "queries_size_actual_bytes": 0,
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
    def queries_size_actual_bytes(self) -> int:
        return self._stats["queries_size_actual_bytes"]

    @property
    def node_count(self) -> int:
        return self._node_count

    @property
    def query_count(self) -> int:
        return self._query_count

    def add(self, query: str):
        qobj = QueryObject(query)
        self._stats["queries_size_raw_bytes"] += len(qobj)
        self._build_path(qobj)

    def get(self, query: str) -> Optional[Node]:
        qobj = QueryObject(query)
        return self._traverse_dfs(qobj)

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

    def _traverse_dfs(self, qobj: QueryObject, path: str = "") -> Optional[Node]:
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

        return self._traverse_dfs(qobj, path + ch)

    def _build_path(self, qobj: QueryObject, pos=0, curr: Optional[Node] = None) -> Optional[int]:
        curr = curr or self.root
        if pos == len(qobj):
            self._query_count += 1
            self.reset_root_node()
        elif pos < len(qobj):
            ch = qobj.key.bin[pos]
            path = QueryObject(qobj.key.bin[: pos + 1])
            if ch == "1":
                if curr.right is None:
                    self._node_count += 1
                    curr.right = Node(path)
                    self._stats["queries_size_actual_bytes"] += 1
                curr = curr.right
            else:
                if curr.left is None:
                    self._node_count += 1
                    curr.left = Node(path)
                    self._stats["queries_size_actual_bytes"] += 1
                curr = curr.left
            return self._build_path(qobj, pos + 1, curr)
        return None

    def __contains__(self, query: str):
        self._stats["seeks"] += 1
        qobj = QueryObject(query)
        node = self._traverse_dfs(qobj)

        if node is not None:
            self._stats["hits"] += 1
            self._last_seek = node
            return True

        self._stats["misses"] += 1
        return False
