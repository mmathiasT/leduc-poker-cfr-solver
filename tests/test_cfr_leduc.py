import pytest

from games.leduc_poker import Card, Move
from train_leduc import training


@pytest.fixture(scope="module")
def strategy() -> dict[tuple, dict[Move, float]]:
    return training(1000)

def test_kings_call(strategy):
    assert strategy[Card.K, Card.K, (Move.CHECK, Move.CHECK)][Move.BET] > 0.90

def test_fold(strategy):
    assert strategy[Card.J, Card.K, (Move.CHECK, Move.CHECK, Move.BET)][Move.FOLD] > 0.60

def test_bet_frequency_monotonic_in_card_rank(strategy):
    assert strategy[Card.J, None, ()][Move.BET] < strategy[Card.Q, None, ()][Move.BET]
    assert strategy[Card.J, None, ()][Move.BET] < strategy[Card.K, None, ()][Move.BET]

def test_probabilities_sum_to_one(strategy):
    for information_set, moves in strategy.items():
        total = sum(moves.values())
        assert total == pytest.approx(1.0)