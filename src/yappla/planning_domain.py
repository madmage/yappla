from typing import Dict

import copy

from .action import Action
from .durative_action_spec import DurativeActionSpec
from .state_variable import StateVariable
from .state import State


class PlanningDomain:
    """A planning domain contains the definition of the state variables and the actions.
    
    This class represents a planning domain that can be used by planners to find
    plans that achieve goals. It maintains a collection of actions and state
    variables that define what transformations are possible in this domain.
    """

    def __init__(self):
        self._actions = {}
        self._variables = {}

    def action(self, name) -> Action:
        """Get an action by name."""
        return self._actions.get(name, None)

    @property
    def actions(self) -> Dict[str, Action]:
        """Get all actions in the domain."""
        return self._actions

    def add_action(self, action: Action):
        """Add an action to the domain."""
        self._actions[action.name] = action

    def variable(self, name) -> StateVariable:
        """Get a state variable by name."""
        return self._variables.get(name, None)

    @property
    def variables(self) -> Dict[str, StateVariable]:
        """Get all state variables in the domain."""
        return self._variables

    def add_variable(self, variable: StateVariable):
        """Add a state variable to the domain."""
        self._variables[variable.name] = variable

    def get_initial_state(self) -> "State":
        """Get the initial state built from the initial values of all state variables."""
        return State(
            {
                name: definition.initial_value if definition.initial_value is not None else "UNK"
                for name, definition in self._variables.items()
            }
        )

    def __repr__(self) -> str:
        """String representation of the domain."""
        r = "PLANNING DOMAIN\n"
        for a in self._actions.values():
            r += str(a) + "\n"
        for v in self._variables.values():
            r += str(v) + "\n"
        return r

    def contains_action_specs(self) -> bool:
        """Check if the domain contains any action-spec objects."""
        for action in self._actions.values():
            if isinstance(action, DurativeActionSpec):
                return True
        return False

    def compile_action_specs(self) -> "PlanningDomain":
        """Return a new domain with action specs compiled into primitive actions.
        
        This method creates a new planning domain where all durative action specs are
        split into their constituent actions (start, success, abort, etc.) and
        state variables are added to track the execution state of each durative action.
        """
        other = copy.deepcopy(self)
        other._actions = {}
        for action in self._actions.values():
            if isinstance(action, Action):
                other.add_action(action)
            elif isinstance(action, DurativeActionSpec):
                other.add_variable(StateVariable(
                    action.name + "__state",
                    possible_values=["idle", "running", "aborting"],
                    initial_value="idle"
                ))
                acts = action.split()
                for act in acts:
                    other.add_action(act)
        return other

    def load_from_dict(self, definition):
        """Load a domain definition from a dictionary.

        The input can either be wrapped under a top-level ``domain`` key or
        contain ``actions``/``variables`` directly.

        Wrapped format:

        .. code-block:: python

            {
                "domain": {
                    "actions": {"action_name": {"...": "..."}, ...},
                    "variables": {"var_name": {"...": "..."}, ...},
                }
            }

        Direct format:

        .. code-block:: python

            {
                "actions": {"action_name": {"...": "..."}, ...},
                "variables": {"var_name": {"...": "..."}, ...},
            }
        """
        if "domain" in definition:
            definition = definition["domain"]
        for action_name, action_definition in definition["actions"].items():
            # Check if this is a durative action
            if action_definition.get("type") == "durative":
                # Convert YAML format to DurativeActionSpec format.
                # Accepted input shapes:
                # - legacy: conditions_to/effects_on (list or dict) with times start/end/success/...
                # - new: conditions/effects (list or dict) with keys to_*/on_*.
                action_dict = dict(action_definition)
                action_dict.pop("type", None)  # Remove type field

                def _normalize_condition_time_key(time_key: str) -> str:
                    # Most YADD(L) files use start/end; map end -> success.
                    if not time_key:
                        time_key = "start"
                    if time_key.startswith("to_"):
                        return time_key
                    if time_key == "end":
                        return "to_success"
                    if time_key in ("start", "abort", "success", "failure", "aborted"):
                        return f"to_{time_key}"
                    # Best effort.
                    return f"to_{time_key}"

                def _normalize_effect_time_key(time_key: str) -> str:
                    if not time_key:
                        time_key = "end"
                    if time_key.startswith("on_"):
                        return time_key
                    if time_key == "end":
                        return "on_success"
                    if time_key in ("start", "abort", "success", "failure", "aborted"):
                        return f"on_{time_key}"
                    return f"on_{time_key}"

                def _conditions_to_dict(obj) -> Dict[str, str]:
                    if obj is None:
                        return {}
                    if isinstance(obj, dict):
                        return {str(k): v for k, v in obj.items()}
                    if isinstance(obj, list):
                        out: Dict[str, str] = {}
                        for cond in obj:
                            time_key = _normalize_condition_time_key(str(cond.get("time", "start")))
                            out[time_key] = cond.get("condition", "")
                        return out
                    return {}

                def _effects_to_dict(obj) -> Dict[str, Dict]:
                    if obj is None:
                        return {}
                    if isinstance(obj, dict):
                        return {str(k): (v or {}) for k, v in obj.items()}
                    if isinstance(obj, list):
                        out: Dict[str, Dict] = {}
                        for eff in obj:
                            time_key = _normalize_effect_time_key(str(eff.get("time", "end")))
                            out[time_key] = eff.get("effects", {}) or {}
                        return out
                    return {}

                # Prefer new keys, but support legacy ones.
                raw_conditions = action_dict.pop("conditions", None)
                raw_effects = action_dict.pop("effects", None)
                if raw_conditions is None and "conditions_to" in action_dict:
                    raw_conditions = action_dict.pop("conditions_to", None)
                if raw_effects is None and "effects_on" in action_dict:
                    raw_effects = action_dict.pop("effects_on", None)

                conditions_dict = _conditions_to_dict(raw_conditions)
                effects_dict = _effects_to_dict(raw_effects)

                # Normalize dict keys into to_*/on_*.
                norm_conditions: Dict[str, str] = {}
                for k, v in conditions_dict.items():
                    norm_conditions[_normalize_condition_time_key(k)] = v
                norm_effects: Dict[str, Dict] = {}
                for k, v in effects_dict.items():
                    norm_effects[_normalize_effect_time_key(k)] = v

                yaction = DurativeActionSpec(
                    name=action_name,
                    conditions=norm_conditions,
                    effects=norm_effects,
                    **action_dict,
                )
            else:
                action_dict = dict(action_definition)
                yaction = Action(name=action_name, **action_dict)
            self.add_action(yaction)
        for variable_name, variable_definition in definition["variables"].items():
            # Remove 'type' field if present (system, internal, action)
            var_dict = dict(variable_definition)
            var_dict.pop("type", None)
            # Map 'values' to 'possible_values'
            if "values" in var_dict:
                var_dict["possible_values"] = var_dict.pop("values")
            yvariable = StateVariable(name=variable_name, **var_dict)
            self.add_variable(yvariable)
