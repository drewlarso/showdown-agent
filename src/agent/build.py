from collections.abc import Callable
from dataclasses import replace

from poke_env.battle import Battle, Move, Pokemon, Status

from agent.damage import calculate_damage_percent
from agent.state import GameState, MoveState, PokeState

DEFAULT_IV = 31
DEFAULT_EV = 85
DAMAGE_FLOOR = 0.05

type GetOpponentMoves = Callable[[Pokemon], dict[str, float]]


def build_state(battle: Battle, get_opponent_moves: GetOpponentMoves):
    active = battle.active_pokemon
    opponent = battle.opponent_active_pokemon
    if not active or not opponent:
        return None

    friendly_moves = [create_move_state(move, probability=1.0) for move in battle.available_moves]
    opponent_moves = _create_opponent_moves(opponent, get_opponent_moves(opponent))

    friendly_bench = []
    for pokemon in battle.available_switches:
        moves = [create_move_state(move, probability=1.0) for move in pokemon.moves.values()]
        friendly_bench.append(_create_poke_state(pokemon, moves))

    friendly_state = _create_poke_state(active, friendly_moves)
    opponent_state = _create_poke_state(opponent, opponent_moves)
    opponent_state = _weight_by_damage(friendly_state, opponent_state)

    return GameState(
        friendly_state,
        opponent_state,
        tuple(friendly_bench),
    )


def create_move_state(move: Move, probability: float):
    return MoveState(
        id=move.id,
        base_power=int(move.base_power * move.expected_hits),
        type=move.type.name,
        category=move.category.name,
        priority=move.entry.get("priority", 0),
        accuracy=move.accuracy,
        probability=probability,
    )


def _create_poke_state(pokemon: Pokemon, moves: list[MoveState]):
    return PokeState(
        species=pokemon.species,
        level=pokemon.level,
        hp_percent=pokemon.current_hp_fraction,
        max_hp=_get_max_hp(pokemon),
        atk=get_stat(pokemon, "atk"),
        defense=get_stat(pokemon, "def"),
        spa=get_stat(pokemon, "spa"),
        spd=get_stat(pokemon, "spd"),
        spe=get_stat(pokemon, "spe"),
        item=pokemon.item or "",
        types=tuple(t.name for t in pokemon.types),
        moves=tuple(moves),
    )


def calculate_hp(base_hp: int, level: int, ev: int = DEFAULT_EV, iv: int = DEFAULT_IV):
    if base_hp == 1:
        return 1
    return ((2 * base_hp + iv + (ev // 4)) * level) // 100 + level + 10


def calculate_stat(base_stat: int, level: int, ev: int = DEFAULT_EV, iv: int = DEFAULT_IV):
    return ((2 * base_stat + iv + (ev // 4)) * level) // 100 + 5


def get_stat(pokemon: Pokemon, name: str):
    value = pokemon.stats.get(name) or calculate_stat(pokemon.base_stats[name], pokemon.level)

    boost = pokemon.boosts.get(name, 0)
    if boost >= 0:
        value = value * (2 + boost) // 2
    else:
        value = value * 2 // (2 - boost)

    if name == "atk" and pokemon.status == Status.BRN:  # burn
        value //= 2
    if name == "spe" and pokemon.status == Status.PAR:  # paralysis
        value //= 2

    return value


def _get_max_hp(pokemon: Pokemon):
    if pokemon.stats.get("atk"):  # true for friendly pokemon
        return pokemon.max_hp
    return calculate_hp(pokemon.base_stats["hp"], pokemon.level)


def _weight_by_damage(friendly: PokeState, opponent: PokeState):
    moves = []
    for move in opponent.moves:
        damage = calculate_damage_percent(opponent, friendly, move)
        moves.append(replace(move, probability=move.probability * (damage + DAMAGE_FLOOR)))
    return replace(opponent, moves=tuple(moves))


def _is_simulated(move: Move):
    # eventually might look like:
    #   move.base_power > 0 or move.heal > 0
    return move.base_power > 0


def _create_opponent_moves(opponent: Pokemon, probabilities: dict[str, float]):
    moves: list[MoveState] = []
    noop_probability = 0.0  # chance the simulator can't handle it

    for move_id, probability in probabilities.items():
        move = opponent.moves.get(move_id) or Move(move_id, gen=9)
        if _is_simulated(move):
            moves.append(create_move_state(move, probability))
        else:
            noop_probability += probability

    if noop_probability > 0 or not moves:
        moves.append(MoveState("noop", 0, "NORMAL", "STATUS", 0, 1.0, noop_probability or 1.0))

    return moves
