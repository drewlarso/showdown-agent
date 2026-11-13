from dataclasses import dataclass

from poke_env.battle import Battle, Move, Pokemon


@dataclass(frozen=True)
class GameState:
    friendly_pokemon: PokeState
    opponent_pokemon: PokeState
    friendly_bench: dict[str, PokeState]
    opponent_bench: dict[str, PokeState]


@dataclass(frozen=True)
class PokeState:
    species: str
    level: int
    hp_percent: float
    stats: dict[str, int | None]
    base_stats: dict[str, int]
    types: list[str]
    boosts: dict[str, int]
    moves: list[MoveState]


@dataclass(frozen=True)
class MoveState:
    id: str
    base_power: int
    type: str
    category: str
    priority: int
    accuracy: float
    probability: float


@dataclass(frozen=True)
class SwitchState:
    species: str
    priority: int = 6


ActionState = MoveState | SwitchState


def build_state(battle: Battle, use_role_weights: bool = True):
    if not battle.active_pokemon or not battle.opponent_active_pokemon:
        return None

    friendly_moves = []
    for move in battle.available_moves:
        friendly_moves.append(create_move_state(move, probability=1))
    opponent_moves = []
    for move in battle.opponent_active_pokemon.moves.values():
        opponent_moves.append(create_move_state(move, probability=1))

    friendly_state = _create_poke_state(battle.active_pokemon, friendly_moves)
    opponent_state = _create_poke_state(battle.opponent_active_pokemon, opponent_moves)

    friendly_bench = {}
    opponent_bench = {}

    for key, pokemon in battle.team.items():
        poke_state = _create_poke_state(pokemon, [])
        friendly_bench[key] = poke_state

    for key, pokemon in battle.opponent_team.items():
        poke_state = _create_poke_state(pokemon, [])
        opponent_bench[key] = poke_state

    return GameState(friendly_state, opponent_state, friendly_bench, opponent_bench)


def create_move_state(move: Move, probability: float):
    return MoveState(
        id=move.id,
        base_power=move.base_power,
        type=move.type.name,
        category=move.category.name,
        priority=move.priority,
        accuracy=move.accuracy,
        probability=probability,
    )


def _create_poke_state(pokemon: Pokemon, moves: list[MoveState]):
    types = [t.name for t in pokemon.types]
    return PokeState(
        species=pokemon.species,
        level=pokemon.level,
        hp_percent=pokemon.current_hp_fraction,
        stats=pokemon.stats.copy(),
        base_stats=pokemon.base_stats.copy(),
        types=types.copy(),
        boosts={},
        moves=moves,
    )
