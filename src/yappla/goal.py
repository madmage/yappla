import re
from typing import List, Dict

from .utils import bc


class Goal(list):
    """A goal is a list of dictionaries.

    Each entry can contain:

    - ``priority`` (optional, default: 10): higher priority goals are checked
      first; lower priority goals are considered only if the current state
      satisfies the higher priority goals.
    - ``conditions`` (optional): a string (or compiled expression) that must be
      true for this goal entry to be active.
    - ``goal``: the goal expression over state variables.
    """

    def pretty_str(self, columns=True) -> str:
        if not columns:
            return str(self)
        else:
            lines = []
            self.sort(key=lambda x: -x["priority"] if "priority" in x else -10)
            for g in self:
                prio = g["priority"] if "priority" in g else 10
                cond = "[" + g["conditions"] + "]" if "conditions" in g else ""
                goal = re.sub(r" +", " ", g["goal"].replace("\n", " "))
                g = f"{bc.BOLD}{prio}{bc.ENDC} {bc.ORANGE}{cond}{bc.ENDC} {goal}"
                lines.append(str(g))
            return "\n".join(lines)
