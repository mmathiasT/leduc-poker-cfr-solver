from enum import Enum, IntEnum


class Move(Enum):
    CHECK = "check"
    BET = "bet"
    CALL = "call"
    FOLD = "fold"

class Card(IntEnum):
    J = 0
    Q = 1
    K = 2

class GameState:
    def __init__(self, players_cards: list[Card], move_history: list[Move]):
        self.players_cards = players_cards
        self.move_history = move_history

    def current_player(self) -> int:
        """Return the number of the player that moves next."""
        return len(self.move_history) % 2

    def possible_moves(self) -> list[Move]:
        check_or_bet: list[Move] = [Move.CHECK, Move.BET]
        call_or_fold: list[Move] = [Move.CALL, Move.FOLD]

        if len(self.move_history) == 0:
            return check_or_bet
        elif self.move_history[-1] == Move.BET:
            return call_or_fold
        elif (self.move_history[-1] in call_or_fold) or (
                len(self.move_history) > 1 and self.move_history[-1] == Move.CHECK and self.move_history[-2] == Move.CHECK):
            return []
        elif self.move_history[-1] == Move.CHECK:
            return check_or_bet
        else:
            return []

    def play(self, move: Move) -> "GameState":
        return GameState(self.players_cards, self.move_history + [move])

    def first_player_payoff(self) -> int:
        """ Return the first player payoff. """
        moves = len(self.move_history)

        if moves == 0:
            raise ValueError("Moves history error! - Empty history")

        abs_profit = 0
        if self.move_history[-1] == Move.FOLD:
            abs_profit = 1
        elif self.move_history[-1] == Move.CALL:
            abs_profit = 2
        elif self.move_history[-1] == Move.CHECK:
            abs_profit = 1

        if self.move_history[-1] == Move.FOLD:
            if moves % 2 == 0:                      # Second player folded.
                return abs_profit
            else:
                return -abs_profit
        elif moves > 1 and (self.move_history[-1] == Move.CHECK and self.move_history[-2] == Move.CHECK) or (
            self.move_history[-1] == Move.CALL):    # Showdown.
            if self.players_cards[0] > self.players_cards[1]:
                return abs_profit
            else:
                return -abs_profit
        else:
            raise ValueError("Moves history error!")

    def information_set(self) -> tuple:
        return (self.players_cards[self.current_player()], tuple(self.move_history))