import random
from typing import Optional

from data import Data
from draft_policy import Policy
from team import Team


class Draft:
    def __init__(
            self,
            needed_pos_and_counts: dict,
            policies: list[Policy],
            teams: Optional[list[Team]] = None,
    ):
        assert teams is not None or policies is not None
        if teams is None:
            teams = [Team(needed_pos_and_counts) for _ in range(len(policies))]
        self.teams = teams
        self.policies = policies
        self.team_count = len(policies)
        self.current_team_index = 0
        self.current_pick = 1
        self.rounds = sum(needed_pos_and_counts.values())
        self.current_round = 1

    @property
    def current_team_selecting(self):
        return self.teams[self.current_team_index]

    def simulate(self, data: Data) -> None:
        while self.current_pick <= self.rounds * self.team_count:
            current_team = self.current_team_selecting
            position_to_draft = self.policies[self.current_team_index].get_action(
                team=current_team,
                current_round=self.current_round,
                data=data,
                policies=self.policies,
                teams=self.teams,
            )  # TODO: turn this into a dataclass
            assert position_to_draft is not None
            score = data.get_and_remove_score(position_to_draft)
            self._next_team_selection(position_to_draft, score)

    def _next_team_selection(self, pos: str, score: float) -> None:
        self.current_team_selecting.add_player(pos, score)
        self._update_current_team_selecting()
        self.current_pick += 1

    def _update_current_team_selecting(self) -> None:
        current_team = self.current_team_index
        if self.current_round % 2 == 1:  # odd, move forward through teams
            if current_team + 1 < self.team_count:
                self.current_team_index += 1
            else:
                self.current_round += 1
        else:  # even, move backward through teams
            if current_team - 1 >= 0:
                self.current_team_index -= 1
            else:
                self.current_round += 1

    def results(self):
        scores = dict()
        for team in range(self.team_count):
            scores[team] = self.teams[team].score

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        mean_score = sum(scores.values()) / len(scores)

        return {team: {
            "score": score - mean_score,
            "position_draft_order": self.teams[team].pos_draft_order,
        } for team, score in sorted_scores}

    def __repr__(self):
        print_string = ""
        results = self.results()
        for team in results:
            print_string += f"{self.policies[team].policy}\n"
            print_string += f"{team}: {results[team]['score']} {results[team]['position_draft_order']}\n"

        return print_string
