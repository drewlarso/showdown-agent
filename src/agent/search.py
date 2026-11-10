from agent.simulate import get_legal_actions, is_anyone_dead, simulate_turn
from agent.state import GameState, MoveState


def get_best_move(state: GameState, depth: int):
    best_value = float("-inf")
    best_move = None

    for friendly_move in get_legal_actions(state, True):
        if friendly_move:
            value = chance_node(state, friendly_move, depth)
            if value > best_value:
                best_value = value
                best_move = friendly_move

    return best_move


def max_node(state: GameState, depth: int):
    if depth <= 0 or is_anyone_dead(state):
        return evaluate(state)

    best_value = float("-inf")

    for friendly_move in get_legal_actions(state, True):
        if friendly_move:
            value = chance_node(state, friendly_move, depth)
            best_value = max(best_value, value)

    if best_value == float("-inf"):
        return evaluate(state)

    return best_value


def chance_node(state: GameState, friendly_move: MoveState, depth: int):
    total = 0

    opponent_moves = get_legal_actions(state, False)
    for opponent_move in opponent_moves:
        for probability, next_state in simulate_turn(state, friendly_move, opponent_move):
            total += probability * max_node(next_state, depth - 1)

    return total / len(opponent_moves)


def evaluate(state: GameState):
    return state.friendly_pokemon.hp_percent - state.opponent_pokemon.hp_percent
