# apps/blue_hesab/blue_hesab/bh_core/regress/reporting.py
from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from blue_hesab.bh_core.versioning import get_schema_version


@dataclass
class CaseResult:
    name: str
    pass_: bool
    ts: str
    ms: int
    error: Optional[str] = None
    tb: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def run_cases(
    *,
    suite: str,
    company: str,
    cases: Iterable[Callable[[], Any]],
    run_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    cases: iterable of callables. Each callable may:
      - return dict(meta)
      - return True/False
      - raise Exception
    """
    started = time.time()
    results: list[CaseResult] = []

    for fn in cases:
        name = getattr(fn, "__name__", "case")
        t0 = time.time()
        try:
            out = fn()
            meta: dict[str, Any] | None = None
            ok = True

            if isinstance(out, bool):
                ok = out
            elif isinstance(out, dict):
                meta = out
                # allow dict to include "pass"
                if "pass" in out:
                    ok = bool(out["pass"])
            elif out is None:
                ok = True
            else:
                meta = {"return": repr(out)}

            results.append(
                CaseResult(
                    name=name,
                    pass_=ok,
                    ts=_utc_now_iso(),
                    ms=int((time.time() - t0) * 1000),
                    meta=meta,
                    error=None if ok else (meta.get("error") if meta else "FAILED"),
                )
            )
        except Exception as e:
            results.append(
                CaseResult(
                    name=name,
                    pass_=False,
                    ts=_utc_now_iso(),
                    ms=int((time.time() - t0) * 1000),
                    error=str(e),
                    tb=traceback.format_exc(),
                )
            )

    total = len(results)
    passed = sum(1 for r in results if r.pass_)
    failed = total - passed

    report: dict[str, Any] = {
        "schema_version": get_schema_version(),
        "run_id": run_id or f"{suite}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "suite": suite,
        "company": company,
        "ts": _utc_now_iso(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "duration_ms": int((time.time() - started) * 1000),
        "results": [asdict(r) for r in results],
    }
    return report


def write_report(report: dict[str, Any], out_dir: str | Path, filename: Optional[str] = None) -> str:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = filename or f"{report.get('run_id','RUN')}.json"
    p = out_dir / fname
    p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(p)


def console_summary(report: dict[str, Any]) -> str:
    # always show failures list when failed>0
    lines = [
        f"schema_version={report.get('schema_version')}",
        f"suite={report.get('suite')} company={report.get('company')}",
        f"total={report.get('total')} passed={report.get('passed')} failed={report.get('failed')}",
    ]
    if report.get("failed", 0):
        lines.append("FAILED CASES:")
        for r in report.get("results", []):
            if not r.get("pass_"):
                lines.append(f" - {r.get('name')}: {r.get('error')}")
    return "\n".join(lines)
