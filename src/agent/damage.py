from agent.items import modify_attack, modify_damage, modify_defense
from agent.state import MoveState, PokeState
from agent.type_chart import TYPE_CHART


def calculate_damage_percent(attacker: PokeState, defender: PokeState, move: MoveState, roll_multiplier: float = 0.925):
    if move.category == "STATUS" or not move.base_power:
        return 0.0

    type_multiplier = _get_type_multiplier(move.type, defender.types)

    if move.category == "PHYSICAL":
        attack, defense = attacker.atk, defender.defense
    else:
        attack, defense = attacker.spa, defender.spd

    attack = modify_attack(attacker.item, move.category, attack)
    defense = modify_defense(defender.item, move.category, defense)

    base = ((2 * attacker.level) // 5 + 2) * move.base_power * attack // max(defense, 1)
    base = base // 50 + 2

    stab = 1.5 if move.type in attacker.types else 1.0
    damage = int(base * roll_multiplier * stab * type_multiplier)
    damage = modify_damage(attacker.item, damage)

    return damage / defender.max_hp


def _get_type_multiplier(move_type: str, defender_types: tuple[str, ...]):
    multiplier = 1.0
    for defender_type in defender_types:
        multiplier *= TYPE_CHART.get(defender_type, {}).get(move_type, 1.0)
    return multiplier
