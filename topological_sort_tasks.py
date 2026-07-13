"""
# Topological Task Sorter

## What it is

A utility for ordering project tasks based on prerequisite dependencies using graph
theory concepts:

- **Directed graph** - Tasks are nodes; each prerequisite defines a directed edge
  from the prerequisite task to the dependent task (A must finish before B).
- **Directed Acyclic Graph (DAG)** - A valid project plan contains no cycles;
  topological sorting is only defined on DAGs.
- **Topological sort** - An ordering where every task appears after all of its
  prerequisites. Kahn's algorithm is used: track in-degrees (number of unmet
  prerequisites), repeatedly schedule tasks with in-degree zero, decrement
  dependents, and enqueue newly ready tasks.
- **Cycle detection** - If any tasks remain unscheduled after the queue is
  exhausted, the graph contains a circular dependency and
  `CircularDependencyError` is raised.

## What it is used for

Ordered execution is essential wherever steps must follow a strict sequence:

- **Automated project timelines** - Sequence milestones (design, build, test,
  deploy) for clinic IT rollouts or research study phases.
- **Build systems** - Order compilation or pipeline stages so artifacts build
  before dependents, similar to Make or Bazel task graphs.
- **Milestone trackers** - Validate that a task plan is executable before
  assigning work to teams.
"""

from __future__ import annotations

from collections import deque


class CircularDependencyError(Exception):
    """Raised when task dependencies contain a cycle."""


def topological_sort(tasks: dict[str, list[str]]) -> list[str]:
    """Return a valid execution order for tasks given their prerequisites."""
    all_tasks: set[str] = set(tasks)
    for prerequisites in tasks.values():
        all_tasks.update(prerequisites)

    in_degree = {task: 0 for task in all_tasks}
    dependents: dict[str, list[str]] = {task: [] for task in all_tasks}

    for task, prerequisites in tasks.items():
        in_degree[task] = len(prerequisites)
        for prerequisite in prerequisites:
            dependents[prerequisite].append(task)

    queue = deque(task for task in all_tasks if in_degree[task] == 0)
    order: list[str] = []

    while queue:
        task = queue.popleft()
        order.append(task)
        for dependent in dependents[task]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(all_tasks):
        unresolved = sorted(all_tasks - set(order))
        raise CircularDependencyError(
            f"Circular dependency detected among tasks: {', '.join(unresolved)}"
        )

    return order


if __name__ == "__main__":
    clean_pipeline = {
        "requirements": [],
        "design": ["requirements"],
        "implementation": ["design"],
        "testing": ["implementation"],
        "deployment": ["testing"],
    }

    circular_pipeline = {
        "task_a": ["task_c"],
        "task_b": ["task_a"],
        "task_c": ["task_b"],
    }

    print("Clean project pipeline:")
    print(f"  tasks: {clean_pipeline}")
    print(f"  execution order: {topological_sort(clean_pipeline)}")

    print("\nCircular pipeline:")
    print(f"  tasks: {circular_pipeline}")
    try:
        topological_sort(circular_pipeline)
    except CircularDependencyError as error:
        print(f"  caught error: {error}")
