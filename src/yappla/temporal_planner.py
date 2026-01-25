import time
import copy
import logging
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field

from yappla.state import State
from yappla.utils import CompiledExpression, bc, PriorityQueue
from yappla.plan import Plan, PlannerOutcome, PlannerResult
from yappla.planner import Planner
from yappla.action import Action
from yappla.durative_action_spec import DurativeActionSpec


@dataclass
class TemporalEvent:
    """Represents a temporal event in the plan."""
    time: float
    action_name: str
    action_type: str  # 'start', 'success', 'failure', 'abort', 'aborted'
    state_change: Dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Event({self.time:.1f}: {self.action_name}.{self.action_type})"


@dataclass
class ScheduledAction:
    """Represents an action that has been scheduled."""
    action: Action
    start_time: float
    end_time: float
    action_type: str  # 'primitive' or 'compiled'
    base_name: str = ""
    aborted_requested: bool = False

    def overlaps_with(self, other: "ScheduledAction") -> bool:
        """Check if this action's execution overlaps with another."""
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)

    def __repr__(self) -> str:
        label = self.base_name or self.action.name
        return f"Scheduled({label}[{self.start_time:.1f}-{self.end_time:.1f}])"


class TemporalState:
    """State representation that includes temporal information."""

    def __init__(self, state_vars: Dict = None, current_time: float = 0.0, 
                 scheduled_actions: List[ScheduledAction] = None,
                 all_scheduled_actions: List[ScheduledAction] = None,
                 initial_state_vars: Dict = None,
                 events: List[TemporalEvent] = None):
        self.state_vars = State(state_vars or {})
        # Snapshot of the initial merged state at time 0.0. This enables plan
        # reconstruction with meaningful intermediate state snapshots.
        self.initial_state_vars = State(initial_state_vars if initial_state_vars is not None else self.state_vars)
        self.current_time = current_time
        # Actions that are currently executing (i.e., "active" actions).
        self.scheduled_actions = scheduled_actions or []
        # Full schedule history (used to reconstruct the final plan).
        self.all_scheduled_actions = all_scheduled_actions or []
        self.events = events or []

    def copy(self) -> "TemporalState":
        """Create a deep copy of this temporal state."""
        return TemporalState(
            state_vars=dict(self.state_vars),
            initial_state_vars=dict(self.initial_state_vars),
            current_time=self.current_time,
            scheduled_actions=copy.deepcopy(self.scheduled_actions),
            all_scheduled_actions=copy.deepcopy(self.all_scheduled_actions),
            events=copy.deepcopy(self.events)
        )

    def get_active_actions_at(self, time: float) -> List[ScheduledAction]:
        """Get actions that are executing at the given time."""
        return [a for a in self.scheduled_actions if a.start_time <= time < a.end_time]

    def get_next_decision_point(self) -> float:
        """Get the next time when a decision can be made.
        
        This is the earliest of:
        - When the first action completes
        - Current time (if no actions are active)
        """
        if not self.scheduled_actions:
            return self.current_time
        
        # Find the earliest end time of active or future actions
        end_times = [a.end_time for a in self.scheduled_actions]
        return min(end_times) if end_times else self.current_time

    def apply_action_effects(self, scheduled_action: ScheduledAction) -> None:
        """Apply the effects of a completed action to the state."""
        # Effects are applied when the action completes. This method applies
        # a single (deterministic) outcome.
        effects = scheduled_action.action._effects or []
        if not effects:
            return
        # If multiple outcomes exist, this method applies only the first.
        effect = effects[0]
        if isinstance(effect, dict):
            for key, value in effect.items():
                self.state_vars[key] = value

    def has_mutex_conflict(self, new_action: Action, duration: float) -> bool:
        """Check if scheduling new_action would conflict with already scheduled actions.
        
        Returns True if:
        - New action would overlap with an existing action and both modify the same variable
        - OR new action cannot start due to an existing action's effects on state
        """
        start_time = self.current_time
        end_time = start_time + duration

        for scheduled in self.scheduled_actions:
            # Check if actions overlap
            if start_time < scheduled.end_time and end_time > scheduled.start_time:
                # Actions overlap - check if they conflict
                # They conflict if they modify the same state variables
                new_effects = set(new_action._effects[0].keys()) if new_action._effects else set()
                scheduled_effects_list = scheduled.action._effects or []
                scheduled_effects = set()
                for effect in scheduled_effects_list:
                    if isinstance(effect, dict):
                        scheduled_effects.update(effect.keys())

                # Mutex if they both affect same variable
                if new_effects & scheduled_effects:
                    return True

        return False

    def __repr__(self) -> str:
        return (f"TemporalState(t={self.current_time:.1f}, vars={dict(self.state_vars)}, "
                f"active={len(self.get_active_actions_at(self.current_time))} actions)")

    def __hash__(self) -> int:
        """Hash based on state variables and time."""
        # Round time to avoid floating point issues
        time_bucket = int(self.current_time * 10)  # 0.1 time unit resolution
        # Include active actions in the hash, otherwise we may incorrectly
        # merge states that differ only by running actions (which affects future).
        active_sig = tuple(sorted(
            (a.action.name, int(a.start_time * 10), int(a.end_time * 10))
            for a in self.scheduled_actions
        ))
        return hash((frozenset(self.state_vars.items()), time_bucket, active_sig))

    def __eq__(self, other) -> bool:
        """Check equality with small time tolerance."""
        if not isinstance(other, TemporalState):
            return False
        time_tolerance = 0.01
        if dict(self.state_vars) != dict(other.state_vars):
            return False
        if abs(self.current_time - other.current_time) >= time_tolerance:
            return False
        self_active = sorted((a.action.name, a.start_time, a.end_time) for a in self.scheduled_actions)
        other_active = sorted((a.action.name, a.start_time, a.end_time) for a in other.scheduled_actions)
        if len(self_active) != len(other_active):
            return False
        for (n1, s1, e1), (n2, s2, e2) in zip(self_active, other_active):
            if n1 != n2:
                return False
            if abs(s1 - s2) >= time_tolerance or abs(e1 - e2) >= time_tolerance:
                return False
        return True


class TemporalPlanner(Planner):
    """A temporal planner that considers action durations and mutex constraints.
    
    This planner extends the basic Planner to support:
    - Action durations
    - Time-aware planning (makespan optimization)
    - Mutex constraints between overlapping actions
    - Explicit scheduling of actions with time tracking
    """

    def __init__(self, logger=None):
        super().__init__(logger)
        self.temporal_result = None

    def _assert_domain_has_no_action_specs(self) -> None:
        """Ensure the planner domain contains only primitive Action operators.

        In Yappla, high-level `DurativeActionSpec` instances are expected to be compiled
        into primitive `Action` operators (e.g., start/abort/success/...) by calling
        `Planner.set_domain()`, which uses the domain's durative-to-non-durative
        transformation.
        """
        if self._domain is None:
            raise ValueError("TemporalPlanner has no domain set. Call set_domain(domain) first.")

        durative_names = [
            a.name for a in self._domain.actions.values()
            if isinstance(a, DurativeActionSpec)
        ]
        if durative_names:
            durative_preview = ", ".join(sorted(durative_names)[:5])
            more = "" if len(durative_names) <= 5 else f" (+{len(durative_names) - 5} more)"
            raise ValueError(
                "TemporalPlanner received a domain that still contains DurativeActionSpec objects "
                f"({durative_preview}{more}). DurativeActionSpec must be split into primitive Action "
                "operators before planning. Ensure you call planner.set_domain(domain) and that "
                "the domain implements contains_action_specs()/compile_action_specs()."
            )

    def plan(self, initial_state: "State", goal=None):
        """Find a temporal plan considering action durations and constraints.
        
        Returns a PlannerResult with a time-annotated plan.
        """
        if goal:
            self.set_goal(goal)

        # Fail fast if the domain still includes high-level DurativeActionSpec objects.
        self._assert_domain_has_no_action_specs()

        # Index compiled operator families by (parent_action_name, split_kind).
        # TemporalPlanner relies on Action metadata and does not parse action names.
        compiled_ops: Dict[str, Dict[str, Action]] = {}
        for op in self._domain.actions.values():
            parent = getattr(op, "parent_action_name", None)
            kind = getattr(op, "split_kind", None)
            category = getattr(op, "split_category", None)
            if parent and kind and category:
                compiled_ops.setdefault(parent, {})[kind] = op

        initial_time = time.thread_time()
        
        # Prepare initial state
        domain_initial = self._domain.get_initial_state()
        merged_state = State({**domain_initial, **initial_state})
        
        goal_expr = CompiledExpression(self._compute_cur_goal(merged_state))
        
        self.log(1, "")
        self.log(1, f"[Temporal Planning] Starting from state: {dict(merged_state)}")
        self.log(1, f"To goal: {self._cur_goal}")
        
        # Initialize temporal search
        initial_temporal_state = TemporalState(
            state_vars=merged_state,
            initial_state_vars=merged_state,
            current_time=0.0,
            scheduled_actions=[],
            all_scheduled_actions=[],
        )
        
        open_pq = PriorityQueue()
        open_pq.push(initial_temporal_state, 0)  # priority = makespan lower bound
        
        visited = set()
        planner_result = PlannerResult(self)
        planning_iterations = 0
        
        while planning_iterations < self.max_iterations:
            if open_pq.empty():
                break
                
            temporal_state, current_cost = open_pq.pop()
            planning_iterations += 1
            
            if self.max_verbosity_level >= 2:
                self.log(2, f"[{planning_iterations}] Exploring {temporal_state}")
            elif self.max_verbosity_level == 1:
                print(".", end="")
            
            # Check if goal is satisfied (we require all running actions to be finished)
            if goal_expr.eval_in_state(temporal_state.state_vars) and not temporal_state.scheduled_actions:
                self.log(1, f"\n[{planning_iterations}] FOUND PLAN! Makespan: {temporal_state.current_time:.1f} time units")
                
                # Build result with temporal information
                planner_result.plan = self._build_temporal_plan(temporal_state)
                planner_result.outcome = PlannerOutcome.SUCCESS
                planner_result.stats["time"] = time.thread_time() - initial_time
                planner_result.stats["iterations"] = planning_iterations
                planner_result.stats["makespan"] = temporal_state.current_time
                break
            
            state_key = hash(temporal_state)
            if state_key in visited:
                continue
            visited.add(state_key)

            def active_compiled_instance(state: TemporalState, base: str) -> ScheduledAction:
                for a in state.scheduled_actions:
                    if a.action_type == "compiled" and a.base_name == base:
                        if a.start_time <= state.current_time < a.end_time:
                            return a
                return None

            # 1) Start any applicable actions at the current time (do NOT advance time).
            for action in self._domain.actions.values():
                if isinstance(action, DurativeActionSpec):
                    raise ValueError(
                        f"Unexpected DurativeActionSpec '{action.name}' found during search. "
                        "DurativeActionSpec must be split into primitive Action operators before planning."
                    )

                compiled_kind = getattr(action, "split_kind", None)
                compiled_category = getattr(action, "split_category", None)
                compiled_base = getattr(action, "parent_action_name", None)

                # Completion operators are applied automatically at the end of the running interval.
                if compiled_category == "event":
                    continue

                # Abort operator: instantaneous request while the action is running.
                if compiled_kind == "abort":
                    if not compiled_base:
                        raise ValueError(
                            f"Compiled abort action '{action.name}' is missing parent_action_name metadata."
                        )
                    active = active_compiled_instance(temporal_state, compiled_base)
                    if active is None:
                        continue
                    if not action.applicable(temporal_state.state_vars):
                        continue

                    for outcome_state in action.possible_outcomes(temporal_state.state_vars):
                        new_temporal_state = temporal_state.copy()
                        new_temporal_state.state_vars = outcome_state

                        # Mark abort request and reschedule end time on the matching active instance.
                        # Semantics: abort__X.duration models the remaining time from the abort
                        # request until the activity is fully aborted.
                        abort_duration = float(action.duration)
                        abort_end_time = new_temporal_state.current_time + abort_duration

                        def matches_active(scheduled: ScheduledAction) -> bool:
                            return (
                                scheduled.action_type == "compiled"
                                and scheduled.base_name == compiled_base
                                and abs(scheduled.start_time - active.start_time) < 0.01
                            )

                        for a in new_temporal_state.scheduled_actions:
                            if matches_active(a):
                                a.aborted_requested = True
                                if abort_end_time < a.end_time - 0.01:
                                    a.end_time = abort_end_time

                        for a in new_temporal_state.all_scheduled_actions:
                            if matches_active(a):
                                a.aborted_requested = True
                                if abort_end_time < a.end_time - 0.01:
                                    a.end_time = abort_end_time
                        cost = max(
                            new_temporal_state.current_time,
                            max((a.end_time for a in new_temporal_state.all_scheduled_actions), default=new_temporal_state.current_time),
                        )
                        open_pq.push(new_temporal_state, cost)
                    continue

                # Start operator: start effects happen now; completion effects happen at end.
                if compiled_kind == "start":
                    if not compiled_base:
                        raise ValueError(
                            f"Compiled start action '{action.name}' is missing parent_action_name metadata."
                        )
                    # Avoid starting multiple instances of the same compiled base.
                    if any(a.action_type == "compiled" and a.base_name == compiled_base for a in temporal_state.scheduled_actions):
                        continue
                    if not action.applicable(temporal_state.state_vars):
                        continue

                    start_duration = float(action.duration)
                    for start_outcome_state in action.possible_outcomes(temporal_state.state_vars):
                        new_temporal_state = temporal_state.copy()
                        new_temporal_state.state_vars = start_outcome_state
                        scheduled = ScheduledAction(
                            action=action,
                            start_time=temporal_state.current_time,
                            end_time=temporal_state.current_time + start_duration,
                            action_type='compiled',
                            base_name=compiled_base,
                            aborted_requested=False,
                        )
                        new_temporal_state.scheduled_actions.append(scheduled)
                        new_temporal_state.all_scheduled_actions.append(scheduled)
                        cost = max(
                            new_temporal_state.current_time,
                            max((a.end_time for a in new_temporal_state.all_scheduled_actions), default=new_temporal_state.current_time),
                        )
                        open_pq.push(new_temporal_state, cost)
                    continue

                # Primitive operator
                # Avoid starting multiple identical instances unless model explicitly allows it.
                if any(a.action_type == "primitive" and a.action.name == action.name for a in temporal_state.scheduled_actions):
                    continue
                if not action.applicable(temporal_state.state_vars):
                    continue
                if action.duration <= 0:
                    # Instantaneous action: apply immediately (no overlap semantics required).
                    for outcome_state in action.possible_outcomes(temporal_state.state_vars):
                        new_temporal_state = temporal_state.copy()
                        new_temporal_state.state_vars = outcome_state
                        # current_time unchanged
                        cost = max(
                            new_temporal_state.current_time,
                            max((a.end_time for a in new_temporal_state.all_scheduled_actions), default=new_temporal_state.current_time),
                        )
                        open_pq.push(new_temporal_state, cost)
                    continue

                if temporal_state.has_mutex_conflict(action, action.duration):
                    continue

                new_temporal_state = temporal_state.copy()
                scheduled = ScheduledAction(
                    action=action,
                    start_time=temporal_state.current_time,
                    end_time=temporal_state.current_time + float(action.duration),
                    action_type='primitive',
                    base_name='',
                    aborted_requested=False,
                )
                new_temporal_state.scheduled_actions.append(scheduled)
                new_temporal_state.all_scheduled_actions.append(scheduled)

                cost = max(
                    new_temporal_state.current_time,
                    max((a.end_time for a in new_temporal_state.all_scheduled_actions), default=new_temporal_state.current_time),
                )
                open_pq.push(new_temporal_state, cost)

            # 2) Advance time to the next completion point and apply completed effects.
            if temporal_state.scheduled_actions:
                next_time = min(a.end_time for a in temporal_state.scheduled_actions)
                advanced_base = temporal_state.copy()
                advanced_base.current_time = next_time

                completed = [
                    a for a in advanced_base.scheduled_actions
                    if abs(a.end_time - next_time) < 0.01
                ]
                advanced_base.scheduled_actions = [
                    a for a in advanced_base.scheduled_actions
                    if a.end_time > next_time + 0.01
                ]

                # Apply effects of all completed actions at this time.
                outcome_states = [advanced_base.state_vars]
                for completed_action in completed:
                    next_outcomes = []
                    for s in outcome_states:
                        if completed_action.action_type == "compiled":
                            base = completed_action.base_name
                            if completed_action.aborted_requested:
                                completion_kinds = ["aborted"]
                            else:
                                completion_kinds = ["success", "failure"]

                            by_kind = compiled_ops.get(base, {})
                            completion_actions = [by_kind.get(k) for k in completion_kinds]
                            completion_actions = [a for a in completion_actions if a is not None]

                            # If no explicit completion operator exists, preserve state.
                            if not completion_actions:
                                next_outcomes.append(s)
                            else:
                                for comp in completion_actions:
                                    outs = comp.possible_outcomes(s)
                                    if not outs:
                                        next_outcomes.append(s)
                                    else:
                                        next_outcomes.extend(outs)
                        else:
                            outs = completed_action.action.possible_outcomes(s)
                            if not outs:
                                next_outcomes.append(s)
                            else:
                                next_outcomes.extend(outs)
                    outcome_states = next_outcomes

                for outcome_state in outcome_states:
                    advanced_state = advanced_base.copy()
                    advanced_state.state_vars = outcome_state
                    cost = max(
                        advanced_state.current_time,
                        max((a.end_time for a in advanced_state.all_scheduled_actions), default=advanced_state.current_time),
                    )
                    open_pq.push(advanced_state, cost)
        
        if planner_result.outcome != PlannerOutcome.SUCCESS:
            planner_result.outcome = PlannerOutcome.FAILURE
            planner_result.stats["time"] = time.thread_time() - initial_time
            planner_result.stats["iterations"] = planning_iterations
        
        return planner_result

    def _build_temporal_plan(self, temporal_state: TemporalState) -> Plan:
        """Convert a temporal state to a plan representation."""
        plan = Plan()

        # Reconstruct a meaningful state/action/state trace.
        # Temporal actions apply effects at completion; to show state changes, we
        # simulate the completion of actions in chronological completion order.
        # The action string still includes the start time annotation.
        sorted_actions = sorted(
            temporal_state.all_scheduled_actions,
            key=lambda a: (a.end_time, a.start_time, a.action.name),
        )

        # Match the classical Planner format: (state_before, action), ..., (final_state, None)
        if not sorted_actions:
            plan.append((State(dict(temporal_state.initial_state_vars)), None))
            return plan

        current_state = State(dict(temporal_state.initial_state_vars))
        final_state_hint = State(dict(temporal_state.state_vars))

        # Index compiled operator families by (parent_action_name, split_kind).
        compiled_ops: Dict[str, Dict[str, Action]] = {}
        for op in self._domain.actions.values():
            parent = getattr(op, "parent_action_name", None)
            kind = getattr(op, "split_kind", None)
            category = getattr(op, "split_category", None)
            if parent and kind and category:
                compiled_ops.setdefault(parent, {})[kind] = op

        def choose_outcome(outcomes: List[State], changed_keys: List[str]) -> State:
            if not outcomes:
                return current_state
            if len(outcomes) == 1:
                return outcomes[0]
            best = outcomes[0]
            best_score = -1
            for candidate in outcomes:
                score = 0
                for k in changed_keys:
                    if k in final_state_hint and candidate.get(k, None) == final_state_hint.get(k, None):
                        score += 1
                if score > best_score:
                    best = candidate
                    best_score = score
            return best

        def changed_keys_for(action: Action) -> List[str]:
            keys: List[str] = []
            for eff in (action._effects or []):
                if isinstance(eff, dict):
                    keys.extend(list(eff.keys()))
            return keys

        for scheduled in sorted_actions:
            if scheduled.action_type == "compiled" and scheduled.base_name:
                label_name = scheduled.base_name
            else:
                label_name = scheduled.action.name
            action_label = {
                "name": label_name,
                "time": float(scheduled.start_time),
                "duration": float(scheduled.end_time - scheduled.start_time),
            }
            # state before completion of this action
            plan.append((State(dict(current_state)), action_label))

            # Apply (one) completion outcome to advance the state snapshot.
            if scheduled.action_type == "compiled":
                base = scheduled.base_name
                candidates = []
                if scheduled.aborted_requested:
                    a = compiled_ops.get(base, {}).get("aborted")
                    if a is not None:
                        candidates.append(a)
                else:
                    for k in ("success", "failure"):
                        a = compiled_ops.get(base, {}).get(k)
                        if a is not None:
                            candidates.append(a)

                best_state = current_state
                best_score = -1
                for cand in candidates:
                    outs = cand.possible_outcomes(current_state)
                    ck = changed_keys_for(cand)
                    candidate_state = choose_outcome(outs, ck)
                    score = 0
                    for k in ck:
                        if k in final_state_hint and candidate_state.get(k, None) == final_state_hint.get(k, None):
                            score += 1
                    if score > best_score:
                        best_state = candidate_state
                        best_score = score
                current_state = State(dict(best_state))
            else:
                outcomes = scheduled.action.possible_outcomes(current_state)
                changed_keys = changed_keys_for(scheduled.action)
                current_state = State(dict(choose_outcome(outcomes, changed_keys)))

        # Final state
        plan.append((State(dict(current_state)), None))
        
        return plan
