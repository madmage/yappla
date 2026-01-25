from typing import List, Union, Dict, Optional

from .utils import bc, eval_expression
from .state import State
from .action import Action


def _add_effects(effects1: List[Dict], effects2: Dict):
    if len(effects1) == 0:
        return [effects2]
    else:
        return [{**effects, **effects2} for effects in effects1]


class DurativeActionSpec:
    def __init__(
    self,
    name: str,
    conditions: Optional[Dict[str, str]] = None,
    effects: Optional[Dict[str, Union[List, Dict]]] = None,
    cost: int = 0,
    duration: float = 1.0,
    ):
        """Constructor

        Args:
            name (str): the name of the operator
            preconditions (str): an expression specifying the preconditions that
                have to hold to apply this operator
            effects (list): a list of dicts containing the (expected) effects of the
                application of this operator, for each variable name, the
                dict contains either a string with the expected value or
                a list of strings in case of multiple possible effects
            cost (int): this is the cost of applying this operator, e.g., for
                better modeling the differences between aborting or ending
                an action
        """
        self.name = name

        # Normalize input format:
        # - Conditions keys should be `to_*` (to_start, to_success, ...)
        # - Effects keys should be `on_*` (on_start, on_success, ...)
        # Backward-compat: accept legacy keys (start/success/abort/failure/aborted/end).
        conditions = conditions or {}
        effects = effects or {}

        kind_aliases = {"end": "success"}
        legacy_kinds = {"start", "abort", "success", "failure", "aborted", "end"}

        self._conditions: Dict[str, str] = {}
        for key, condition in (conditions or {}).items():
            if key in legacy_kinds:
                key = f"to_{kind_aliases.get(key, key)}"
            elif not key.startswith("to_"):
                # Allow advanced/custom keys, but keep YAML-style `to_*` if possible.
                key = f"to_{key}" if key in {"start", "abort", "success", "failure", "aborted"} else key
            self._conditions[key] = condition

        self._effects: Dict[str, Optional[List[Dict]]] = {}
        for key, eff in (effects or {}).items():
            if key in legacy_kinds:
                key = f"on_{kind_aliases.get(key, key)}"
            elif not key.startswith("on_"):
                key = f"on_{key}" if key in {"start", "abort", "success", "failure", "aborted"} else key

            if not eff:
                self._effects[key] = None
            elif isinstance(eff, list):
                self._effects[key] = eff
            elif isinstance(eff, dict):
                self._effects[key] = [eff]
        self.cost = cost
        self.duration = duration

    def __repr__(self) -> str:
        return (
            "DURATIVE ACTION SPEC "
            + self.name
            + " {\n"
            + "  preconditions:\n"
            + "    " + str(self._conditions) + "\n"
            + "  effects:\n"
            + "    " + str(self._effects) + "\n"
            + "  cost: " + str(self.cost) + "\n"
            + "  duration: " + str(self.duration) + "\n"
            + "}"
        )


    def split(self) -> List[Action]:
        actions = []
        for act_type in ["start", "abort", "success", "failure", "aborted"]:
            split_category = "decision" if act_type in ("start", "abort") else "event"
            action = Action(act_type + "__" + self.name,
                preconditions=self._conditions.get(f"to_{act_type}"),
                effects=self._effects.get(f"on_{act_type}"),
                cost=self.cost,
                duration=self.duration,
                parent_action_name=self.name,
                split_kind=act_type,
                split_category=split_category,
            )
            if act_type == "start":
                action._preconditions = "(" + action.preconditions + ") and " + self.name + "__state == 'idle'"
                action._effects = _add_effects(action.effects, {self.name + "__state": "running"})
            elif act_type == "abort":
                action._preconditions = "(" + action.preconditions + ") and " + self.name + "__state == 'running'"
                action._effects = _add_effects(action.effects, {self.name + "__state": "aborting"})
            elif act_type == "success":
                action._preconditions = "(" + action.preconditions + ") and " + self.name + "__state == 'running'"
                action._effects = _add_effects(action.effects, {self.name + "__state": "idle"})
            elif act_type == "failure":
                action._preconditions = "(" + action.preconditions + ") and " + self.name + "__state == 'running'"
                action._effects = _add_effects(action.effects, {self.name + "__state": "idle"})
            elif act_type == "aborted":
                action._preconditions = "(" + action.preconditions + ") and " + self.name + "__state == 'aborting'"
                action._effects = _add_effects(action.effects, {self.name + "__state": "idle"})
            action._preconditions = action._preconditions.replace("(True) and ", "")
            actions.append(action)
        return actions
