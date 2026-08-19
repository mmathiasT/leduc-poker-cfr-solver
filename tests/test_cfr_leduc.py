from train_leduc import training
from games.leduc_poker import Move, Card
import pytest

def strategy() -> dict[tuple, dict[Move, float]]:
    return training(10000)

def test_kings_call():
    result_strategy = strategy()
    assert result_strategy[Card.K, Card.K, (Move.CHECK, Move.CHECK)][Move.BET] > 0.97

def test_fold():
    result_strategy = strategy()
    assert result_strategy[Card.J, Card.K, (Move.CHECK, Move.BET)][Move.FOLD] > 0.60

def test_bet_frequency_monotonic_in_card_rank():
    result_strategy = strategy()
    assert result_strategy[Card.J, None, ()][Move.BET] < result_strategy[Card.Q, None, ()][Move.BET]
    assert result_strategy[Card.Q, None, ()][Move.BET] < result_strategy[Card.K, None, ()][Move.BET]
                 
def test_probabilities_sum_to_one():
    result_strategy = strategy()
    for information_set, moves in result_strategy.items():
        total = sum(moves.values())
        assert total == pytest.approx(1.0)