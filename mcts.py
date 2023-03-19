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
            simulations: int = 250,
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
        self.state_info = dict()
        for _ in range(self.simulations):
            _data = copy.deepcopy(data)
            _teams = copy.deepcopy(teams)
            _policies = copy.deepcopy(policies)
            needed_pos_counts = copy.deepcopy(team.needed_pos_counts)
            team_index = teams.index(team)

            # selection and expansion
            state = tuple(copy.deepcopy(team.pos_draft_order))
            actions = []
            while True:
                if not needed_pos_counts:  # no more picks can be made
                    break

                next_action, fully_expanded = self._make_selection_or_expand(state, needed_pos_counts)
                actions.append(next_action)
                # needs to be tuple for dict key
                state = list(state)
                state.append(next_action)
                state = tuple(state)

                if not fully_expanded:
                    break


            # simulation
            # set offline draft policy with selection actions, then random till end
            from draft_policy import Policy
            mcts_policy = Policy("offline")
            mcts_offline_policy = dict()
            for i in range(current_round, current_round + len(actions)):
                mcts_offline_policy[i] = {actions[i - current_round]: 1}
            # use a random policy for remainder of simulation
            # for all rounds not included in offline policy, draft_policy will use a random action
            mcts_policy.offline_policy = mcts_offline_policy
            _policies[team_index] = mcts_policy
            from draft import Draft
            draft = Draft(policies=_policies, teams=_teams, current_round=current_round, current_team_index=team_index)
            draft.simulate(_data)
            place = list(draft.results()).index(team_index) + 1
            if place <= len(_policies) * 0.5:  # only top 50% get reward
                reward = 1 / (math.pow(2, place - 1))  # 1 for 1st, 0.5 for 2nd, 0.25 for 3rd, etc
            else:
                reward = 0

            # backpropagation
            actions_reversed = reversed(actions)
            for action in actions_reversed:
                self._update_state_info(state, reward)
                state = self._get_previous_state(state)

            self._update_state_info(state, reward)  # root

        return self._best_action(team)

    def _best_action(self, team: Team) -> str:
        state = tuple(copy.deepcopy(team.pos_draft_order))
        best_value = -math.inf
        best_action = None
        for action in team.needed_pos_counts:
            reward, count = self.state_info.get(self._get_next_state(state, action), [0, 0])
            value = (reward / count) if count != 0 else -math.inf
            if value > best_value:
                best_value = value
                best_action = action

        # print(best_action)
        return best_action

    def _update_state_info(self, state, reward):
        if self.state_info.get(state) is None:
            self.state_info[state] = [0, 0]
        self.state_info[state][0] += reward
        self.state_info[state][1] += 1  # na

    def _make_selection_or_expand(self, state: tuple, needed_pos_counts: dict) -> tuple[str, bool]:
        fully_expanded = self._is_fully_expanded(state, needed_pos_counts.keys())
        if fully_expanded:
            action = self._make_selection(state, list(needed_pos_counts.keys()))
        else:
            action = self._get_random_action(needed_pos_counts)

        needed_pos_counts[action] -= 1
        if needed_pos_counts[action] == 0:
            del needed_pos_counts[action]
        return action, fully_expanded

    def _is_fully_expanded(self, state, possible_actions) -> bool:
        for action in possible_actions:
            if self.state_info.get(self._get_next_state(state, action), None) is None:
                return False

        return True

    def _make_selection(self, state: tuple, possible_actions: list) -> str:
        _N = self.state_info[state][1]
        actions = dict()
        for action in possible_actions:
            actions[action] = self.state_info[self._get_next_state(state, action)]
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

    @staticmethod
    def _get_previous_state(state: tuple) -> tuple:
        previous_state = tuple(list(state)[:-1])  # to get previous state, remove last action

        return previous_state

    @staticmethod
    def _get_next_state(state: tuple, action: str) -> tuple:
        if state:
            next_state = list(state)
            next_state.append(action)
            next_state = tuple(next_state)
        else:
            next_state = tuple([action])

        return next_state
