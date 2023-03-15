import copy
import math
import random
from typing import Optional

from team import Team
from data import Data


class MCTS:
    def __init__(
            self,
            random_seed: Optional[int] = None,
            c: float = math.sqrt(2),
            simulations: int = 100,
    ):
        self.c = c
        self.simulations = simulations
        self.state_info = dict()
        if random_seed is not None:
            random.seed(random_seed)

    def get_action(
            self,
            team: Team,
            data: Data,
            teams: list[Team],
            policies: list,
            current_round: int
    ) -> str:
        _data = copy.deepcopy(data)
        _teams = copy.deepcopy(teams)
        _policies = copy.deepcopy(policies)
        original_state = tuple(copy.deepcopy(team.pos_draft_order))
        needed_pos_counts = copy.deepcopy(team.needed_pos_counts)

        # selection and expansion
        state = copy.deepcopy(original_state)
        actions = []
        while True:
            next_action, fully_expanded = self._make_selection_or_expand(state, needed_pos_counts)
            actions.append(next_action)
            if not fully_expanded:
                if self.state_info.get(state) is None:
                    self.state_info[state] = {"count": 0, "actions": {next_action: (0, 0)}}
                elif self.state_info[state]["actions"].get(next_action) is None:
                    self.state_info[state]["actions"][next_action] = (0, 0)
                break

            # needs to be tuple for dict key
            # if else for first state of draft when state is empty
            state = tuple(list(state).append(next_action) if state else [next_action])

        # simulation
        # set offline draft policy with starting actions, then random till end
        from draft_policy import Policy
        remaining_actions = self._get_position_list(needed_pos_counts)
        # use a random policy for remainder of simulation
        random.shuffle(remaining_actions)
        actions += remaining_actions
        mcts_offline_policy = [{action: 1} for action in actions]
        mcts_policy = Policy("offline")
        mcts_policy.offline_policy = mcts_offline_policy
        # from draft import Draft
        # draft = Draft(team.needed_pos_counts, policies, teams)
        test = "hi"

        # backprop
        # get results and go through updating states

    def _make_selection_or_expand(self, state: tuple, needed_pos_counts: dict) -> tuple[str, bool]:
        fully_expanded = self._is_fully_expanded(state, needed_pos_counts.keys())
        if fully_expanded:
            action = self._make_selection(state)
        else:
            action = self._get_random_action(needed_pos_counts)

        needed_pos_counts[action] -= 1
        if needed_pos_counts[action] == 0:
            del needed_pos_counts[action]
        return action, fully_expanded

    def _is_fully_expanded(self, state, needed_pos) -> bool:
        is_fully_expanded = False
        if self.state_info.get(state) is not None:
            actions_explored = self.state_info[state]["actions"].keys()
            is_fully_expanded = (sorted(actions_explored) == sorted(needed_pos))

        return is_fully_expanded

    def _make_selection(self, state) -> str:
        actions = self.state_info[state]["actions"]
        _N = self.state_info[state]["count"]
        best_action = None
        highest_ucb1 = -math.inf
        for action, reward_and_na in actions.items():
            reward, na = reward_and_na
            ucb1 = (reward / na) + (self.c * (math.sqrt(math.log(_N) / na)))
            if ucb1 > highest_ucb1:
                highest_ucb1 = ucb1
                best_action = action

        return best_action

    def _get_random_action(self, needed_pos_counts: dict) -> str:
        return random.choice(self._get_position_list(needed_pos_counts))

    @staticmethod
    def _get_position_list(needed_pos_counts: dict) -> list:
        _positions_needed = []
        for pos, needed in needed_pos_counts.items():
            _positions_needed += [pos] * needed

        return _positions_needed
