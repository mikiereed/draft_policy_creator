from draft import Draft
from draft_policy import Policy

_simple_pos_and_counts = {
    "qb": 3,
    "rb": 2,
    "te": 1,
}

_policies_all_random = [Policy("random")]


def test_init():
    team_count = 5
    draft = Draft(
        needed_pos_and_counts=_simple_pos_and_counts,
        policies=_policies_all_random * team_count,
    )

    assert draft.teams[3].needed_pos_counts == _simple_pos_and_counts
    assert draft.teams[2].score == 0
    assert len(draft.teams) == 5
    assert draft.rounds == 6


def test_next_player_selection():
    team_count = 3
    draft = Draft(
        needed_pos_and_counts=_simple_pos_and_counts,
        policies=_policies_all_random * team_count,
    )
    assert draft.current_team_selecting.score == 0

    draft._next_team_selection("qb", 50.4)
    assert draft.current_team_index == 1

    draft._next_team_selection("rb", 43.2)
    assert draft.current_team_index == 2
    assert draft.current_round == 1

    draft._next_team_selection("qb", 45.5)
    assert draft.current_team_index == 2
    assert draft.current_round == 2

    draft._next_team_selection("qb", 30.0)
    assert draft.current_team_index == 1
    assert draft.teams[2].score == 75.5
