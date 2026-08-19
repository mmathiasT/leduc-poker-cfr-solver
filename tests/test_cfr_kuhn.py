from train_kuhn import training
from games.kuhn_poker import Move, Card

def strategy() -> dict[tuple, dict[Move, float]]:
    return training(10000)

def test_kings_call():
    result_strategy = strategy()
    assert result_strategy[(Card.K, (Move.BET, ))][Move.CALL] > 0.95

def test_jack_dont_call():
    result_strategy = strategy()
    assert result_strategy[(Card.J, (Move.BET, ))][Move.CALL] < 0.05

def test_king_bets_three_times_more_than_jack_bluffs():
    result_strategy = strategy()
    assert abs(3 * result_strategy[(Card.J, ())][Move.BET] - result_strategy[(Card.K, ())][Move.BET]) < 0.05