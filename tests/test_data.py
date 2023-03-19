from data import Data

_simple_pos_and_counts = {
        "qb": 3,
        "rb": 2,
        "te": 1,
    }


def test_data_init():
    data = Data(3, _simple_pos_and_counts, percent_extra=0, random_seed=1)

    assert len(data.players["qb"]) == 9
    assert len(data.players["rb"]) == 6
    assert len(data.players["te"]) == 3

    assert data.players["qb"][0] == 207.8746937695424  # random_seed will ensure this is always the same


def test_data_init_percent_extra():
    data = Data(3, _simple_pos_and_counts, percent_extra=50, random_seed=1)

    assert len(data.players["qb"]) == 14
    assert len(data.players["rb"]) == 9
    assert len(data.players["te"]) == 5
