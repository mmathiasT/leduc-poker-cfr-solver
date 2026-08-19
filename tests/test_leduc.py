from games.leduc_poker import Move, GameState, Card

def test_raise_cap_removes_raise_option():
    state = GameState([Card.K, Card.Q], [Move.BET, Move.RAISE, Move.RAISE], [1, 1],
        Card.J, 2, 1, [Move.BET, Move.RAISE, Move.RAISE])
    assert state.possible_moves() == [Move.CALL, Move.FOLD]

def test_fold_ends_game_in_round_one():
    state = GameState([Card.K, Card.Q], [Move.BET, Move.FOLD], [1, 1],
        Card.J, 0, 1, [Move.BET, Move.FOLD])
    assert state.possible_moves() == []

def test_bet_updates_contributions():
    state = GameState([Card.K, Card.Q], [], [1, 1], Card.J, 0, 1, [])
    state = state.play(Move.BET)
    assert state.contributions == [3, 1]

def test_call_matches_opponent_contribution():
    state = GameState([Card.K, Card.Q], [Move.BET], [3, 1], Card.J, 0, 1, [Move.BET])
    state = state.play(Move.CALL)
    assert state.contributions == [3, 3]

def test_raise_increases_contribution_and_counter():
    state = GameState([Card.K, Card.Q], [Move.BET], [3, 1], Card.J, 0, 1, [Move.BET])
    state = state.play(Move.RAISE)
    assert state.contributions == [3, 5]
    assert state.current_round_raises == 1

def test_pair_beats_higher_card():
    state = GameState([Card.Q, Card.K], [], [1, 1], Card.Q, 0, 2, [])
    assert state.winner() == 0

def test_high_card_wins_without_pair():
    state = GameState([Card.Q, Card.J], [], [1, 1], Card.K, 0, 2, [])
    assert state.winner() == 0

def test_draw_when_no_pair_and_equal_cards():
    state = GameState([Card.Q, Card.Q], [], [1, 1], Card.K, 0, 2, [])
    assert state.winner() == -1

def test_fold_payoff_favors_opponent_of_folder():
    state = GameState([Card.K, Card.J], [], [1, 1], Card.Q, 0, 1, [])
    state = state.play(Move.BET)
    state = state.play(Move.FOLD)
    assert state.first_player_payoff() == 1

def test_fold_payoff_negative_when_first_player_folds():
    state = GameState([Card.K, Card.J], [], [1, 1], Card.Q, 0, 1, [])
    state = state.play(Move.CHECK)
    state = state.play(Move.BET)
    state = state.play(Move.FOLD)
    assert state.first_player_payoff() == -1

def test_showdown_payoff_for_winner():
    state = GameState([Card.K, Card.Q], [], [1, 1], Card.K, 0, 1, [])
    state = state.play(Move.CHECK)
    state = state.play(Move.CHECK)
    state = state.next_round()
    state = state.play(Move.CHECK)
    state = state.play(Move.CHECK)
    assert state.first_player_payoff() == 1

def test_next_round_resets_round_state():
    state = GameState([Card.K, Card.Q], [Move.CHECK, Move.CHECK], [1, 1],
        Card.J, 0, 1, [Move.CHECK, Move.CHECK])
    new_state = state.next_round()
    assert new_state.round_number == 2
    assert new_state.round_move_history == []
    assert new_state.current_round_raises == 0
    assert new_state.move_history == [Move.CHECK, Move.CHECK]

def test_round_one_call_continues_to_round_two_options():
    state = GameState([Card.K, Card.Q], [Move.BET, Move.CALL], [3, 3],
        Card.J, 0, 1, [Move.BET, Move.CALL])
    assert state.possible_moves() == [Move.CHECK, Move.BET]

def test_round_two_call_ends_game():
    state = GameState([Card.K, Card.Q], [Move.BET, Move.CALL, Move.BET, Move.CALL], [3, 3],
        Card.J, 0, 2, [Move.BET, Move.CALL])
    assert state.possible_moves() == []
