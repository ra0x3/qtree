import collections
import abc
from typing import *
from objsize import get_deep_size

Primitive = Union[float, str, int, bool]


def str_to_binary(s: bytes) -> bytes:
    return "".join(list("".join([format(b, "b") for b in s]))).encode("utf-8")


def char_at(s: bytes, pos: int) -> Optional[int]:
    try:
        return s[pos]
    except IndexError:
        return None


def append_bpath(b: int, path: bytes) -> bytes:
    ch = b"1" if b == 49 else b"0"
    return path + ch


def is_exclusively_01(s: bytes) -> bool:
    for ch in s:
        if not ch in (48, 49):
            return False
    return True


class LightKey:
    def __init__(self, char: int):
        self.char = char

    def __str__(self):
        return chr(self.char)

    def __eq__(self, other: object):
        if not isinstance(other, LightKey):
            raise NotImplementedError
        return self.char == other.char


class QueryKey:
    def __init__(self, query: bytes):
        self._bin: bytes = str_to_binary(query) if not is_exclusively_01(query) else query

    @property
    def bin(self) -> bytes:
        return self._bin

    # def char_at(self, pos: int) -> Optional[bytes]:
    #     try:
    #         return chr(self._bin[pos]).encode()
    #     except IndexError:
    #         return None

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


class Node(abc.ABC):
    @abc.abstractmethod
    def add_child(self, node):
        raise NotImplementedError

    def is_root(self):
        return self.query == b""

    def is_leaf(self):
        return self.right == self.left == None


class HistoryNode(Node):
    def __init__(self, query: bytes):
        self.query = QueryKey(query)
        self.left: Optional[HistoryNode] = None
        self.right: Optional[HistoryNode] = None

    @property
    def char(self) -> Union[bytes, int]:
        return b"-1" if self.is_root() else self.query.bin[-1]

    def add_child(self, node: "HistoryNode"):
        if node.query.bin[-1] == b"1":
            self.right = node
        else:
            self.left = node


class LightNode(Node):
    def __init__(self, query: int):
        self.query = query
        self.left: Optional[LightNode] = None
        self.right: Optional[LightNode] = None
        self.children = collections.OrderedDict()

    def add_child(self, node: "LightNode"):
        if node.query >= self.query:
            self.right = node
        else:
            self.left = node

    def __eq__(self, other: object):
        if not isinstance(other, (LightNode, int)):
            raise NotImplementedError
        if isinstance(other, LightNode):
            return other.query == self.query
        return other == self.query


default_start_query = 50


class Graph:
    def __init__(self):
        self.root = LightNode(default_start_query)
        self.curr = self.root
        self._node_count: int = 1
        self._query_count: int = 0
        self._last_seek: Optional[LightNode] = None
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

    def add(self, query: bytes):
        self._stats["queries_size_raw_bytes"] += get_deep_size(query)
        self._build_path(query)

    def get(self, query: bytes) -> Optional[LightNode]:
        _ = self._traverse(query)
        copy = self.curr
        return copy

    def reset_root_node(self):
        self.curr = self.root

    def print(self):
        raise NotImplementedError

    def _traverse(self, query: bytes, path: str = "") -> Optional[LightNode]:
        if not self.curr:
            return None

        ch = char_at(query, len(path))
        if ch is None:
            return path

        if ch > self.curr.query:
            self.curr = self.curr.right
        else:
            self.curr = self.curr.left

        return self._traverse(query, path + chr(ch))

    def _build_path(self, query: bytes, pos: int =0, curr: Optional[LightNode] = None, path: str = ""):
        curr = curr or self.root
        ch = char_at(query, pos)
        if ch is None:
            self._query_count += 1
            self.reset_root_node()
            return None

        path = path + chr(ch)
        if ch > curr.query:
            if curr.right is None:
                self._node_count += 1
                curr.right = LightNode(ch)
            curr = curr.right
        else:
            if curr.left is None:
                self._node_count += 1
                curr.left = LightNode(ch)
            curr = curr.left
        self._stats["queries_size_actual_bytes"] += get_deep_size(ch)
        return self._build_path(query, pos + 1, curr, path)

    def __contains__(self, query: bytes) -> bool:
        self._stats["seeks"] += 1
        path = self._traverse(query)
        node = self.curr

        if node is not None and path == query.decode():
            print(node.query, path, query)
            self._stats["hits"] += 1
            self._last_seek = node
            return True

        self._stats["misses"] += 1
        return False
