"""
# LRU Cache System

## What it is

A Least Recently Used (LRU) cache built from scratch by combining two structures:

- **Hash map (`dict`)** - Maps keys to `_Node` references for O(1) lookup: given a
  key, the cache locates the corresponding list node instantly.
- **Doubly linked list** - Maintains usage order from most-recently-used (head) to
  least-recently-used (tail). Each node stores `key`, `value`, `prev`, and `next`.
- **Why together** - A plain dict alone cannot reorder by recency in O(1); a plain
  list requires O(n) moves. Combining them lets `get`/`put` update recency by
  splicing a known node in O(1) while the dict provides O(1) key access.
- **Sentinel nodes** - Dummy head/tail nodes eliminate edge-case branches when
  inserting or removing at boundaries.
- **Eviction** - When size exceeds `capacity`, the node before the tail sentinel
  (LRU end) is removed from both the list and the dict.

## What it is used for

LRU caching optimizes high-frequency system performance:

- **Hot data in memory** - Keep frequently accessed patient configs, session
  tokens, or lookup tables close to the caller.
- **Bounded memory** - Automatically purge stale entries instead of letting
  unbounded caches grow without limit.
- **High-frequency systems** - Reduce repeated database or API fetches for critical
  parameters that recur within a short window.
"""

from __future__ import annotations


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int | str, value: int | str) -> None:
        self.key = key
        self.value = value
        self.prev: _Node | None = None
        self.next: _Node | None = None


class _DoublyLinkedList:
    """Maintains recency order with O(1) insert, remove, and LRU pop."""

    def __init__(self) -> None:
        self._head = _Node(0, 0)
        self._tail = _Node(0, 0)
        self._head.next = self._tail
        self._tail.prev = self._head

    def add_to_front(self, node: _Node) -> None:
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node

    def remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def move_to_front(self, node: _Node) -> None:
        self.remove(node)
        self.add_to_front(node)

    def pop_lru(self) -> _Node:
        lru = self._tail.prev
        self.remove(lru)
        return lru

    def iter_mru_to_lru(self) -> list[_Node]:
        nodes: list[_Node] = []
        current = self._head.next
        while current is not self._tail:
            nodes.append(current)
            current = current.next
        return nodes


class LRUCache:
    """LRU cache with O(1) get and put using a dict plus doubly linked list."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._nodes: dict[int | str, _Node] = {}
        self._order = _DoublyLinkedList()
        self.last_evicted_key: int | str | None = None

    def get(self, key: int | str) -> int | str:
        if key not in self._nodes:
            return -1
        node = self._nodes[key]
        self._order.move_to_front(node)
        return node.value

    def put(self, key: int | str, value: int | str) -> None:
        self.last_evicted_key = None

        if key in self._nodes:
            node = self._nodes[key]
            node.value = value
            self._order.move_to_front(node)
            return

        node = _Node(key, value)
        self._nodes[key] = node
        self._order.add_to_front(node)

        if len(self._nodes) > self._capacity:
            lru = self._order.pop_lru()
            del self._nodes[lru.key]
            self.last_evicted_key = lru.key

    def snapshot(self) -> list[tuple[int | str, int | str]]:
        return [(node.key, node.value) for node in self._order.iter_mru_to_lru()]


def _log(operation: str, cache: LRUCache, note: str = "") -> None:
    state = cache.snapshot()
    suffix = f" | {note}" if note else ""
    print(f"{operation}{suffix}")
    print(f"  state (MRU -> LRU): {state}")


if __name__ == "__main__":
    cache = LRUCache(capacity=2)

    print("LRU Cache Demo (capacity=2)\n")

    cache.put(1, 10)
    _log("PUT 1:10", cache)

    cache.put(2, 20)
    _log("PUT 2:20", cache)

    result = cache.get(1)
    _log("GET 1", cache, f"HIT -> {result}")

    cache.put(3, 30)
    evicted = cache.last_evicted_key
    _log("PUT 3:30", cache, f"EVICTED key={evicted}")

    result = cache.get(2)
    _log("GET 2", cache, f"MISS -> {result}")

    cache.put(4, 40)
    evicted = cache.last_evicted_key
    _log("PUT 4:40", cache, f"EVICTED key={evicted}")
