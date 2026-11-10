from dataclasses import replace

from agent.damage import calculate_damage_percent, get_stat
from agent.state import GameState, MoveState

ROLL_RANGES = [(0.25, 0.85), (0.5, 0.925), (0.25, 1.0)]


def get_legal_actions(state: GameState, player_attacking: bool):
    # add switches here later
    if player_attacking:
        return state.friendly_pokemon.moves
    else:
        return state.opponent_pokemon.moves or [None]


def is_anyone_dead(state: GameState):
    friendly_hp = state.friendly_pokemon.hp_percent
    opponent_hp = state.opponent_pokemon.hp_percent
    return friendly_hp <= 0 or opponent_hp <= 0


def simulate_attack(state: GameState, move: MoveState | None, player_attacking: bool):
    if move is None:
        return [(1.0, state)]

    possibilities: list[tuple[float, GameState]] = []

    if player_attacking:
        attacker = state.friendly_pokemon
        defender = state.opponent_pokemon
    else:
        attacker = state.opponent_pokemon
        defender = state.friendly_pokemon

    if move.accuracy < 1.0:
        possibilities.append((1 - move.accuracy, state))

    for probability, multiplier in ROLL_RANGES:
        damage_percent = calculate_damage_percent(attacker, defender, move, multiplier)
        resulting_hp = max(0.0, defender.hp_percent - damage_percent)

        damaged_defender = replace(defender, hp_percent=resulting_hp)
        if player_attacking:
            new_state = replace(state, opponent_pokemon=damaged_defender)
        else:
            new_state = replace(state, friendly_pokemon=damaged_defender)

        possibilities.append((probability * move.accuracy, new_state))

    return possibilities


def simulate_turn(state: GameState, friendly_move: MoveState, opponent_move: MoveState | None):
    friendly_priority = friendly_move.priority
    opponent_priority = opponent_move.priority if opponent_move else 0
    friendly_speed = get_stat(state.friendly_pokemon, "spe")
    opponent_speed = get_stat(state.opponent_pokemon, "spe")

    if friendly_priority != opponent_priority:
        orders = [(1.0, friendly_priority > opponent_priority)]
    elif friendly_speed != opponent_speed:
        orders = [(1.0, friendly_speed > opponent_speed)]
    else:
        orders = [(0.5, True), (0.5, False)]

    possibilities: list[tuple[float, GameState]] = []

    for probability, friendly_first in orders:
        if friendly_first:
            first_move = friendly_move
            second_move = opponent_move
        else:
            first_move = opponent_move
            second_move = friendly_move

        for first_probability, first_state in simulate_attack(state, first_move, friendly_first):
            if is_anyone_dead(first_state):
                possibilities.append((probability * first_probability, first_state))
                continue

            for second_probability, second_state in simulate_attack(first_state, second_move, not friendly_first):
                possibilities.append((probability * first_probability * second_probability, second_state))

    return possibilities
