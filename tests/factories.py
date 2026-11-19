from agent.engine.state import Boosts, Category, Item, MoveState, PokemonState, Status, Type


def make_move(
    id: str = "tackle",
    base_power: int = 80,
    move_type: Type = Type.NORMAL,
    category: Category = Category.PHYSICAL,
    priority: int = 0,
    accuracy: float = 1.0,
    prior: float = 1.0,
    **kwargs,
) -> MoveState:
    return MoveState(
        id=id,
        base_power=base_power,
        move_type=move_type,
        category=category,
        priority=priority,
        accuracy=accuracy,
        prior=prior,
        **kwargs,
    )


def make_pokemon(
    types: tuple[Type, ...] = (Type.NORMAL,),
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
        "status": Status.NONE,
        "item": Item.NO_ITEM,
        "types": types,
        "moves": moves,
    }
    fields.update(kwargs)
    return PokemonState(**fields)
