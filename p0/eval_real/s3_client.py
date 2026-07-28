"""
012 Setup (T003) -- a thin, read-only boto3 wrapper over the real closed-loan
extraction bundles already acquired for this feature
(`s3://mortgage-qc-extraction/results/`, per spec.md's Foundation section).

Mirrors `p0/experiment_g3/llm_arm.py`'s existing `PROFILE = 'gordon-chan'`
session-setup pattern rather than inventing a second AWS-auth convention.
Read-only: this module has no write/delete path to the source bucket at all
(only `list_loan_prefixes`/`download_bundle`).

Not part of `pytest p0/tests` -- like `llm_arm.py`, this needs live AWS
credentials this project's own convention keeps out of the default CI/pytest
suite. Use manually (see this feature's quickstart note / README) to fetch a
real bundle into `p0/eval_real/local_cache/` (gitignored, never committed --
FR-012).

Python 3.9 compatible. Requires boto3 + AWS profile 'gordon-chan'.
"""
from __future__ import annotations

import os
from typing import List, Optional

import boto3

REGION = "us-east-1"
PROFILE = "gordon-chan"
BUCKET = "mortgage-qc-extraction"
RESULTS_PREFIX = "results/"

# The 3 already-acquired real loans confirmed in spec.md's Foundation section.
KNOWN_REAL_LOAN_IDS = ["301224293", "301224442", "301224735"]


def _client():
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    return session.client("s3")


def list_loan_prefixes(bucket: str = BUCKET,
                        results_prefix: str = RESULTS_PREFIX) -> List[str]:
    """Read-only: list the top-level loan-id prefixes under
    `s3://{bucket}/{results_prefix}` (e.g. "301224293/")."""
    client = _client()
    resp = client.list_objects_v2(Bucket=bucket, Prefix=results_prefix,
                                   Delimiter="/")
    return [cp["Prefix"] for cp in resp.get("CommonPrefixes", [])]


def download_bundle(loan_id: str, local_dir: str, bucket: str = BUCKET,
                     results_prefix: str = RESULTS_PREFIX) -> List[str]:
    """Read-only: download every object under
    `s3://{bucket}/{results_prefix}{loan_id}/` into `local_dir` (intended
    caller: `p0/eval_real/local_cache/{loan_id}/`, gitignored -- FR-012).
    Returns the list of local file paths written. Never writes back to S3."""
    client = _client()
    loan_prefix = f"{results_prefix}{loan_id}/"
    written: List[str] = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=loan_prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            rel_path = key[len(loan_prefix):]
            if not rel_path:
                continue
            local_path = os.path.join(local_dir, rel_path)
            os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
            client.download_file(bucket, key, local_path)
            written.append(local_path)
    return written
