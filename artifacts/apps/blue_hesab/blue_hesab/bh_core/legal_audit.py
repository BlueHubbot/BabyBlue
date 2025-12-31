# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional


# ------------------------------------------------------------
# Bench-root discovery (critical: DO NOT depend on cwd)
# ------------------------------------------------------------

def _find_bench_root() -> Path:
    """
    Robust bench root resolver.
    We walk upwards from this file and pick the first directory that contains:
      - apps/
      - sites/
    """
    p = Path(__file__).resolve()
    for parent in [p] + list(p.parents)[:12]:
        if (parent / "apps").is_dir() and (parent / "sites").is_dir():
            return parent
    # fallback: old behavior (best-effort)
    return Path(os.getcwd()).resolve()


_BENCH_ROOT = _find_bench_root()

CHAIN_LOG_BASENAME = "legal_chain.log"
POLICY_LOG_BASENAME = "legal_policy.log"

DEFAULT_MAX_BYTES = 20 * 1024 * 1024  # 20MB
DEFAULT_KEEP = 10


# ------------------------------------------------------------
# JSON / time helpers
# ------------------------------------------------------------

def _now_ts() -> str:
    # match your existing log style
    return time.strftime("%Y-%m-%d %H:%M:%S") + f".{int((time.time() % 1) * 1_000_000):06d}"


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=str)


def _abs_path(path_or_basename: str) -> Path:
    """
    Always resolve relative paths under bench root.
    """
    p = Path(path_or_basename)
    if p.is_absolute():
        return p
    return (_BENCH_ROOT / p).resolve()


# ------------------------------------------------------------
# Rotation + append
# ------------------------------------------------------------

def _rotate_if_needed(p: Path, max_bytes: int = DEFAULT_MAX_BYTES, keep: int = DEFAULT_KEEP) -> None:
    try:
        if not p.exists():
            return
        if p.stat().st_size < max_bytes:
            return

        # rotate: file -> file.1 -> file.2 ...
        for i in range(keep, 0, -1):
            src = p.with_name(p.name + f".{i}")
            dst = p.with_name(p.name + f".{i+1}")
            if src.exists():
                if i == keep:
                    # drop the oldest
                    try:
                        src.unlink(missing_ok=True)
                    except Exception:
                        pass
                else:
                    try:
                        os.replace(str(src), str(dst))
                    except Exception:
                        pass

        # move current to .1
        try:
            os.replace(str(p), str(p.with_name(p.name + ".1")))
        except Exception:
            pass

    except Exception:
        # Never break business flow due to logging/rotation
        return


def _append_jsonl(p: Path, rec: Dict[str, Any]) -> None:
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        _rotate_if_needed(p)
        with p.open("a", encoding="utf-8") as f:
            f.write(_json_dumps(rec) + "\n")
    except Exception:
        # Never break business flow due to logging
        return


# ------------------------------------------------------------
# ctx capture (best-effort)
# ------------------------------------------------------------

def build_ctx() -> Dict[str, Any]:
    """
    Best-effort ctx collector:
      - user, sid
      - request_id
      - ip
      - user_agent
    Works in HTTP and CLI contexts.
    """
    ctx: Dict[str, Any] = {
        "user": None,
        "sid": None,
        "request_id": None,
        "ip": None,
        "user_agent": None,
    }

    try:
        import frappe  # type: ignore
    except Exception:
        return ctx

    try:
        # user + sid
        try:
            ctx["user"] = getattr(frappe, "session", None) and getattr(frappe.session, "user", None)
        except Exception:
            ctx["user"] = None

        try:
            ctx["sid"] = getattr(getattr(frappe, "local", None), "session", None) and getattr(frappe.local.session, "sid", None)
        except Exception:
            ctx["sid"] = None

        # request context (may be absent in bench execute)
        req = None
        try:
            req = getattr(getattr(frappe, "local", None), "request", None)
        except Exception:
            req = None

        # request_id (try a few common places)
        rid = None
        try:
            rid = getattr(getattr(frappe, "local", None), "request_id", None)
        except Exception:
            rid = None

        if not rid and req is not None:
            try:
                rid = req.headers.get("X-Request-ID") or req.headers.get("X-Request-Id") or req.headers.get("X-Req-Id")
            except Exception:
                rid = None
        ctx["request_id"] = rid

        # ip
        ip = None
        try:
            ip = getattr(getattr(frappe, "local", None), "request_ip", None)
        except Exception:
            ip = None
        if not ip and req is not None:
            try:
                ip = getattr(req, "remote_addr", None)
            except Exception:
                ip = None
        ctx["ip"] = ip

        # user_agent
        ua = None
        if req is not None:
            try:
                ua = req.headers.get("User-Agent")
            except Exception:
                ua = None
        ctx["user_agent"] = ua

    except Exception:
        pass

    return ctx


# ------------------------------------------------------------
# Public API (must keep backward-compat names)
# ------------------------------------------------------------

def append_jsonl(path_or_basename: str, rec: Dict[str, Any]):
    """
    Backward-compatible helper imported by older modules (e.g. legal_hooks.py).

    Some legacy code paths expect:
      out_name = append_jsonl("legal_chain.log", {"out_name": "...", ...})

    So we MUST return a useful identifier.
    """
    record = dict(rec or {})
    _append_jsonl(_abs_path(path_or_basename), record)

    return (
        record.get("out_name")
        or record.get("legal_output")
        or record.get("output_name")
        or record.get("docname")
        or record.get("name")
    )


def log_emit(
    *,
    event: str,
    company: Optional[str],
    ref_doctype: str,
    ref_name: str,
    out_name: Optional[str],
    details: Dict[str, Any],
    ctx: Optional[Dict[str, Any]] = None,
    action: str = "emit",
    log_basename: str = CHAIN_LOG_BASENAME,
) -> Optional[str]:
    """
    Standardized emit/reuse logger.
    action MUST be 'emit' or 'reuse' (or you can pass custom actions if needed).
    """
    rec: Dict[str, Any] = {
        "ts": _now_ts(),
        "site": None,
        "event": event,
        "action": action,
        "company": company,
        "ref_doctype": ref_doctype,
        "ref_name": ref_name,
        "out_name": out_name,
        "ctx": ctx or build_ctx(),
        "details": details or {},
    }

    try:
        import frappe  # type: ignore
        try:
            rec["site"] = getattr(getattr(frappe, "local", None), "site", None)
        except Exception:
            rec["site"] = None
    except Exception:
        rec["site"] = None

    _append_jsonl(_abs_path(log_basename), rec)
    return out_name


def log_reuse(**kwargs) -> Optional[str]:
    kwargs["action"] = "reuse"
    return log_emit(**kwargs)


def log_enabled(
    *,
    event: str,
    company: Optional[str],
    ref_doctype: str,
    ref_name: str,
    phase: str,
    enabled: Any,
    ctx: Optional[Dict[str, Any]] = None,
    log_basename: str = POLICY_LOG_BASENAME,
) -> None:
    rec: Dict[str, Any] = {
        "ts": _now_ts(),
        "site": None,
        "event": event,
        "action": "enabled",
        "company": company,
        "ref_doctype": ref_doctype,
        "ref_name": ref_name,
        "out_name": None,
        "ctx": ctx or build_ctx(),
        "details": {"phase": phase, "enabled": enabled},
    }

    try:
        import frappe  # type: ignore
        try:
            rec["site"] = getattr(getattr(frappe, "local", None), "site", None)
        except Exception:
            rec["site"] = None
    except Exception:
        rec["site"] = None

    _append_jsonl(_abs_path(log_basename), rec)


def log_block_write(
    *,
    doctype: str,
    name: str,
    reason: Optional[str] = None,
    ctx: Optional[Dict[str, Any]] = None,
    log_basename: str = CHAIN_LOG_BASENAME,
) -> None:
    """
    Keep the legacy shape you already have in logs:
      {"action":"BLOCK_WRITE","doctype":"BH Legal Output","name":"...","ts":"...","site":"...","user":"..."}
    """
    c = ctx or build_ctx()
    rec: Dict[str, Any] = {
        "action": "BLOCK_WRITE",
        "doctype": doctype,
        "name": name,
        "ts": _now_ts(),
        "site": None,
        "user": c.get("user"),
    }
    if reason:
        rec["reason"] = reason
    _append_jsonl(_abs_path(log_basename), rec)


def log_tamper(
    *,
    out_name: str,
    ref_doctype: Optional[str] = None,
    ref_name: Optional[str] = None,
    attempted: Optional[Dict[str, Any]] = None,
    ctx: Optional[Dict[str, Any]] = None,
    log_basename: str = CHAIN_LOG_BASENAME,
) -> str:
    """
    Required by some regress modules.
    """
    rec: Dict[str, Any] = {
        "ts": _now_ts(),
        "event": "LEGAL-TAMPER",
        "action": "tamper",
        "out_name": out_name,
        "ref_doctype": ref_doctype,
        "ref_name": ref_name,
        "ctx": ctx or build_ctx(),
        "details": {"attempted": attempted or {}},
    }
    _append_jsonl(_abs_path(log_basename), rec)
    return out_name
