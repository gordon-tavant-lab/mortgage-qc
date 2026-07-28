"""
002f SC-005/FR-009/FR-010/T018: a static (AST-based) check that
`p0/ontology_extraction/` has zero imports from `p0/qc_engine/`'s
mortgage-specific modules (`ruleset.py`, `engine.py`, `catalog.py`).

FR-010 explicitly REQUIRES `layer2_grounded.py` to import `002c`'s
`knowledge_base.py`/`judge_panel.py` directly (reuse, not reimplement) --
those two are not mortgage-specific (spec.md Assumptions: "already
implementation-generic... no mortgage-specific content"), so this test
enforces the precise, spec-sanctioned shape: zero `qc_engine` imports
anywhere in the package EXCEPT `layer2_grounded.py`, which may import only
`qc_engine.compiler.knowledge_base` and `qc_engine.compiler.judge_panel` --
never `qc_engine.ruleset`, `qc_engine.engine`, or `qc_engine.catalog`.

Python 3.9 compatible.
"""
from __future__ import annotations

import ast
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
_PACKAGE_DIR = os.path.join(_REPO_ROOT, "p0", "ontology_extraction")

_FORBIDDEN_MORTGAGE_SPECIFIC = ("qc_engine.ruleset", "qc_engine.engine", "qc_engine.catalog")
_ALLOWED_QC_ENGINE_IMPORTS = ("qc_engine.compiler.knowledge_base", "qc_engine.compiler.judge_panel")
_SANCTIONED_EXCEPTION_FILE = "layer2_grounded.py"


def _imported_module_names(path: str):
    with open(path) as f:
        tree = ast.parse(f.read(), filename=path)
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
            for alias in node.names:
                names.append(f"{node.module}.{alias.name}")
    return names


def _package_files():
    return sorted(
        os.path.join(_PACKAGE_DIR, fname)
        for fname in os.listdir(_PACKAGE_DIR)
        if fname.endswith(".py")
    )


def test_no_qc_engine_imports_outside_layer2():
    for path in _package_files():
        fname = os.path.basename(path)
        if fname == _SANCTIONED_EXCEPTION_FILE:
            continue
        imports = _imported_module_names(path)
        qc_engine_imports = [m for m in imports if m == "qc_engine" or m.startswith("qc_engine.")]
        assert not qc_engine_imports, (
            f"{fname} must have zero qc_engine imports (FR-009), found: {qc_engine_imports}"
        )


def test_layer2_imports_only_the_two_sanctioned_qc_engine_modules():
    path = os.path.join(_PACKAGE_DIR, _SANCTIONED_EXCEPTION_FILE)
    imports = _imported_module_names(path)
    qc_engine_imports = [
        m for m in imports
        if (m == "qc_engine" or m.startswith("qc_engine."))
        # drop bare intermediate package names a "from X.Y import Z" naturally
        # also emits (e.g. "qc_engine.compiler") -- only the fully-qualified
        # leaf import target is the thing that actually needs sanctioning.
        and not any(other != m and other.startswith(m + ".") for other in imports)
    ]

    for forbidden in _FORBIDDEN_MORTGAGE_SPECIFIC:
        assert forbidden not in qc_engine_imports, (
            f"{_SANCTIONED_EXCEPTION_FILE} must not import mortgage-specific module {forbidden}"
        )

    for m in qc_engine_imports:
        assert m in _ALLOWED_QC_ENGINE_IMPORTS, (
            f"{_SANCTIONED_EXCEPTION_FILE} imports unsanctioned qc_engine module: {m} "
            f"(only {_ALLOWED_QC_ENGINE_IMPORTS} are allowed, per FR-010)"
        )


def test_package_is_importable_standalone():
    """T001's done-when condition: `import ontology_extraction` succeeds
    with `p0/` on the path."""
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, "-c", "import ontology_extraction"],
        cwd=os.path.join(_REPO_ROOT, "p0"),
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
