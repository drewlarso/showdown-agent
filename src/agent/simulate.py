from dataclasses import replace

from agent.damage import calculate_damage_percent
from agent.items import end_of_turn_hp, modify_speed
from agent.state import ActionState, GameState, MoveState, SwitchState

# ROLL_RANGES = [(0.25, 0.85), (0.5, 0.925), (0.25, 1.0)]
ROLL_RANGES = [(1.0, 0.925)]


def get_player_legal_actions(state: GameState):
    actions: list[ActionState] = list(state.friendly_pokemon.moves)
    for bench_index, pokemon in enumerate(state.friendly_bench):
        if pokemon.hp_percent > 0:
            actions.append(SwitchState(bench_index))
    return actions


def get_opponent_legal_actions(state: GameState):
    return list(state.opponent_pokemon.moves)


def is_anyone_dead(state: GameState):
    friendly_hp = state.friendly_pokemon.hp_percent
    opponent_hp = state.opponent_pokemon.hp_percent
    return friendly_hp <= 0 or opponent_hp <= 0


def simulate_switch(state: GameState, bench_index: int):
    bench = list(state.friendly_bench)
    new_active = bench[bench_index]
    bench[bench_index] = state.friendly_pokemon
    return replace(state, friendly_pokemon=new_active, friendly_bench=tuple(bench))


def simulate_attack(state: GameState, move: MoveState, player_attacking: bool):
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


def simulate_turn(state: GameState, friendly_action: ActionState, opponent_move: MoveState):
    if isinstance(friendly_action, SwitchState):
        switched_state = simulate_switch(state, friendly_action.bench_index)
        return apply_turn_ending(simulate_attack(switched_state, opponent_move, False))

    friendly_priority = friendly_action.priority
    opponent_priority = opponent_move.priority
    friendly_speed = modify_speed(state.friendly_pokemon.item, state.friendly_pokemon.spe)
    opponent_speed = modify_speed(state.opponent_pokemon.item, state.opponent_pokemon.spe)

    if friendly_priority != opponent_priority:
        orders = [(1.0, friendly_priority > opponent_priority)]
    elif friendly_speed != opponent_speed:
        orders = [(1.0, friendly_speed > opponent_speed)]
    else:
        orders = [(0.5, True), (0.5, False)]

    possibilities: list[tuple[float, GameState]] = []

    for probability, friendly_first in orders:
        if friendly_first:
            first_move = friendly_action
            second_move = opponent_move
        else:
            first_move = opponent_move
            second_move = friendly_action

        for first_probability, first_state in simulate_attack(state, first_move, friendly_first):
            if is_anyone_dead(first_state):
                possibilities.append((probability * first_probability, first_state))
                continue

            for second_probability, second_state in simulate_attack(first_state, second_move, not friendly_first):
                possibilities.append((probability * first_probability * second_probability, second_state))

    return apply_turn_ending(possibilities)


def apply_turn_ending(possibilities: list[tuple[float, GameState]]):
    return [(probability, _end_turn(next_state)) for probability, next_state in possibilities]


def _end_turn(state: GameState):
    friendly = state.friendly_pokemon
    opponent = state.opponent_pokemon
    return replace(
        state,
        friendly_pokemon=replace(friendly, hp_percent=end_of_turn_hp(friendly.item, friendly.hp_percent)),
        opponent_pokemon=replace(opponent, hp_percent=end_of_turn_hp(opponent.item, opponent.hp_percent)),
    )
