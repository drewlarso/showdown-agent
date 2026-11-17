from dataclasses import replace

from agent.engine.mechanics import get_damage_percent, get_end_of_turn_hp, get_speed
from agent.engine.state import Action, Boosts, GameState, MoveState, PokemonState


def simulate_turn(
    state: GameState,
    friendly_action: Action,
    opponent_move: MoveState,
) -> list[tuple[float, GameState]]:
    if friendly_action.is_switch:
        switched_state = simulate_switch(state, friendly_action.index)
        return [
            (probability, end_turn(next_state))
            for probability, next_state in simulate_move(switched_state, opponent_move, friendly_attacking=False)
        ]

    friendly_move = state.friendly_pokemon.moves[friendly_action.index]
    friendly_first_chance = get_friendly_first_chance(state, friendly_move, opponent_move)
    outcomes: list[tuple[float, GameState]] = []

    for order_probability, friendly_first in ((friendly_first_chance, True), (1 - friendly_first_chance, False)):
        if order_probability == 0:
            continue

        if friendly_first:
            first_move, second_move = friendly_move, opponent_move
        else:
            first_move, second_move = opponent_move, friendly_move

        for first_probability, first_state in simulate_move(state, first_move, friendly_first):
            branch_probability = order_probability * first_probability
            if has_anyone_fainted(first_state):
                outcomes.append((branch_probability, first_state))
                continue

            for second_probability, second_state in simulate_move(first_state, second_move, not friendly_first):
                outcomes.append((branch_probability * second_probability, second_state))

    return [(probability, end_turn(next_state)) for probability, next_state in outcomes]


def get_friendly_actions(state: GameState) -> list[Action]:
    actions = [Action(is_switch=False, index=index) for index in range(len(state.friendly_pokemon.moves))]
    for bench_index, pokemon_state in enumerate(state.friendly_bench):
        if pokemon_state.hp_percent > 0:
            actions.append(Action(is_switch=True, index=bench_index))
    return actions


def has_anyone_fainted(state: GameState) -> bool:
    return state.friendly_pokemon.hp_percent <= 0 or state.opponent_pokemon.hp_percent <= 0


def simulate_switch(state: GameState, bench_index: int) -> GameState:
    bench = list(state.friendly_bench)
    new_active = bench[bench_index]
    bench[bench_index] = replace(state.friendly_pokemon, boosts=Boosts())
    return replace(state, friendly_pokemon=new_active, friendly_bench=tuple(bench))


def get_friendly_first_chance(state: GameState, friendly_move: MoveState, opponent_move: MoveState) -> float:
    if friendly_move.priority != opponent_move.priority:
        return 1.0 if friendly_move.priority > opponent_move.priority else 0.0

    friendly_speed = get_speed(state.friendly_pokemon)
    opponent_speed = get_speed(state.opponent_pokemon)
    if friendly_speed != opponent_speed:
        return 1.0 if friendly_speed > opponent_speed else 0.0
    return 0.5


def simulate_move(state: GameState, move: MoveState, friendly_attacking: bool) -> list[tuple[float, GameState]]:
    possibilities: list[tuple[float, GameState]] = []

    if friendly_attacking:
        attacker = state.friendly_pokemon
        defender = state.opponent_pokemon
    else:
        attacker = state.opponent_pokemon
        defender = state.friendly_pokemon

    if attacker.item.startswith("choice"):
        attacker = replace(attacker, moves=(move,))

    if move.accuracy < 1.0:
        possibilities.append((1 - move.accuracy, replace_active_pokemon(state, attacker, defender, friendly_attacking)))

    damage_percent = get_damage_percent(attacker, defender, move)
    damage_dealt = min(damage_percent, defender.hp_percent)
    damaged_defender = replace(defender, hp_percent=defender.hp_percent - damage_dealt)

    damage_hp = damage_dealt * defender.max_hp
    hp_change = move.heal + (move.drain - move.recoil) * damage_hp / attacker.max_hp
    attacker_hp = 0.0 if move.self_destruct else max(0.0, min(1.0, attacker.hp_percent + hp_change))

    new_attacker = replace(
        attacker,
        hp_percent=attacker_hp,
        boosts=add_boosts(attacker.boosts, move.self_boosts),
    )

    new_state = replace_active_pokemon(state, new_attacker, damaged_defender, friendly_attacking)
    possibilities.append((move.accuracy, new_state))

    return possibilities


def replace_active_pokemon(
    state: GameState,
    attacker: PokemonState,
    defender: PokemonState,
    friendly_attacking: bool,
) -> GameState:
    if friendly_attacking:
        return replace(state, friendly_pokemon=attacker, opponent_pokemon=defender)
    return replace(state, friendly_pokemon=defender, opponent_pokemon=attacker)


def add_boosts(boosts: Boosts, change: Boosts) -> Boosts:
    return Boosts(
        atk=clamp_boost(boosts.atk + change.atk),
        defense=clamp_boost(boosts.defense + change.defense),
        spa=clamp_boost(boosts.spa + change.spa),
        spd=clamp_boost(boosts.spd + change.spd),
        spe=clamp_boost(boosts.spe + change.spe),
    )


def clamp_boost(boost: int) -> int:
    return max(-6, min(6, boost))


def end_turn(state: GameState) -> GameState:
    friendly = state.friendly_pokemon
    opponent = state.opponent_pokemon
    return replace(
        state,
        friendly_pokemon=replace(friendly, hp_percent=get_end_of_turn_hp(friendly.item, friendly.hp_percent)),
        opponent_pokemon=replace(opponent, hp_percent=get_end_of_turn_hp(opponent.item, opponent.hp_percent)),
    )
