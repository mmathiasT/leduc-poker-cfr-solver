from games.leduc_poker import Card, GameState, Move
from cfr.cfr_leduc import CFRTrainer
from itertools import permutations

def possible_hands() -> list[tuple[Card, Card, Card]]:
    deck = [Card.J, Card.J, Card.Q, Card.Q, Card.K, Card.K]
    return list(permutations(deck, 3))

def training(iterations: int) -> dict[tuple, dict[Move, float]]:
    trainer = CFRTrainer()
    hands = possible_hands()

    for iteration in range(0,iterations):
        for hand in hands:
            players_cards = list(hand[:2])
            trainer.cfr(GameState(players_cards, [], [1,1], hand[2], 0, 1, []), [1, 1])

    strategy_sum = trainer.strategy_sum
    final_strategy: dict[tuple, dict[Move, float]] = {}

    for information_set, moves in strategy_sum.items():
        possible_moves_sum = sum(moves.values())
        for move in moves:
            if information_set not in final_strategy:
                final_strategy[information_set] = {}
            if possible_moves_sum == 0:
                final_strategy[information_set][move] = 1  / len(moves)   
            else:
                final_strategy[information_set][move] = strategy_sum[information_set][move] / possible_moves_sum

    return final_strategy

if __name__ == "__main__":
    final_strategy = training(100)
    print(final_strategy)