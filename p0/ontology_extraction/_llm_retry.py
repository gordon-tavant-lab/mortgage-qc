"""
Shared bounded-retry-then-explicit-abstain wrapper (FR-011, Onity precedent):
any Layer 1/2 LLM call that returns malformed/unparseable output retries a
bounded number of times, then returns an explicit failure marker -- never
silently coerced into a guessed "no precondition" or "precondition found"
default.

Deliberately generic (no qc_engine import, no Layer-specific types) so both
`layer1_extraction.py` and `layer2_grounded.py` share one tested
implementation instead of two near-duplicates.

Python 3.9 compatible.
"""
from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeVar

T = TypeVar("T")

DEFAULT_MAX_RETRIES = 2


def call_with_retry(
    call_fn: Callable[[], str],
    parse_fn: Callable[[str], T],
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Tuple[bool, Optional[T], Optional[str]]:
    """Calls `call_fn()` (expected to return raw text, e.g. an LLM response),
    then `parse_fn(raw)` (expected to raise on malformed output). Retries the
    whole call+parse cycle up to `max_retries` additional times on failure.

    Returns `(succeeded, parsed_result_or_None, last_error_or_None)`.
    `succeeded=False` means every attempt failed to parse -- callers must
    treat this as an explicit `parse_failed` proposal state, never fall back
    to a guessed answer."""
    last_error: Optional[str] = None
    for _ in range(max_retries + 1):
        raw = call_fn()
        try:
            return True, parse_fn(raw), None
        except Exception as e:  # noqa: BLE001 -- any parse failure triggers a retry
            last_error = f"{type(e).__name__}: {e}"
    return False, None, last_error
