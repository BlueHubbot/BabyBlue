from __future__ import annotations

from typing import List, Dict, Any, Optional

try:
    from erpnext.accounts.doctype.journal_entry.journal_entry import JournalEntry as ERPJournalEntry
except Exception:  # pragma: no cover
    ERPJournalEntry = object  # type: ignore


_DIM_FIELDS = ("bh_branch", "bh_tafsili_1", "bh_tafsili_2")


def _f(x) -> float:
    try:
        return float(x or 0)
    except Exception:
        return 0.0


def _s(x) -> str:
    return (x or "").strip()


class BlueJournalEntry(ERPJournalEntry):  # type: ignore[misc]
    """
    DIM-04 JE Line-aware:
    - Inject voucher_detail_no (JE Account row.name) into GL dicts
    - Inject bh_* dims from the SAME row into GL dicts (no overwrite if already set)
    """

    def get_gl_entries(self, *args, **kwargs) -> List[Dict[str, Any]]:
        gl_entries = super().get_gl_entries(*args, **kwargs)  # type: ignore[misc]
        try:
            rows = list(getattr(self, "accounts", None) or [])
            if not rows or not gl_entries:
                return gl_entries

            # Work on dict-only entries
            dict_entries: List[Dict[str, Any]] = [ge for ge in gl_entries if isinstance(ge, dict)]
            if not dict_entries:
                return gl_entries

            used = set()

            for r in rows:
                # skip 0 lines
                r_acc = _s(getattr(r, "account", None))
                r_dr = _f(getattr(r, "debit", None))
                r_cr = _f(getattr(r, "credit", None))
                if not r_acc or (abs(r_dr) < 1e-9 and abs(r_cr) < 1e-9):
                    continue

                # find matching GL dict by account + amount (tolerant)
                hit_i: Optional[int] = None
                for i, ge in enumerate(dict_entries):
                    if i in used:
                        continue
                    if _s(ge.get("account")) != r_acc:
                        continue
                    ge_dr = _f(ge.get("debit"))
                    ge_cr = _f(ge.get("credit"))
                    if abs(ge_dr - r_dr) < 0.0001 and abs(ge_cr - r_cr) < 0.0001:
                        hit_i = i
                        break

                if hit_i is None:
                    continue

                used.add(hit_i)
                ge = dict_entries[hit_i]

                # 1) voucher_detail_no for line-aware stamp
                if not _s(ge.get("voucher_detail_no")):
                    ge["voucher_detail_no"] = getattr(r, "name", None)

                # 2) copy dims from row -> GL dict (no overwrite)
                for f in _DIM_FIELDS:
                    rv = _s(getattr(r, f, None))
                    if rv and not _s(ge.get(f)):
                        ge[f] = rv

        except Exception:
            # never break posting
            return gl_entries

        return gl_entries
