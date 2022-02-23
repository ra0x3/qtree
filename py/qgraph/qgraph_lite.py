import logging
import json
import sys
from typing import *

logging.basicConfig(
    level=logging.DEBUG,
    filename="qgraph_lite.log",
    format="[%(asctime)s] %(levelname)s PID:%(process)s %(module)s L%(lineno)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("qgraph_lite")

Primitive = Union[float, str, int, bool]


def json_log(d: Dict[str, Any]) -> str:
    return json.dumps(d)


class Children:
    def __init__(self):
        self._items: Dict[TreeNode, TreeNode] = {}
        self.size: int = 30

    def has_capacity(self) -> bool:
        return len(self._items) < self.size

    def __getitem__(self, node: "TreeNode") -> "TreeNode":
        return self._items[node]

    def __setitem__(self, key: "TreeNode", value: "TreeNode"):
        self._items[key] = value

    def get(self, node: "TreeNode") -> Optional["TreeNode"]:
        if node in self:
            return self._items[node]
        return None

    def add(self, node: "TreeNode"):
        if node not in self:
            self._items[node] = node

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, node: "TreeNode") -> bool:
        return node in self._items


class TreeNode:
    def __init__(self, key: int):
        self.key = key
        self.children: Children = Children()

    def __hash__(self) -> int:
        return hash(self.key)

    def is_root(self) -> bool:
        return self.key == 0x2

    def is_leaf(self) -> bool:
        return not self.children

    def __len__(self) -> int:
        return len(self.children)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (int, TreeNode)):
            raise NotImplementedError
        if isinstance(other, TreeNode):
            return other.key == self.key
        return self.key == other

    def __repr__(self) -> str:
        return f"TreeNode({self.key}|{chr(self.key)})"


default_start_query = 0x2


class Tree:
    def __init__(self):
        self.root = self.curr = TreeNode(default_start_query)
        self._node_count: int = 1
        self._query_count: int = 0
        self._last_seek: Optional[TreeNode] = None
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
        logger.debug("Adding new query('%s') with size %dB", query.decode(), len(query))
        self._stats["queries_size_raw_bytes"] += sys.getsizeof(query)
        self._build_path(query)

    def get(self, query: bytes) -> Optional[str]:
        logger.debug("Getting query('%s') in tree", query.decode())
        return self._traverse(query)

    def reset_root_node(self):
        logger.debug("Resetting tree current node to node %s", self.root)
        self.curr = self.root

    def print(self):
        raise NotImplementedError

    def _traverse(self, query: bytes, path: str = "") -> Optional[str]:
        if not self.curr:
            return None
        try:
            ch = query[len(path)]
            node = TreeNode(ch)
            if self.curr.children.has_capacity():
                if node not in self.curr.children:
                    logger.debug("Adding new node %s to %s", node, self.curr)
                    self.curr.children[node] = node
                    self._node_count += 1

                else:
                    logger.debug("Found previously added node %s in node %s", node, self.curr)
                self.curr = self.curr.children[node]

            return self._traverse(query, path + chr(ch))
        except IndexError:
            logger.debug("Found query('%s') in tree", query.decode())
            self.reset_root_node()
            return path

    def _build_path(self, query: bytes, pos: int = 0):
        try:
            ch = query[pos]
            node = TreeNode(ch)
            if self.curr.children.has_capacity():
                if node not in self.curr.children:
                    logger.debug("Adding new node %s to %s", node, self.curr)
                    self.curr.children[node] = node
                    self._node_count += 1
                    self._stats["queries_size_actual_bytes"] += sys.getsizeof(ch)
                else:
                    logger.debug("Skipping previously added node %s in %s", node, self.curr)
                self.curr = self.curr.children[node]
            return self._build_path(query, pos + 1)
        except IndexError:
            logger.debug("Finished adding query('%s') to tree", query.decode())
            self._query_count += 1
            self.reset_root_node()
            return None

    def __contains__(self, query: bytes) -> bool:
        logger.debug("Searching for query('%s') in tree", query.decode())
        self._stats["seeks"] += 1
        _ = self._traverse(query)

        if self.curr is not None:
            self._stats["hits"] += 1
            return True

        self._stats["misses"] += 1
        return False
