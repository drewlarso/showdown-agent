from poke_env.battle import Move, MoveCategory, Pokemon

DEFAULT_IV = 31
DEFAULT_EV = 85
EV_BONUS = DEFAULT_EV // 4


def calculate_hp(base_hp: int, level: int):
    if base_hp == 1:
        return 1
    return (((2 * base_hp + DEFAULT_IV + EV_BONUS) * level) // 100) + level + 10


def calculate_stat(base_stat: int, level: int, nature_modifier: float = 1.0):
    raw_stat = (((2 * base_stat + DEFAULT_IV + EV_BONUS) * level) // 100) + 5
    return int(raw_stat * nature_modifier)


def get_stat(pokemon: Pokemon, stat: str):
    value = pokemon.stats.get(stat)
    if value:
        return value
    return calculate_stat(pokemon.base_stats[stat], pokemon.level)


def boost_multiplier(stage: int):
    return (2 + stage) / 2 if stage >= 0 else 2 / (2 - stage)


def calculate_move_damage(attacker: Pokemon, defender: Pokemon, move: Move, roll_multiplier: float):
    if move.category == MoveCategory.STATUS or not move.base_power:
        return 0

    type_multiplier = defender.damage_multiplier(move.type)
    if type_multiplier == 0.0:
        return 0

    if move.category == MoveCategory.PHYSICAL:
        attack_key, defense_key = "atk", "def"
    else:
        attack_key, defense_key = "spa", "spd"

    attack = int(get_stat(attacker, attack_key) * boost_multiplier(attacker.boosts.get(attack_key, 0)))
    defense = int(get_stat(defender, defense_key) * boost_multiplier(defender.boosts.get(defense_key, 0)))
    defense = max(defense, 1)

    base = ((2 * attacker.level) // 5 + 2) * move.base_power * attack // defense
    base = base // 50 + 2

    stab = 1.5 if move.type in attacker.types else 1.0

    return int(base * roll_multiplier * stab * type_multiplier)


def damage_fraction(attacker: Pokemon, defender: Pokemon, move: Move, roll_multiplier: float):
    damage = calculate_move_damage(attacker, defender, move, roll_multiplier)
    max_hp = calculate_hp(defender.base_stats["hp"], defender.level)
    return damage / max_hp
