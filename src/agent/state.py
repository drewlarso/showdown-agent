from dataclasses import dataclass


@dataclass(frozen=True)
class GameState:
    friendly_pokemon: PokeState
    opponent_pokemon: PokeState
    friendly_bench: tuple[PokeState, ...]


@dataclass(frozen=True)
class PokeState:
    species: str
    level: int
    hp_percent: float
    max_hp: int
    atk: int
    defense: int
    spa: int
    spd: int
    spe: int
    boosts: Boosts
    status: str
    item: str
    types: tuple[str, ...]
    moves: tuple[MoveState, ...]


@dataclass(frozen=True)
class Boosts:
    atk: int = 0
    defense: int = 0
    spa: int = 0
    spd: int = 0
    spe: int = 0


@dataclass(frozen=True)
class MoveState:
    id: str
    base_power: int
    type: str
    category: str
    priority: int
    accuracy: float
    probability: float
    heal: float = 0.0
    drain: float = 0.0
    self_boosts: Boosts = Boosts()


@dataclass(frozen=True)
class SwitchState:
    bench_index: int


ActionState = MoveState | SwitchState
