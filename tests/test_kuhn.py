from games.kuhn_poker import Card, GameState, Move


def test_check_check_payoff():
    state = GameState([Card.Q, Card.J], [Move.CHECK, Move.CHECK])
    assert state.first_player_payoff() == 1

def test_bet_call_payoff():
    state = GameState([Card.K, Card.J], [Move.BET, Move.CALL])
    assert state.first_player_payoff() == 2

def test_bet_fold_payoff():
    state = GameState([Card.K, Card.J], [Move.BET, Move.FOLD])
    assert state.first_player_payoff() == 1
