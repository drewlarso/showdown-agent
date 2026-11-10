from poke_env.battle import PokemonType
from poke_env.data import GenData

from agent.state import MoveState, PokeState

GEN_DATA = GenData(9)
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


def get_stat(pokemon: PokeState, stat: str):
    value = pokemon.stats.get(stat)
    if value:
        return value
    return calculate_stat(pokemon.base_stats[stat], pokemon.level)


def calculate_damage_amount(attacker: PokeState, defender: PokeState, move: MoveState, roll_multiplier: float):
    if move.category == "STATUS" or not move.base_power:
        return 0

    types = [PokemonType[t] for t in defender.types]
    type_multiplier = PokemonType[move.type].damage_multiplier(*types, type_chart=GEN_DATA.type_chart)
    if type_multiplier == 0.0:
        return 0

    if move.category == "PHYSICAL":
        attack_key, defense_key = "atk", "def"
    else:
        attack_key, defense_key = "spa", "spd"

    attack = get_stat(attacker, attack_key)
    defense = get_stat(defender, defense_key)
    defense = max(defense, 1)

    base = ((2 * attacker.level) // 5 + 2) * move.base_power * attack // defense
    base = base // 50 + 2

    stab = 1.5 if move.type in attacker.types else 1.0

    return int(base * roll_multiplier * stab * type_multiplier)


def calculate_damage_percent(attacker: PokeState, defender: PokeState, move: MoveState, roll_multiplier: float):
    damage = calculate_damage_amount(attacker, defender, move, roll_multiplier)
    max_hp = calculate_hp(defender.base_stats["hp"], defender.level)
    return damage / max_hp
