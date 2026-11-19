import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from agent.engine.type_chart import Type


class Category(StrEnum):
    PHYSICAL = "PHYSICAL"
    SPECIAL = "SPECIAL"
    STATUS = "STATUS"


class Status(StrEnum):
    NONE = ""
    BRN = "BRN"
    FNT = "FNT"
    FRZ = "FRZ"
    PAR = "PAR"
    PSN = "PSN"
    SLP = "SLP"
    TOX = "TOX"


class Item(StrEnum):
    NO_ITEM = ""
    CHOICE_BAND = "choiceband"
    CHOICE_SCARF = "choicescarf"
    CHOICE_SPECS = "choicespecs"
    ASSAULT_VEST = "assaultvest"
    EVIOLITE = "eviolite"
    LEFTOVERS = "leftovers"
    LIFE_ORB = "lifeorb"
    OTHER = "other"

    @classmethod
    def _missing_(cls, value: object) -> Item:
        return cls.OTHER


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
    move_type: Type
    category: Category
    priority: int
    accuracy: float
    prior: float
    heal: float = 0.0
    drain: float = 0.0
    recoil: float = 0.0
    self_destruct: bool = False
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
    status: Status
    item: Item
    types: tuple[Type, ...]
    moves: tuple[MoveState, ...]
    locked_move: int | None = None


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
    state = GameState(
        friendly_pokemon=load_pokemon_state(data["friendly_pokemon"]),
        opponent_pokemon=load_pokemon_state(data["opponent_pokemon"]),
        friendly_bench=tuple(load_pokemon_state(pokemon) for pokemon in data["friendly_bench"]),
    )
    opponent_moves = state.opponent_pokemon.moves
    if not opponent_moves or any(move.prior <= 0 for move in opponent_moves):
        raise ValueError("opponent needs at least one move and all priors must be positive")
    return state


def dump_game_state(state: GameState) -> str:
    return json.dumps(asdict(state))


def load_pokemon_state(data: dict[str, Any]) -> PokemonState:
    fields = data.copy()
    fields["boosts"] = Boosts(**data["boosts"])
    fields["status"] = Status(data["status"])
    fields["item"] = Item(data["item"])
    fields["types"] = tuple(Type(pokemon_type) for pokemon_type in data["types"])
    fields["moves"] = tuple(load_move_state(move) for move in data["moves"])
    return PokemonState(**fields)


def load_move_state(data: dict[str, Any]) -> MoveState:
    fields = data.copy()
    fields["move_type"] = Type(data["move_type"])
    fields["category"] = Category(data["category"])
    fields["self_boosts"] = Boosts(**data["self_boosts"])
    return MoveState(**fields)
