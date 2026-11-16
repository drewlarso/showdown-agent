import json
from dataclasses import dataclass
from typing import Any


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
    prior: float
    heal: float = 0.0
    drain: float = 0.0
    self_boosts: Boosts = Boosts()


@dataclass(frozen=True)
class PokemonState:
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
class GameState:
    friendly_pokemon: PokemonState
    opponent_pokemon: PokemonState
    friendly_bench: tuple[PokemonState, ...]


@dataclass(frozen=True)
class Action:
    is_switch: bool
    index: int


def load_game_state(state_json: str) -> GameState:
    data = json.loads(state_json)
    return GameState(
        friendly_pokemon=load_pokemon_state(data["friendly_pokemon"]),
        opponent_pokemon=load_pokemon_state(data["opponent_pokemon"]),
        friendly_bench=tuple(load_pokemon_state(pokemon) for pokemon in data["friendly_bench"]),
    )


def load_pokemon_state(data: dict[str, Any]) -> PokemonState:
    fields = data.copy()
    fields["boosts"] = Boosts(**data["boosts"])
    fields["types"] = tuple(data["types"])
    fields["moves"] = tuple(load_move_state(move) for move in data["moves"])
    return PokemonState(**fields)


def load_move_state(data: dict[str, Any]) -> MoveState:
    fields = data.copy()
    fields["self_boosts"] = Boosts(**data["self_boosts"])
    return MoveState(**fields)
