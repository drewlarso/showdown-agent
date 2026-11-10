from dataclasses import dataclass

from poke_env.battle import Battle, Move, Pokemon


@dataclass(frozen=True)
class GameState:
    friendly_pokemon: PokeState
    opponent_pokemon: PokeState


@dataclass(frozen=True)
class PokeState:
    species: str
    hp_fraction: float
    stats: dict[str, int | None]
    types: list[str]
    moves: list[MoveState]


@dataclass(frozen=True)
class MoveState:
    id: str
    base_power: int
    type: str
    category: str
    priority: int
    accuracy: float


@dataclass(frozen=True)
class SwitchState:
    species: str
    priority: int = 6


ActionState = MoveState | SwitchState


def build_state(battle: Battle):
    if not battle.active_pokemon or not battle.opponent_active_pokemon:
        return None

    friendly_moves = []
    for move in battle.available_moves:
        friendly_moves.append(_create_move_state(move))
    opponent_moves = []
    for move in battle.opponent_active_pokemon.moves.values():
        opponent_moves.append(_create_move_state(move))

    friendly_state = _create_poke_state(battle.active_pokemon, friendly_moves)
    opponent_state = _create_poke_state(battle.opponent_active_pokemon, opponent_moves)

    return GameState(friendly_state, opponent_state)


def _create_move_state(move: Move):
    return MoveState(
        id=move.id,
        base_power=move.base_power,
        type=move.type.name,
        category=move.category.name,
        priority=move.priority,
        accuracy=move.accuracy,
    )


def _create_poke_state(pokemon: Pokemon, moves: list[MoveState]):
    types = [t.name for t in pokemon.types]
    return PokeState(
        species=pokemon.species,
        hp_fraction=pokemon.current_hp_fraction,
        stats=dict(pokemon.stats),
        types=types.copy(),
        moves=moves,
    )
