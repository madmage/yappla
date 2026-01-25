"""Shared pytest configuration and fixtures."""
import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def pytest_addoption(parser):
    parser.addoption(
        "--perf",
        action="store_true",
        default=False,
        help="Enable printing grep-friendly PERF timing lines from selected tests.",
    )
    parser.addoption(
        "--show-plans",
        action="store_true",
        default=False,
        help="Collect and print a consolidated planner/temporal planner plan report at end of session.",
    )


def pytest_configure(config):
    # Tests that emit PERF lines will check this env var.
    if config.getoption("--perf"):
        os.environ["YAPPLA_PYTEST_PERF"] = "1"
    if config.getoption("--show-plans"):
        os.environ["YAPPLA_PYTEST_SHOW_PLANS"] = "1"


def pytest_sessionstart(session):
    # Reset PERF collection for each pytest invocation.
    try:
        from tests.yappla.perf import clear_perf_lines
        clear_perf_lines()
    except Exception:
        # Don't make tests fail if PERF helper cannot be imported.
        pass

    # Reset PLAN collection for each pytest invocation.
    try:
        from tests.yappla.plan_report import clear_plan_records
        clear_plan_records()
    except Exception:
        pass


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    if not config.getoption("--perf"):
        return

    try:
        from tests.yappla.perf import get_perf_lines
        lines = get_perf_lines()
    except Exception:
        return

    if not lines:
        return

    terminalreporter = config.pluginmanager.getplugin("terminalreporter")
    header = f"PERF report ({len(lines)} records)"
    if terminalreporter:
        # Ensure we don't interleave with pytest progress output.
        terminalreporter.write_line("")
        terminalreporter.write_sep("=", header)
        for line in lines:
            terminalreporter.write_line(line)
    else:
        # Fallback: should still appear with -s.
        print("=" * 80)
        print(header)
        for line in lines:
            print(line)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not config.getoption("--show-plans"):
        return

    try:
        from tests.yappla.plan_report import get_plan_records
        records = get_plan_records()
    except Exception:
        return

    if not records:
        return

    import textwrap

    def _state_to_lines(state_dict) -> list:
        if not isinstance(state_dict, dict) or not state_dict:
            state_str = str(state_dict)
        else:
            parts = [f"{k}={state_dict[k]!r}" for k in sorted(state_dict.keys())]
            state_str = ", ".join(parts)
        # Wrap on spaces (we already have ", ") to avoid hard terminal wrapping.
        return textwrap.wrap(
            state_str,
            width=120,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]

    def _write_goal(goal: str) -> None:
        goal_str = str(goal)
        parts = textwrap.wrap(goal_str, width=100) or [""]
        for part in parts:
            terminalreporter.write_line(f"GOAL {part}")

    def _write_plan_trace(trace):
        # Fallback format (used only if pretty plan is unavailable):
        # - state as a comma-separated list of k=v pairs
        # - action name on a separate line
        if not trace:
            terminalreporter.write_line("<no plan>")
            return

        for (state_dict, action) in trace:
            for line in _state_to_lines(state_dict):
                terminalreporter.write_line(line)
            if action:
                terminalreporter.write_line(str(action))

    def _write_pretty_plan(pretty) -> bool:
        if not pretty:
            return False
        for line in pretty.splitlines():
            terminalreporter.write_line(line)
        return True

    # Ensure we don't interleave with pytest progress output.
    terminalreporter.write_line("")
    terminalreporter.write_sep("=", f"PLAN report ({len(records)} records)")
    for rec in records:
        # Keep the same stable identifier used by PERF lines, but label it as a problem.
        terminalreporter.write_line(
            f"\nPROBLEM {rec.test_id} planner={rec.planner_type} outcome={rec.outcome}"
        )
        if rec.iterations is not None or rec.makespan is not None:
            terminalreporter.write_line(f"STATS iterations={rec.iterations} makespan={rec.makespan}")
        _write_goal(rec.goal)
        if not _write_pretty_plan(getattr(rec, "pretty_plan", None)):
            _write_plan_trace(getattr(rec, "trace", None) or [])


@pytest.fixture
def sample_state():
    """Fixture providing a sample state for testing."""
    from yappla import State, StateVariable
    
    state_vars = {
        "position": StateVariable("position", ["kitchen", "bedroom", "living_room"]),
        "raining": StateVariable("raining", [True, False]),
    }
    return State(state_vars, {"position": "kitchen", "raining": False})


@pytest.fixture
def sample_domain(sample_state):
    """Fixture providing a sample domain for testing."""
    from yappla import PlanningDomain
    
    domain = PlanningDomain(sample_state)
    return domain
