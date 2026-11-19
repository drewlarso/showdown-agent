from agent.engine.state import Category, Item, MoveState, PokemonState, Status
from agent.engine.type_chart import get_type_multiplier


def get_damage_percent(
    attacker: PokemonState,
    defender: PokemonState,
    move: MoveState,
    roll_multiplier: float = 0.925,
) -> float:
    if move.category == Category.STATUS:
        return 0.0

    type_multiplier = 1.0
    for defender_type in defender.types:
        type_multiplier *= get_type_multiplier(defender_type, move.move_type)
    if type_multiplier == 0:
        return 0.0

    fixed_damage = get_fixed_damage_percent(attacker, defender, move)
    if fixed_damage is not None:
        return fixed_damage

    base_power = get_base_power(attacker, defender, move)
    if not base_power:
        return 0.0

    attack, defense = get_attack_and_defense(attacker, defender, move.category)
    base = ((2 * attacker.level) // 5 + 2) * base_power * attack // max(defense, 1)
    base = base // 50 + 2

    stab = 1.5 if move.move_type in attacker.types else 1.0
    damage = int(base * roll_multiplier * stab * type_multiplier)
    if attacker.item == Item.LIFE_ORB:
        damage = damage * 13 // 10

    return damage / defender.max_hp


def get_speed(pokemon: PokemonState) -> int:
    speed = get_boosted_stat(pokemon.spe, pokemon.boosts.spe)
    if pokemon.status == Status.PAR:
        speed //= 2
    if pokemon.item == Item.CHOICE_SCARF:
        speed = speed * 3 // 2
    return speed


def get_end_of_turn_hp(item: Item, hp_percent: float) -> float:
    if item == Item.LEFTOVERS and hp_percent > 0:
        return min(1.0, hp_percent + 1 / 16)
    return hp_percent


def get_attack_and_defense(attacker: PokemonState, defender: PokemonState, category: Category) -> tuple[int, int]:
    if category == Category.PHYSICAL:
        attack = get_boosted_stat(attacker.atk, attacker.boosts.atk)
        defense = get_boosted_stat(defender.defense, defender.boosts.defense)

        if attacker.status == Status.BRN:
            attack //= 2
        if attacker.item == Item.CHOICE_BAND:
            attack = attack * 3 // 2
    else:
        attack = get_boosted_stat(attacker.spa, attacker.boosts.spa)
        defense = get_boosted_stat(defender.spd, defender.boosts.spd)

        if category == Category.SPECIAL and attacker.item == Item.CHOICE_SPECS:
            attack = attack * 3 // 2

    if defender.item == Item.EVIOLITE or (category == Category.SPECIAL and defender.item == Item.ASSAULT_VEST):
        defense = defense * 3 // 2

    return attack, defense


def get_boosted_stat(value: int, boost: int) -> int:
    if boost >= 0:
        return value * (2 + boost) // 2
    return value * 2 // (2 - boost)


def get_base_power(attacker: PokemonState, defender: PokemonState, move: MoveState) -> int:
    match move.id:
        case "lowkick" | "grassknot" | "heavyslam" | "heatcrash":
            return 60  # just a guess
        case "eruption" | "waterspout" | "dragonenergy":
            return max(1, int(move.base_power * attacker.hp_percent))
        case "hex" if defender.status != Status.NONE:
            return move.base_power * 2
        case "acrobatics" if attacker.item == Item.NO_ITEM:
            return move.base_power * 2
        case _:
            return move.base_power


def get_fixed_damage_percent(attacker: PokemonState, defender: PokemonState, move: MoveState) -> float | None:
    match move.id:
        case "seismictoss" | "nightshade":
            return attacker.level / defender.max_hp
        case "superfang" | "ruination":
            return defender.hp_percent / 2
        case "endeavor":
            hp_difference = defender.hp_percent * defender.max_hp - attacker.hp_percent * attacker.max_hp
            return max(0.0, hp_difference) / defender.max_hp
        case _:
            return None
