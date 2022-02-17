import collections
from typing import *

Primitive = Union[float, str, int, bool]

zero: bytes = b"0"
one: bytes = b"1"
two: bytes = b"2"


def str_to_binary(s: bytes) -> bytes:
    return "".join(list("".join([format(b, "b") for b in s]))).encode("utf-8")


def is_exclusively_01(s: bytes) -> bool:
    for ch in s:
        if not ch in (48, 49):
            return False
    return True


class QueryKey:
    def __init__(self, query: bytes):
        self._bin: bytes = str_to_binary(query) if not is_exclusively_01(query) else query

    @property
    def bin(self) -> bytes:
        return self._bin

    def prune(self):
        del self._bin

    def char_at(self, pos: int) -> int:
        return self._bin[pos]

    def slice_to(self, pos: int) -> bytes:
        return self._bin[:pos]

    def __len__(self) -> int:
        return len(self.bin)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (QueryKey, bytes)):
            raise NotImplementedError
        if isinstance(other, QueryKey):
            return self.bin == other.bin
        return other == self.bin

    def __str__(self) -> str:
        return self.bin.decode("utf-8")

    def __iter__(self):
        for ch in self.bin:
            yield ch


Metadata = collections.namedtuple("Metadata", "visits bottiness count")


class Node:
    def __init__(self, query: bytes):
        self.query = QueryKey(query)
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    @property
    def char(self) -> Union[bytes, int]:
        return two if self.is_root() else self.query.bin[-1]

    def add_child(self, node: "Node"):
        if node.query.bin[-1] == one:
            self.right = node
            return
        self.left = node

    def is_root(self):
        return self.query == b""

    def is_leaf(self):
        return self.right == self.left == None


default_start_query = two


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

    def add(self, query: bytes):
        qkey = QueryKey(query)
        self._stats["queries_size_raw_bytes"] += len(query)
        self._build_path(qkey)

    def get(self, query: bytes) -> Optional[Node]:
        qkey = QueryKey(query)
        return self._traverse(qkey)

    def reset_root_node(self):
        self.curr = self.root

    def print(self):
        raise NotImplementedError

    def _traverse(self, qkey: QueryKey, path: bytes = b"") -> Optional[Node]:
        if len(path) == len(qkey):
            if qkey and qkey == path:
                node: Node = self.curr
                return node
            return None

        if not self.curr:
            return None

        ch = qkey.char_at(len(path))
        if ch == 49:
            self.curr = self.curr.right
        else:
            self.curr = self.curr.left

        bch = one if ch == 49 else zero

        return self._traverse(qkey, path + bch)

    def _build_path(self, qkey: QueryKey, pos=0, curr: Optional[Node] = None):
        curr = curr or self.root
        if pos == len(qkey):
            self._query_count += 1
            self.reset_root_node()
        elif pos < len(qkey):
            ch = qkey.char_at(pos)
            path = qkey.slice_to(pos + 1)
            if ch == 49:
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

    def __contains__(self, query: bytes):
        self._stats["seeks"] += 1
        qkey = QueryKey(query)
        node = self._traverse(qkey)

        if node is not None:
            self._stats["hits"] += 1
            self._last_seek = node
            return True

        self._stats["misses"] += 1
        return False
