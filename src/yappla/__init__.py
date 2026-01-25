from .action import Action
from .durative_action_spec import DurativeActionSpec
from .utils import CompiledExpression
from .goal import Goal
from .plan import Plan, PlannerResult, PlannerOutcome
from .state import State
from .state_variable import StateVariable
from .planning_domain import PlanningDomain
from .planner import Planner
from .temporal_planner import TemporalPlanner

import subprocess
import re
import os


VERSION = (0, 0, 0, "ERR", 1)
#__version__ = "ERR"
__version__ = "0.0.3"

try:
    git_version = subprocess.check_output(
        ["git", "describe", "--tags", "--dirty=-wip"], stderr=subprocess.DEVNULL
    )
    output = git_version.strip().decode("ascii")
    data = output.split("-")
    tag = data[0]
    match = re.match(r"^v?(\d+)\.(\d)+\.(\d)+$", tag)
    if match is not None:
        MAJOR, MINOR, REL = tuple(int(x) for x in match.groups())
    else:
        MAJOR, MINOR, REL = (0, 0, 0)
    try:
        COMMITS = int(data[1])
    except ValueError:
        COMMITS = 0

    if data[-1] == "wip":
        if COMMITS == 0:
            VERSION = (MAJOR, MINOR, REL, "post", 1)
            __version__ = f"{MAJOR}.{MINOR}.{REL}.post1"
        else:
            VERSION = (MAJOR, MINOR, REL, COMMITS, "post", 1)
            __version__ = f"{MAJOR}.{MINOR}.{REL}.{COMMITS}.post1"
    else:
        VERSION = (MAJOR, MINOR, REL, COMMITS, "dev", 1)
        __version__ = f"{MAJOR}.{MINOR}.{REL}.{COMMITS}.dev1"

except Exception:
    pass

