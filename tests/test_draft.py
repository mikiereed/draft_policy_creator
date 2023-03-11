from draft import Draft


_simple_pos_and_counts = {
        "qb": 3,
        "rb": 2,
        "te": 1,
    }


def test_init():
    draft = Draft(5, _simple_pos_and_counts)

    assert draft.teams[3].needed_pos_counts == _simple_pos_and_counts
    assert draft.teams[2].score == 0
    assert len(draft.teams) == 5
    assert draft.rounds == 6


def test_next_player_selection():
    draft = Draft(3, _simple_pos_and_counts)
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
