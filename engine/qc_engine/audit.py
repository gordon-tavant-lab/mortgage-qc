"""
Immutable, cryptographically-chained audit log.

Judge ruling #9: S3 Object Lock gives WORM (you can't delete it) but NOT
verifiability-of-history — you can't prove the sequence was never tampered. QLDB
is end-of-support, so we build the hash chain ourselves and (in prod) anchor it
in Object Lock. Here it lands in SQLite so the P0 is fully runnable offline.

Each audit record hashes: the prior record's hash + the run's canonical content
(loan id, ruleset hash + version, engine version, and the full per-check field
intermediates). Tampering with any historical record breaks every subsequent
hash — that's the "prove the math was never changed" story an examiner wants.

Python 3.9 compatible.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any, Dict, List, Optional

from .engine import RunResult

GENESIS = "0" * 64


def _digest(prev_hash: str, payload: Dict[str, Any]) -> str:
    blob = (prev_hash + json.dumps(payload, sort_keys=True,
            separators=(",", ":"))).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


class AuditLog:
    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_runs (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_id TEXT NOT NULL,
                ruleset_sha256 TEXT NOT NULL,
                ruleset_version INTEGER NOT NULL,
                engine_version TEXT NOT NULL,
                signed_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                record_hash TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def _last_hash(self) -> str:
        row = self.conn.execute(
            "SELECT record_hash FROM audit_runs ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else GENESIS

    def append(self, run: RunResult, signed_at: str) -> str:
        """Append an immutable, chained audit record. Returns the record hash.

        `signed_at` is injected (never wall-clock inside the deterministic
        path) so the engine stays a pure function and runs stay reproducible.
        """
        payload = run.to_dict()
        payload["signed_at"] = signed_at
        prev = self._last_hash()
        rec_hash = _digest(prev, payload)
        self.conn.execute(
            """INSERT INTO audit_runs (loan_id, ruleset_sha256,
               ruleset_version, engine_version, signed_at, payload_json,
               prev_hash, record_hash) VALUES (?,?,?,?,?,?,?,?)""",
            (run.loan_id, run.ruleset_sha256, run.ruleset_version,
             run.engine_version, signed_at, json.dumps(payload, sort_keys=True),
             prev, rec_hash),
        )
        self.conn.commit()
        return rec_hash

    def verify_chain(self) -> bool:
        """Recompute every link; return False if any record was tampered."""
        prev = GENESIS
        for row in self.conn.execute(
            "SELECT payload_json, prev_hash, record_hash FROM audit_runs "
            "ORDER BY seq ASC"
        ):
            payload_json, stored_prev, stored_hash = row
            if stored_prev != prev:
                return False
            payload = json.loads(payload_json)
            if _digest(prev, payload) != stored_hash:
                return False
            prev = stored_hash
        return True

    def records(self) -> List[Dict[str, Any]]:
        out = []
        for row in self.conn.execute(
            "SELECT seq, loan_id, ruleset_sha256, signed_at, record_hash "
            "FROM audit_runs ORDER BY seq ASC"
        ):
            out.append({"seq": row[0], "loan_id": row[1],
                        "ruleset_sha256": row[2], "signed_at": row[3],
                        "record_hash": row[4]})
        return out

    def close(self) -> None:
        self.conn.close()
