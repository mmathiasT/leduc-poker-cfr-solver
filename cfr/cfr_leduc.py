from games.leduc_poker import Move, GameState

def regret_matching(regret_sum_current_set: dict[Move, float], possible_moves: list[Move]) -> dict[Move, float]:
    """
    Returns the strategy as ({action: chance}) dictionary.
    Only moves that the program regrets not doing have positive reach probability.
    """
    chances: dict[Move, float] = {}
    positive_regrets_sum = 0
    for move in possible_moves:
        if regret_sum_current_set[move] > 0:
            positive_regrets_sum += regret_sum_current_set[move]

    if positive_regrets_sum == 0:    # All moves should have the same chance.
        for move in possible_moves:
            chances[move] = 1 / len(possible_moves)
    else:
        for move in possible_moves:
            if regret_sum_current_set[move] > 0:
                chances[move] = regret_sum_current_set[move] / positive_regrets_sum
            else:
                chances[move] = 0

    return chances


class CFRTrainer:
    def __init__(self):
        self.regret_sum: dict[tuple, dict[Move, float]] = {}    # Cumulative regret for each action within each information set.
        self.strategy_sum: dict[tuple, dict[Move, float]] = {}  # Cumulative reach-weighted strategy for each action

    def cfr(self, game_state: GameState, reach_probability: list) -> float:
        """ Recursively computes the value of game_state (from player 1's perspective),
            updating regret_sum and strategy_sum along the way."""
        possible_moves = game_state.possible_moves()

        round_over = game_state.round_move_history and (game_state.round_move_history[-1] == Move.CALL or
            (len(game_state.round_move_history) > 1 and game_state.round_move_history[-2:] == [Move.CHECK, Move.CHECK]))

        if round_over and game_state.round_number == 1:
            game_state = game_state.next_round()
            possible_moves = game_state.possible_moves()
        elif len(possible_moves) == 0:
            return game_state.first_player_payoff()

        player = game_state.current_player()
        information_set = game_state.information_set()

        if information_set not in self.regret_sum:
            self.regret_sum[information_set] = {}
            for move in possible_moves:
                self.regret_sum[information_set][move] = 0

        if information_set not in self.strategy_sum:
            self.strategy_sum[information_set] = {}
            for move in possible_moves:
                self.strategy_sum[information_set][move] = 0

        strategy = regret_matching(self.regret_sum[information_set], possible_moves)

        move_value = {}
        info_set_result = 0
        for move in strategy:
            previous_probability = reach_probability[player]
            reach_probability[player] *= strategy[move]

            move_value[move] = self.cfr(game_state.play(move), reach_probability)
            reach_probability[player] = previous_probability

            info_set_result += move_value[move] * strategy[move]

        if player == 1:
            sign = -1
        else:
            sign = 1

        for move in move_value:
            # Counterfactual regret (Zinkevich). Weighted by opponents reach only, so rarely-chosen actions still get a fair signal.
            difference = sign * (move_value[move] - info_set_result)
            self.regret_sum[information_set][move] += (difference * reach_probability[player ^ 1])

            # Accumulated strategy, averaged after training. Only the time-averaged strategy is guaranteed to converge to a Nash equilibrium.
            self.strategy_sum[information_set][move] += (strategy[move] * reach_probability[player])

        return info_set_result