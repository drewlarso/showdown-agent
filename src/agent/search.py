from agent.damage import calculate_damage_percent
from agent.simulate import (
    get_opponent_legal_actions,
    get_player_legal_actions,
    is_anyone_dead,
    simulate_switch,
    simulate_turn,
)
from agent.state import ActionState, GameState, PokeState, SwitchState

ALIVE_BONUS = 0.5
DAMAGE_FLOOR = 0.05


def get_best_action(state: GameState, depth: int):
    best_value = float("-inf")
    best_action = None

    for friendly_action in get_player_legal_actions(state):
        if state.friendly_pokemon.hp_percent <= 0 and isinstance(friendly_action, SwitchState):
            # forced switch
            value = max_node(simulate_switch(state, friendly_action.bench_index), depth)
        else:
            value = chance_node(state, friendly_action, depth)

        if value > best_value:
            best_value = value
            best_action = friendly_action

    return best_action


def max_node(state: GameState, depth: int):
    if depth <= 0 or is_anyone_dead(state):
        return evaluate(state)

    values = [chance_node(state, action, depth) for action in get_player_legal_actions(state)]
    return max(values, default=evaluate(state))


def chance_node(state: GameState, friendly_action: ActionState, depth: int) -> float:
    total = 0.0
    total_weight = 0.0

    for opponent_move in get_opponent_legal_actions(state):
        damage = calculate_damage_percent(state.opponent_pokemon, state.friendly_pokemon, opponent_move)
        weight = opponent_move.probability * (damage + DAMAGE_FLOOR)

        for probability, next_state in simulate_turn(state, friendly_action, opponent_move):
            total += weight * probability * max_node(next_state, depth - 1)
        total_weight += weight

    return total / total_weight


def evaluate(state: GameState):
    friendly_value = _pokemon_value(state.friendly_pokemon)
    for pokemon in state.friendly_bench:
        friendly_value += _pokemon_value(pokemon)
    return friendly_value - _pokemon_value(state.opponent_pokemon)


def _pokemon_value(pokemon: PokeState):
    if pokemon.hp_percent <= 0:
        return 0.0
    return pokemon.hp_percent + ALIVE_BONUS
