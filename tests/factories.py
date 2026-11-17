from agent.engine.state import Boosts, MoveState, PokemonState


def make_move(
    id: str = "tackle",
    base_power: int = 80,
    type: str = "NORMAL",
    category: str = "PHYSICAL",
    priority: int = 0,
    accuracy: float = 1.0,
    prior: float = 1.0,
    **kwargs,
) -> MoveState:
    return MoveState(
        id=id,
        base_power=base_power,
        type=type,
        category=category,
        priority=priority,
        accuracy=accuracy,
        prior=prior,
        **kwargs,
    )


def make_pokemon(
    types: tuple[str, ...] = ("NORMAL",),
    moves: tuple[MoveState, ...] = (),
    hp_percent: float = 1.0,
    spe: int = 200,
    **kwargs,
) -> PokemonState:
    fields = {
        "level": 80,
        "hp_percent": hp_percent,
        "max_hp": 250,
        "atk": 200,
        "defense": 200,
        "spa": 200,
        "spd": 200,
        "spe": spe,
        "boosts": Boosts(),
        "status": "",
        "item": "",
        "types": types,
        "moves": moves,
    }
    fields.update(kwargs)
    return PokemonState(**fields)
