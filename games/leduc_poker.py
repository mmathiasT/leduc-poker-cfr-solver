from enum import Enum, IntEnum


class Move(Enum):
    CHECK = "check"
    BET = "bet"
    CALL = "call"
    FOLD = "fold"
    RAISE = "raise"

class Card(IntEnum):
    J = 0
    Q = 1
    K = 2

class GameState:
    def __init__(self, players_cards: list[Card], move_history: list[Move], contributions: list[int],
                community_card: Card, current_round_raises: int, round_number: int, round_move_history: list[Move]):
        self.players_cards: list[Card] = players_cards
        self.move_history: list[Move] = move_history
        self.community_card: Card = community_card
        self.contributions: list[int] = contributions
        self.current_round_raises = current_round_raises
        self.round_number = round_number
        self.round_move_history = round_move_history

    def current_player(self) -> int:
        """Return the number of the player that moves next."""
        return len(self.round_move_history) % 2

    def possible_moves(self) -> list[Move]:
        check_or_bet: list[Move] = [Move.CHECK, Move.BET]
        call_or_fold: list[Move] = [Move.CALL, Move.FOLD]

        if len(self.round_move_history) == 0:
            return check_or_bet
        elif self.round_move_history[-1] == Move.BET or self.round_move_history[-1] == Move.RAISE:
            if self.current_round_raises < 2:
                return call_or_fold + [Move.RAISE]
            else:
                return call_or_fold
        elif self.round_move_history[-1] == Move.FOLD:
            return []
        elif self.round_move_history[-1] == Move.CALL or (
                len(self.round_move_history) > 1 and self.round_move_history[-1] == Move.CHECK and self.round_move_history[-2] == Move.CHECK):
            if self.round_number == 1:  # Start the second round
                return check_or_bet
            else:
                return []
        elif self.round_move_history[-1] == Move.CHECK:
            return check_or_bet
        else:
            return []

    def play(self, move: Move) -> "GameState":
        player = self.current_player()
        new_contributions = self.contributions.copy()
        new_raises = self.current_round_raises
        bet = 2 * self.round_number
        if move == Move.BET:
            new_contributions[player] = self.contributions[player] + bet
        elif move == Move.CALL:
            new_contributions[player] = self.contributions[1 ^ player]
        elif move == Move.RAISE:
            new_contributions[player] = self.contributions[1 ^ player] + bet
            new_raises += 1
        return GameState(self.players_cards, self.move_history + [move], new_contributions, self.community_card,
            new_raises, self.round_number, self.round_move_history + [move])

    def winner(self) -> int:
        if self.players_cards[0] == self.community_card:
            return 0
        elif self.players_cards[1] == self.community_card:
            return 1
        elif self.players_cards[0] > self.players_cards[1]:
            return 0
        elif self.players_cards[0] < self.players_cards[1]:
            return 1
        else:
            return -1 # Draw.

    def first_player_payoff(self) -> int:
        """ Return the first player payoff. """
        moves = len(self.move_history)
        player = self.current_player()

        if moves == 0:
            raise ValueError("Moves history error! - Empty history")

        if self.move_history[-1] == Move.FOLD:
            if player == 1:
                return -self.contributions[0]
            else:
                return self.contributions[1]
        else:
            # Showdown -> contributions[0] == contributions[1]
            game_winner: int = self.winner()
            if game_winner == 0:
                return self.contributions[0]
            elif game_winner == 1:
                return -self.contributions[0]
            else:
                return 0

    def information_set(self) -> tuple:
        if self.round_number == 1:
            return (self.players_cards[self.current_player()], None, tuple(self.move_history))
        else:
            return (self.players_cards[self.current_player()], self.community_card, tuple(self.move_history))

    def next_round(self) -> "GameState":
        return GameState(self.players_cards, self.move_history, self.contributions, self.community_card , 0,
            self.round_number + 1, [])