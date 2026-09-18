from cfr.cfr_kuhn import CFRTrainer
from games.kuhn_poker import Card, GameState, Move


def possible_hands() -> list[list[Card]]:
    result: list[list[Card]] = []

    for card_p1 in Card:
        for card_p2 in Card:
            if card_p1 == card_p2:
                continue
            else:
                result.append([card_p1, card_p2])

    return result


def training(iterations: int) -> dict[tuple, dict[Move, float]]:
    trainer = CFRTrainer()
    hands = possible_hands()

    for iteration in range(0,iterations):
        for hand in hands:
            trainer.cfr(GameState(hand, []), [1, 1])

    strategy_sum = trainer.strategy_sum
    final_strategy: dict[tuple, dict[Move, float]] = {}

    for information_set, moves in strategy_sum.items():
        possible_moves_sum = sum(moves.values())
        for move in moves:
            if information_set not in final_strategy:
                final_strategy[information_set] = {}
            final_strategy[information_set][move] = strategy_sum[information_set][move] / possible_moves_sum

    return final_strategy

if __name__ == "__main__":
    final_strategy = training(10000)
    print(final_strategy)