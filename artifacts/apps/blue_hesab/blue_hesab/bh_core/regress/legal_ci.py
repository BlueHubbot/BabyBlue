from __future__ import annotations

import frappe

from blue_hesab.bh_core.regress.reporting import run_cases, write_report, console_summary

# LEGAL07 already has proper case-functions:
from blue_hesab.bh_core.legal07_regress import (
    regress_legal07_amend_without_cancel_should_fail,
    regress_legal07_cancel_then_amend_should_pass,
    regress_legal07_amend_twice_should_fail,
    regress_legal07_cancel_twice_should_fail,
    regress_legal07_cancel_without_issue_should_fail,
)

# You MUST add these in legal08_regress.py (below)
from blue_hesab.bh_core.legal08_regress import (
    regress_legal08_issue_emit_succeeds,
    regress_legal08_policy_lock_blocks_delete,
    regress_legal08_immutable_blocks_update,
)

# You MUST add these in legal09_regress.py (below)
from blue_hesab.bh_core.legal09_regress import (
    regress_legal09_si_issue_outputs_exist,
    regress_legal09_si_cancel_outputs_exist,
    regress_legal09_si_amend_outputs_exist,
    regress_legal09_pi_issue_cancel_outputs_exist,
)


def run_legal_suite(company: str) -> dict:
    cases = [
        # LEGAL07
        regress_legal07_amend_without_cancel_should_fail,
        regress_legal07_cancel_then_amend_should_pass,
        regress_legal07_amend_twice_should_fail,
        regress_legal07_cancel_twice_should_fail,
        regress_legal07_cancel_without_issue_should_fail,

        # LEGAL08
        regress_legal08_issue_emit_succeeds,
        regress_legal08_policy_lock_blocks_delete,
        regress_legal08_immutable_blocks_update,

        # LEGAL09
        regress_legal09_si_issue_outputs_exist,
        regress_legal09_si_cancel_outputs_exist,
        regress_legal09_si_amend_outputs_exist,
        regress_legal09_pi_issue_cancel_outputs_exist,
    ]

    report = run_cases(suite="LEGAL", company=company, cases=cases, run_id="BH-LEGAL-REGRESS")

    out_dir = frappe.get_site_path("private", "files", "bh_regress")
    path = write_report(report, out_dir=out_dir, filename="BH-LEGAL-last.json")

    print(console_summary(report))
    report["report_path"] = path
    return report
