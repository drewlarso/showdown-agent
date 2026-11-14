from agent.items import modify_attack, modify_damage, modify_defense
from agent.state import MoveState, PokeState
from agent.type_chart import TYPE_CHART


def calculate_damage_percent(attacker: PokeState, defender: PokeState, move: MoveState, roll_multiplier: float = 0.925):
    if move.category == "STATUS":
        return 0.0

    type_multiplier = _get_type_multiplier(move.type, defender.types)
    if type_multiplier == 0:
        return 0.0

    fixed_damage = _get_fixed_damage_percent(attacker, defender, move)
    if fixed_damage is not None:
        return fixed_damage

    base_power = _get_base_power(attacker, defender, move)
    if not base_power:
        return 0.0

    if move.category == "PHYSICAL":
        attack, defense = get_boosted_stat(attacker, "atk"), get_boosted_stat(defender, "defense")
    else:
        attack, defense = get_boosted_stat(attacker, "spa"), get_boosted_stat(defender, "spd")

    attack = modify_attack(attacker.item, move.category, attack)
    defense = modify_defense(defender.item, move.category, defense)

    base = ((2 * attacker.level) // 5 + 2) * base_power * attack // max(defense, 1)
    base = base // 50 + 2

    stab = 1.5 if move.type in attacker.types else 1.0
    damage = int(base * roll_multiplier * stab * type_multiplier)
    damage = modify_damage(attacker.item, damage)

    return damage / defender.max_hp


def _get_base_power(attacker: PokeState, defender: PokeState, move: MoveState):
    match move.id:
        case "lowkick" | "grassknot" | "heavyslam" | "heatcrash":
            return 60  # depends on weight, use a typical value
        case "eruption" | "waterspout" | "dragonenergy":
            return max(1, int(move.base_power * attacker.hp_percent))
        case "hex" if defender.status:
            return move.base_power * 2
        case "acrobatics" if not attacker.item:
            return move.base_power * 2
        case _:
            return move.base_power


def get_boosted_stat(pokemon: PokeState, name: str):
    value = getattr(pokemon, name)
    boost = getattr(pokemon.boosts, name)

    if boost >= 0:
        value = value * (2 + boost) // 2
    else:
        value = value * 2 // (2 - boost)

    if name == "atk" and pokemon.status == "BRN":
        value //= 2
    if name == "spe" and pokemon.status == "PAR":
        value //= 2

    return value


def _get_type_multiplier(move_type: str, defender_types: tuple[str, ...]):
    multiplier = 1.0
    for defender_type in defender_types:
        multiplier *= TYPE_CHART.get(defender_type, {}).get(move_type, 1.0)
    return multiplier


def _get_fixed_damage_percent(attacker: PokeState, defender: PokeState, move: MoveState):
    match move.id:
        case "seismictoss" | "nightshade":
            return attacker.level / defender.max_hp
        case "superfang" | "ruination":
            return defender.hp_percent / 2
        case "endeavor":
            hp_difference = defender.hp_percent * defender.max_hp - attacker.hp_percent * attacker.max_hp
            return max(0.0, hp_difference) / defender.max_hp
