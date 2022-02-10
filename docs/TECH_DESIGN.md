# Tech Design

QGraph is a binary search tree that stores abstract queries
    - Every node represents another value (whether bit or byte)
    - At every node you store the value, as well as meta info
        - Meta info: bottyness, rate, etc
    - When the same query comes in again, you match it in the tree
    - Log(n) search time
    - 0(1) insert time

Benefit
    - Qualitative model (to go along with all other models)
    - Fast and more granular analysis
    - Low complecity


Stats to track
- Cache hits vs misses
 - If you don't see a certain cache hit/miss ratio then this will result in worse performance

### Implementation
```python

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
    return ''.join([format(item, 'b') for item in bytearray(s, "utf-8")])


class Key:
    def __init__(self, key: str):
        self.key = key
        self.bin = str_to_binary(self.key)

    def __hash__(self):
        return hash(self.bin)

    def __len__(self):
        return len(self.bin)

    def __eq__(self, other: Union[str, Key]):
        if isinstance(other, Key):
            return self.bin == other.bin
        return other == self.bin

    def __iter__(self):
        for ch in self.bin:
            yield ch


class Metadata:
    def __init__(self):
        self.visits = 0
        self.bottiness = 0.0


class Query:
    def __init__(self, key: str):
        self.key = Key(key)
        self.value = Metadata()

    def update_metadata(self, *args):
        raise NotImplementedError

    def __len__(self):
        return len(self.key)

    def __hash__(self):
        return hash(self.key)


class Node:
    def __init__(self, query: Query):
        self.query = query
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    
    def add_child(self, node: Node):
        if node.key.bin[-1] == "1":
            self.right = node
            return
       self.left = node

    
default_start_key = ""

class Graph:
    def __init__(self):
        self.root = Node(Query(default_start_key))
        self.curr = self.root
        self._seeks = 0.
        self._stats: Dict[str, int] = {
            "cache": {
                "hit": Stat("cache.hit"),
                "miss": Stat("cache.miss"),
            }
        }

    def add(self, key: str):
        """
        g = Graph()
        g.add("iphone 2018")
        g.add("iphone X plus")
        """
        key = Key(key)
        if key in self:
            stat = self._stats["cache"]["hit"]
            return stat.increment()

        query = Query(key)
        self._build_out_for(query)
    
    def get(self, key: str) -> Optional[Metadata]:
        """
        g = Graph()
        node = g.get("foo")
        node.update_metadata(*args)
        """
        query = Query(key)
        return self._traverse_to(query)

    def update_node_metadata(self, key: str, *args):
        raise NotImplementedError

    def cache_hits(self):
        stat = self._stats["cache"]["hit"]
        return stat.percent_of(self._seeks)

    def _traverse_to(self, q: Query, path: str = "") -> Optional[Node]:
        if len(path) == len(q):
            if q.key and q.key == path:
                return self.curr
            return None

        ch = q.key[len(path)]
        if ch == "1":
            self.curr = self.curr.right
            return self._traverse_to(q, path + "1")
        else:
            self.curr = self.curr.left
            return self._traverse_to(q, path + "0")

    def __contains__(self, q: Query):
        node = self._traverse_to(q)
        return node is not None

    def _build_out_for(q: Query, pos = 0) -> Optional[int]:
        while pos < len(q):
            ch = q.key[pos]
            sub_query = Query(q.key[:pos+1])
            if ch == "1":
                if self.curr:
                    self.curr = self.curr.right
                else:
                    self.curr = Node(sub_query)
            else:
                if self.curr:
                    self.curr = self.curr.left
                else:
                    self.curr = Node(sub_query)

            self._build_out_for(q, pos + 1)
```
