from collections.abc import Callable

from poke_env.battle import Battle, Move, Pokemon

from agent.engine.state import Boosts, GameState, MoveState, PokemonState

DEFAULT_IV = 31
DEFAULT_EV = 85

type GetOpponentMovePriors = Callable[[Pokemon], dict[str, float]]


def build_state(battle: Battle, get_opponent_move_priors: GetOpponentMovePriors) -> GameState | None:
    friendly_pokemon = battle.active_pokemon
    opponent_pokemon = battle.opponent_active_pokemon
    if not friendly_pokemon or not opponent_pokemon:
        return None

    friendly_moves = tuple(build_move(move) for move in battle.available_moves)
    opponent_moves = build_opponent_moves(opponent_pokemon, get_opponent_move_priors(opponent_pokemon))

    friendly_bench = []
    for pokemon in battle.available_switches:
        move_states = tuple(build_move(move) for move in pokemon.moves.values())
        friendly_bench.append(build_pokemon(pokemon, move_states))

    return GameState(
        friendly_pokemon=build_pokemon(friendly_pokemon, friendly_moves),
        opponent_pokemon=build_pokemon(opponent_pokemon, opponent_moves),
        friendly_bench=tuple(friendly_bench),
    )


def build_pokemon(pokemon: Pokemon, move_states: tuple[MoveState, ...]) -> PokemonState:
    if pokemon.stats.get("atk"):  # true for friendly pokemon
        max_hp = pokemon.max_hp
    else:
        max_hp = calculate_stat(pokemon.base_stats["hp"], pokemon.level, is_hp=True)

    return PokemonState(
        level=pokemon.level,
        hp_percent=pokemon.current_hp_fraction,
        max_hp=max_hp,
        atk=get_raw_stat(pokemon, "atk"),
        defense=get_raw_stat(pokemon, "def"),
        spa=get_raw_stat(pokemon, "spa"),
        spd=get_raw_stat(pokemon, "spd"),
        spe=get_raw_stat(pokemon, "spe"),
        boosts=build_boosts(pokemon.boosts),
        status=pokemon.status.name if pokemon.status else "",
        item=pokemon.item or "",
        types=tuple(pokemon_type.name for pokemon_type in pokemon.types),
        moves=move_states,
    )


def build_move(move: Move, prior: float = 1.0) -> MoveState:
    self_boosts = move.boosts if move.entry.get("target") == "self" else move.self_boost
    return MoveState(
        id=move.id,
        base_power=int(move.base_power * move.expected_hits),
        type=move.type.name,
        category=move.category.name,
        priority=move.entry.get("priority", 0),
        accuracy=move.accuracy,
        prior=prior,
        heal=move.heal,
        drain=move.drain,
        self_boosts=build_boosts(self_boosts or {}),
    )


def build_opponent_moves(opponent_pokemon: Pokemon, move_priors: dict[str, float]) -> tuple[MoveState, ...]:
    move_states: list[MoveState] = []
    noop_prior = 0.0

    for move_id, prior in move_priors.items():
        if prior <= 0:
            continue

        move = opponent_pokemon.moves.get(move_id) or Move(move_id, gen=9)
        move_state = build_move(move, prior)
        if move_state.category == "STATUS" and not move_state.heal and move_state.self_boosts == Boosts():
            noop_prior += prior
        else:
            move_states.append(move_state)

    if noop_prior > 0 or not move_states:
        move_states.append(MoveState("noop", 0, "NORMAL", "STATUS", 0, 1.0, prior=noop_prior or 1.0))

    return tuple(move_states)


def get_raw_stat(pokemon: Pokemon, stat: str) -> int:
    return pokemon.stats.get(stat) or calculate_stat(pokemon.base_stats[stat], pokemon.level)


def calculate_stat(
    base_stat: int,
    level: int,
    ev: int = DEFAULT_EV,
    iv: int = DEFAULT_IV,
    *,
    is_hp: bool = False,
) -> int:
    if is_hp and base_stat == 1:
        return 1

    scaled_stat = ((2 * base_stat + iv + ev // 4) * level) // 100
    return scaled_stat + (level + 10 if is_hp else 5)


def build_boosts(boosts: dict[str, int]) -> Boosts:
    return Boosts(
        atk=boosts.get("atk", 0),
        defense=boosts.get("def", 0),
        spa=boosts.get("spa", 0),
        spd=boosts.get("spd", 0),
        spe=boosts.get("spe", 0),
    )
