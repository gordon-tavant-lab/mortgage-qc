"""
extract_xml.py — thin wrapper over the existing qc_engine/mismo.py.

Returns the sources.mismo side for every in-scope field, for one loan's MISMO
3.4 export. Adds no XML parsing of its own (mismo.py already parses this
project's exact MISMO shape correctly, per research.md decision #2 — extend,
don't duplicate). Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from qc_engine.mismo import parse_mismo  # noqa: E402


def extract_mismo_fields(mismo_path: str) -> Dict[str, str]:
    """Return the flat canonical-field -> system-side value map for one loan's
    MISMO export, exactly as qc_engine/mismo.py's parse_mismo() produces it."""
    return parse_mismo(mismo_path)
