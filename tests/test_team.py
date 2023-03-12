from team import Team


_simple_pos_and_counts = {
        "qb": 3,
        "rb": 2,
        "te": 1,
    }


def test_team_init():
    team = Team(pos_and_counts_needed=_simple_pos_and_counts)
    assert team.needed_pos_counts == _simple_pos_and_counts
    assert team.current_pos_counts == {
        "qb": 0,
        "rb": 0,
        "te": 0,
    }
    assert team.score == 0


def test_team_add():
    team = Team(_simple_pos_and_counts)
    team.add_player("rb", 203)

    assert team.score == 203
    assert team.current_pos_counts["rb"] == 1
    assert team.current_pos_counts["qb"] == 0
