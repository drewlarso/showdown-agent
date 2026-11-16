from agent.engine.mechanics import get_damage_percent
from agent.engine.simulate import (
    get_friendly_actions,
    has_anyone_fainted,
    simulate_switch,
    simulate_turn,
)
from agent.engine.state import Action, GameState, PokemonState, load_game_state

ALIVE_BONUS = 0.5
DAMAGE_FLOOR = 0.05


def search_python(state_json: str, depth: int) -> Action | None:
    return get_best_action(load_game_state(state_json), depth)


def get_best_action(state: GameState, depth: int) -> Action | None:
    best_action = None
    best_value = float("-inf")

    for action, value in get_action_values(state, depth):
        if value > best_value:
            best_action = action
            best_value = value

    return best_action


def get_action_values(state: GameState, depth: int) -> list[tuple[Action, float]]:
    action_values: list[tuple[Action, float]] = []

    for action in get_friendly_actions(state):
        if action.is_switch and state.friendly_pokemon.hp_percent <= 0:
            switched_state = simulate_switch(state, action.index)
            value = max_node(switched_state, depth)
        else:
            value = chance_node(state, action, depth)

        action_values.append((action, value))

    return action_values


def chance_node(state: GameState, friendly_action: Action, depth: int) -> float:
    weighted_value = 0.0
    total_weight = 0.0

    for opponent_move in state.opponent_pokemon.moves:
        damage = get_damage_percent(state.opponent_pokemon, state.friendly_pokemon, opponent_move)
        move_weight = opponent_move.prior * (damage + DAMAGE_FLOOR)

        for outcome_probability, next_state in simulate_turn(state, friendly_action, opponent_move):
            next_value = max_node(next_state, depth - 1)
            weighted_value += move_weight * outcome_probability * next_value

        total_weight += move_weight

    return weighted_value / total_weight


def max_node(state: GameState, depth: int) -> float:
    if depth <= 0 or has_anyone_fainted(state):
        return get_state_value(state)

    action_values = get_action_values(state, depth)
    if not action_values:
        return get_state_value(state)

    return max(value for _, value in action_values)


def get_state_value(state: GameState) -> float:
    friendly_value = get_pokemon_value(state.friendly_pokemon)
    for pokemon_state in state.friendly_bench:
        friendly_value += get_pokemon_value(pokemon_state)

    return friendly_value - get_pokemon_value(state.opponent_pokemon)


def get_pokemon_value(pokemon_state: PokemonState) -> float:
    if pokemon_state.hp_percent <= 0:
        return 0.0
    return pokemon_state.hp_percent + ALIVE_BONUS
