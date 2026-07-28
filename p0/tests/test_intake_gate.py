"""
002c -- intake gate (US5, FR-011): halt on an unknown document type.

Run from p0/:  python -m pytest tests/test_intake_gate.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.compiler import intake as I


KNOWN_TYPES = {"AMQ_WORKBOOK", "HUD_HANDBOOK_EXCERPT", "SELLING_GUIDE_EXCERPT"}


# --- T031: an unknown document type halts, never silently proceeds --------
def test_unknown_document_type_halts():
    try:
        I.classify_and_gate("SOME_NEW_INVESTOR_GUIDELINE_PDF", KNOWN_TYPES)
        assert False, "expected UnknownDocumentTypeError"
    except I.UnknownDocumentTypeError as e:
        assert "SOME_NEW_INVESTOR_GUIDELINE_PDF" in str(e)


def test_known_document_type_proceeds():
    # No exception -- intake may continue.
    I.classify_and_gate("AMQ_WORKBOOK", KNOWN_TYPES)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
