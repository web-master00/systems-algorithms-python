# Systems Algorithms

Three small Python utilities used in backend systems: a fixed-size LRU cache, a sliding-window rate limiter, and a topological sort for task prerequisites.

## Programs

| File | What it does |
| --- | --- |
| `lru_cache.py` | Keeps a bounded cache and evicts the least recently used entry. |
| `rate_limit.py` | Rejects calls that exceed a count inside a time window. |
| `topological_sort_tasks.py` | Orders tasks so each one runs after its prerequisites, and raises if the graph has a cycle. |

## Requirements

- Python 3.10 or newer

## Run

```bash
python lru_cache.py
python rate_limit.py
python topological_sort_tasks.py
```
