import random
from django.shortcuts import render, redirect
from games.leduc_poker import GameState, Card, Move
from pokerbot.apps import STRATEGY

# Create your views here.
def save_game_state(session, game_state):
    session["players_cards"] = [card.value for card in game_state.players_cards]
    session["move_history"] = [move.value for move in game_state.move_history]
    session["contributions"] = game_state.contributions
    session["community_card"] = game_state.community_card.value
    session["current_round_raises"] = game_state.current_round_raises
    session["round_move_history"] = [move.value for move in game_state.round_move_history]
    session["round_number"] = game_state.round_number

def load_game_state(session):
    return GameState(
        players_cards=[Card(v) for v in session["players_cards"]],
        move_history=[Move(v) for v in session["move_history"]],
        contributions=session["contributions"],
        community_card=Card(session["community_card"]),
        current_round_raises=session["current_round_raises"],
        round_number=session["round_number"],
        round_move_history=[Move(v) for v in session["round_move_history"]],
    )

def start_game(request):
    deck = [Card.J, Card.J, Card.Q, Card.Q, Card.K, Card.K]
    dealt = random.sample(deck, 3)

    players_cards = dealt[:2]
    community_card = dealt[2]

    game_state = GameState(players_cards, [], [1, 1], community_card, 0, 1, [])
    save_game_state(request.session, game_state)

    request.session.setdefault("player_balance", 0)
    request.session["payoff_recorded"] = False
    request.session["history_log"] = []

    return redirect("game")

def format_distribution(distribution):
    return [(m.value, round(p * 100, 1)) for m, p in sorted(distribution.items(), key=lambda item: -item[1])]

def log_move(session, player, move_value, distribution):
    history = session.get("history_log", [])
    history.append({"player": player, "move": move_value, "distribution": distribution})
    session["history_log"] = history

def game(request):
    if "players_cards" not in request.session:
        return redirect("start_game")

    game_state = load_game_state(request.session)

    while game_state.possible_moves() and game_state.current_player() == 1:
        move, distribution = sample_bot_move(game_state)
        log_move(request.session, "Bot", move.value, format_distribution(distribution))
        game_state = game_state.play(move)
        game_state = maybe_advance_round(game_state)

    save_game_state(request.session, game_state)

    game_over = (len(game_state.possible_moves()) == 0)
    payoff = game_state.first_player_payoff() if game_over else None

    if game_over and not request.session.get("payoff_recorded"):
        request.session["player_balance"] = request.session.get("player_balance", 0) + payoff
        request.session["payoff_recorded"] = True

    context = {
        "player_card": game_state.players_cards[0].name,
        "community_card": game_state.community_card.name if game_state.round_number == 2 else None,
        "contributions": game_state.contributions,
        "pot_total": sum(game_state.contributions),
        "bet_size": 2 * game_state.round_number,
        "history_log": request.session.get("history_log", []),
        "possible_moves": game_state.possible_moves(),
        "game_over": game_over,
        "payoff": payoff,
        "player_balance": request.session.get("player_balance", 0),
        "bot_balance": -request.session.get("player_balance", 0),
    }
    return render(request, "pokerbot/game.html", context)

def act(request):
    game_state = load_game_state(request.session)
    move = Move(request.POST["move"])

    if move not in game_state.possible_moves():
        return redirect("game")

    game_state = game_state.play(move)
    game_state = maybe_advance_round(game_state)
    save_game_state(request.session, game_state)
    log_move(request.session, "You", move.value, None)
    return redirect("game")

def maybe_advance_round(game_state):
    round_over = game_state.round_move_history and (
        game_state.round_move_history[-1] == Move.CALL or
        (len(game_state.round_move_history) > 1 and game_state.round_move_history[-2:] == [Move.CHECK, Move.CHECK])
    )
    if round_over and game_state.round_number == 1:
        return game_state.next_round()
    return game_state

def sample_bot_move(game_state):
    infoset = game_state.information_set()
    distribution = STRATEGY[infoset]
    moves = list(distribution.keys())
    weights = list(distribution.values())
    chosen = random.choices(moves, weights=weights, k=1)[0]
    return chosen, distribution