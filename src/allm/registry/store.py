"""Append-only JSONL registry for reproducible runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from allm.domain.models import Run, RunStatus


class RunRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, run: Run) -> None:
        run.validate()
        existing = {item.run_id for item in self.list()}
        if run.run_id in existing:
            raise ValueError(f"run already exists: {run.run_id}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(run.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")

    def append_once(self, run: Run) -> Run:
        """Append a run, or return the existing identical run on a safe retry."""
        try:
            existing = self.get(run.run_id)
        except KeyError:
            self.append(run)
            return run
        expected = run.to_dict()
        actual = existing.to_dict()
        expected.pop("created_at", None)
        actual.pop("created_at", None)
        if actual != expected:
            raise ValueError(f"run ID exists with different metadata: {run.run_id}")
        return existing

    def list(self) -> list[Run]:
        if not self.path.exists():
            return []
        runs: list[Run] = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    value = json.loads(line)
                    value["status"] = RunStatus(value["status"])
                    runs.append(Run(**value))
        return runs

    def get(self, run_id: str) -> Run:
        for run in self.list():
            if run.run_id == run_id:
                return run
        raise KeyError(run_id)

    def completed(self) -> Iterable[Run]:
        return (run for run in self.list() if run.status is RunStatus.COMPLETED)

    def assert_lineage(
        self,
        run_id: str,
        *,
        dataset_hash: str,
        tokenizer_hash: str,
        evaluation_hash: str,
    ) -> None:
        """Ensure a recorded run points to the exact artifacts being reviewed."""
        run = self.get(run_id)
        expected = (dataset_hash, tokenizer_hash, evaluation_hash)
        actual = (run.dataset_hash, run.tokenizer_hash, run.evaluation_hash)
        if actual != expected:
            raise ValueError(f"lineage mismatch for {run_id}")
