"""
# Rate Limit Decorator

## What it is

A functional programming wrapper (decorator) that manages per-function call state
over rolling time windows:

- **Decorator factory** - `rate_limit(max_calls, time_window_seconds)` returns a
  decorator that wraps the target callable without changing its signature.
- **Rolling window tracking** - Each wrapped function keeps an in-memory list of
  recent call timestamps (`time.monotonic()`). Before each invocation, timestamps
  older than `time_window_seconds` are discarded.
- **Enforcement** - If the number of remaining timestamps is already
  `>= max_calls`, execution is blocked and `RateLimitExceeded` is raised;
  otherwise the current timestamp is recorded and the wrapped function runs
  normally.
- **Isolated state** - Each decorated function maintains its own timestamp list
  via closure scope (no shared global counter).

## What it is used for

Rate limiting protects systems from overload and accidental runaway traffic:

- **Internal resources** - Cap how often a costly handler runs (e.g. report
  generation, batch exports).
- **Database queues** - Prevent runaway loops from flooding write queues or
  connection pools.
- **Third-party API keys** - Enforce client-side throttling so external provider
  rate limits are not exceeded by spam or retry storms.
"""

from __future__ import annotations

import functools
import time
from collections import deque
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class RateLimitExceeded(Exception):
    """Raised when a decorated function exceeds its allowed call rate."""


def rate_limit(
    max_calls: int,
    time_window_seconds: float,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that limits calls to max_calls per rolling time window."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        call_times: deque[float] = deque()

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            now = time.monotonic()
            cutoff = now - time_window_seconds

            while call_times and call_times[0] <= cutoff:
                call_times.popleft()

            if len(call_times) >= max_calls:
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {max_calls} calls allowed per "
                    f"{time_window_seconds:g} seconds"
                )

            call_times.append(now)
            return func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    @rate_limit(max_calls=3, time_window_seconds=2.0)
    def fetch_patient_record(patient_id: str) -> str:
        return f"record:{patient_id}"

    for attempt in range(1, 6):
        patient_id = f"MRN-{attempt:03d}"
        try:
            result = fetch_patient_record(patient_id)
            print(f"Call {attempt}: {patient_id} -> ok ({result})")
        except RateLimitExceeded as error:
            print(f"Call {attempt}: blocked -> {error}")
