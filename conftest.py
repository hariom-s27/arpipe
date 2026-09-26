"""T0.4 Amendment 01: strict expected-failure registration for three original T0.4 guards.

This is the external registration required by docs/identity/T0_4_AMENDMENT_01.md section 4.
It does not edit, wrap or replace the guards. They execute unchanged. It only decides how
their outcome is reported.

The authorized A1-A4 reconstruction changes exactly arpipe/models.py, arpipe/triage.py,
arpipe/ocr.py and arpipe/store.py. The original literal T0.4 path guards report that as a
freeze violation. Under this registration:

    guard fails with the literal violation on exactly those four paths -> XFAIL
    guard passes                                                        -> XPASS(strict), a failure
    any other failure (fifth path, different error, setup error)        -> a failure

Node IDs are relative to the repository root, so run pytest from the repository root.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent

AMENDMENT_RECORD = "docs/identity/T0_4_AMENDMENT_01.md"

# The only production paths the amendment authorizes to differ from the T0.4 base (A1-A4).
AUTHORIZED_A1_A4_PATHS = frozenset({
    "arpipe/models.py",
    "arpipe/triage.py",
    "arpipe/ocr.py",
    "arpipe/store.py",
})

XFAIL_REASON = (
    "T0.4 Amendment 01 (" + AMENDMENT_RECORD + "): the authorized A1-A4 reconstruction "
    "changes arpipe/models.py, arpipe/triage.py, arpipe/ocr.py and arpipe/store.py, which "
    "this original literal T0.4 path guard reports as the known freeze deviation"
)

# node ID -> which literal violation the guard reports.
#   protected_paths:    tools.t0_4.core.verify_protected_paths_unchanged, which raises
#                       SetupInvariantError("frozen historical paths changed: [...]")
#   frozen_since_audit: tests/t0_4/test_t0_4_closure_record.py, which asserts that
#                       "git diff --name-only <audited commit> -- FROZEN_SINCE_AUDIT" is empty
STRICT_EXPECTED_FAILURES = {
    "tests/t0_4/test_t0_4_setup.py::test_frozen_corpus_and_history_are_unchanged": "protected_paths",
    "tests/t0_4/test_t0_4_setup.py::test_fail_closed_setup_audit_passes": "protected_paths",
    "tests/t0_4/test_t0_4_closure_record.py::test_frozen_inputs_are_unchanged_since_the_audited_commit": "frozen_since_audit",
}

_PROTECTED_PATHS_MESSAGE_PREFIX = "frozen historical paths changed: "
_FROZEN_SINCE_AUDIT_STATEMENT = "changed.stdout.split() == []"


def judge_guard(kind, exc_type_name, exc_message, failing_statement, violation_paths):
    """Return "xfail", "xpass" or "fail" for one registered guard outcome.

    exc_type_name is None when the guard passed. violation_paths is the literal violation
    recomputed independently with the guard's own git command, or None if unavailable.
    """
    if exc_type_name is None:
        return "xpass"
    if violation_paths is None:
        return "fail"
    if len(violation_paths) != len(AUTHORIZED_A1_A4_PATHS) or set(violation_paths) != AUTHORIZED_A1_A4_PATHS:
        return "fail"
    if kind == "protected_paths":
        if exc_type_name != "SetupInvariantError" or not exc_message.startswith(_PROTECTED_PATHS_MESSAGE_PREFIX):
            return "fail"
        try:
            listed = ast.literal_eval(exc_message[len(_PROTECTED_PATHS_MESSAGE_PREFIX):])
        except (ValueError, SyntaxError):
            return "fail"
        if not isinstance(listed, list) or len(listed) != len(AUTHORIZED_A1_A4_PATHS):
            return "fail"
        return "xfail" if set(listed) == AUTHORIZED_A1_A4_PATHS else "fail"
    if kind == "frozen_since_audit":
        if exc_type_name != "AssertionError" or _FROZEN_SINCE_AUDIT_STATEMENT not in failing_statement:
            return "fail"
        return "xfail"
    return "fail"


def _git_changed(base_commit, paths):
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "diff", "--name-only", base_commit, "--", *paths],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip().splitlines()


def _literal_violation(item, kind):
    """Recompute the violation the guard itself reports; None when it cannot be determined."""
    try:
        if kind == "protected_paths":
            core = sys.modules["tools.t0_4.core"]
            return _git_changed(core.BASE_COMMIT, core.PROTECTED_PATHS)
        if kind == "frozen_since_audit":
            record = item.funcargs["record"]
            return _git_changed(record["final_commit_after_audit"], item.module.FROZEN_SINCE_AUDIT)
    except Exception:
        return None
    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    kind = STRICT_EXPECTED_FAILURES.get(item.nodeid)
    if kind is None or call.when != "call":
        return
    report = outcome.get_result()
    if hasattr(report, "wasxfail"):
        return
    if call.excinfo is not None and call.excinfo.errisinstance(pytest.skip.Exception):
        return
    if call.excinfo is None:
        verdict = judge_guard(kind, None, "", "", None)
    else:
        try:
            statement = str(call.excinfo.traceback[-1].statement)
        except Exception:
            statement = ""
        verdict = judge_guard(
            kind, call.excinfo.type.__name__, str(call.excinfo.value), statement,
            _literal_violation(item, kind),
        )
    if verdict == "xfail":
        report.outcome = "skipped"
        report.wasxfail = XFAIL_REASON
    elif verdict == "xpass":
        report.outcome = "failed"
        report.longrepr = "[XPASS(strict)] " + XFAIL_REASON
