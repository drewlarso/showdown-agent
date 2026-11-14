from collections.abc import Callable

from poke_env.battle import Battle, Move, Pokemon

from agent.state import Boosts, GameState, MoveState, PokeState

DEFAULT_IV = 31
DEFAULT_EV = 85

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

    return GameState(
        friendly_state,
        opponent_state,
        tuple(friendly_bench),
    )


def create_move_state(move: Move, probability: float):
    self_boosts = move.boosts if move.entry.get("target") == "self" else move.self_boost
    return MoveState(
        id=move.id,
        base_power=int(move.base_power * move.expected_hits),
        type=move.type.name,
        category=move.category.name,
        priority=move.entry.get("priority", 0),
        accuracy=move.accuracy,
        probability=probability,
        heal=move.heal,
        drain=move.drain,
        self_boosts=_create_boosts(self_boosts or {}),
    )


def _create_poke_state(pokemon: Pokemon, moves: list[MoveState]):
    return PokeState(
        species=pokemon.species,
        level=pokemon.level,
        hp_percent=pokemon.current_hp_fraction,
        max_hp=_get_max_hp(pokemon),
        atk=_get_raw_stat(pokemon, "atk"),
        defense=_get_raw_stat(pokemon, "def"),
        spa=_get_raw_stat(pokemon, "spa"),
        spd=_get_raw_stat(pokemon, "spd"),
        spe=_get_raw_stat(pokemon, "spe"),
        boosts=_create_boosts(pokemon.boosts),
        status=pokemon.status.name if pokemon.status else "",
        item=pokemon.item or "",
        types=tuple(t.name for t in pokemon.types),
        moves=tuple(moves),
    )


def _get_raw_stat(pokemon: Pokemon, name: str):
    return pokemon.stats.get(name) or calculate_stat(pokemon.base_stats[name], pokemon.level)


def _create_boosts(boosts: dict[str, int]):
    return Boosts(
        atk=boosts.get("atk", 0),
        defense=boosts.get("def", 0),
        spa=boosts.get("spa", 0),
        spd=boosts.get("spd", 0),
        spe=boosts.get("spe", 0),
    )


def calculate_hp(base_hp: int, level: int, ev: int = DEFAULT_EV, iv: int = DEFAULT_IV):
    if base_hp == 1:
        return 1
    return ((2 * base_hp + iv + (ev // 4)) * level) // 100 + level + 10


def calculate_stat(base_stat: int, level: int, ev: int = DEFAULT_EV, iv: int = DEFAULT_IV):
    return ((2 * base_stat + iv + (ev // 4)) * level) // 100 + 5


def _get_max_hp(pokemon: Pokemon):
    if pokemon.stats.get("atk"):  # true for friendly pokemon
        return pokemon.max_hp
    return calculate_hp(pokemon.base_stats["hp"], pokemon.level)


def _create_opponent_moves(opponent: Pokemon, probabilities: dict[str, float]):
    moves: list[MoveState] = []
    noop_probability = 0.0  # chance the simulator can't handle it

    for move_id, probability in probabilities.items():
        if probability <= 0:
            continue
        move = create_move_state(opponent.moves.get(move_id) or Move(move_id, gen=9), probability)
        if move.category == "STATUS" and not move.heal and move.self_boosts == Boosts():
            noop_probability += probability
        else:
            moves.append(move)

    if noop_probability > 0 or not moves:
        moves.append(MoveState("noop", 0, "NORMAL", "STATUS", 0, 1.0, noop_probability or 1.0))

    return moves
