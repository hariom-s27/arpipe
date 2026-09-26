"""Read-only pytest reporting for P-A; does not select or change test outcomes."""
import json
import os
import sys
from pathlib import Path

import pytest

reports = []
collection_errors = []


def pytest_runtest_logreport(report):
    entry = {"nodeid": report.nodeid, "phase": report.when,
             "outcome": report.outcome, "duration_seconds": report.duration,
             "wasxfail": getattr(report, "wasxfail", None)}
    if report.skipped or report.failed:
        entry["detail"] = str(report.longrepr)
    reports.append(entry)


def pytest_collectreport(report):
    if report.failed:
        collection_errors.append({"nodeid": report.nodeid, "detail": str(report.longrepr)})


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    counts = {key: len(terminal.stats.get(key, [])) for key in
              ("passed", "skipped", "xfailed", "xpassed", "failed", "error")}
    counts["errors"] = counts.pop("error")
    result = {"collected": session.testscollected, "exitstatus": int(exitstatus),
              "counts": counts, "collection_errors": collection_errors,
              "reports": reports,
              "arpipe_modules": {name: str(module.__file__) for name, module in
                  sorted(sys.modules.items()) if (name == "arpipe" or name.startswith("arpipe."))
                  and getattr(module, "__file__", None)},
              "sys_path": list(sys.path)}
    Path(os.environ["PA_OBSERVER_OUTPUT"]).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
