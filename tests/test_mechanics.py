from factories import make_move, make_pokemon

from agent.engine.mechanics import get_damage_percent, get_speed
from agent.engine.state import Boosts


def test_type_effectiveness_changes_damage():
    attacker = make_pokemon()
    move = make_move(type="FIRE", category="SPECIAL")

    grass = get_damage_percent(attacker, make_pokemon(types=("GRASS",)), move)
    normal = get_damage_percent(attacker, make_pokemon(types=("NORMAL",)), move)
    water = get_damage_percent(attacker, make_pokemon(types=("WATER",)), move)
    grass_bug = get_damage_percent(attacker, make_pokemon(types=("GRASS", "BUG")), move)

    assert grass > normal > water
    assert grass_bug > grass


def test_zero_damage_cases():
    attacker = make_pokemon()
    defender = make_pokemon()

    immune = get_damage_percent(attacker, make_pokemon(types=("FLYING",)), make_move(type="GROUND"))
    status = get_damage_percent(attacker, defender, make_move(category="STATUS"))
    no_base_power = get_damage_percent(attacker, defender, make_move(base_power=0))

    assert immune == 0
    assert status == 0
    assert no_base_power == 0


def test_stab_increases_damage():
    defender = make_pokemon()
    move = make_move(type="FIRE")

    fire = get_damage_percent(make_pokemon(types=("FIRE",)), defender, move)
    water = get_damage_percent(make_pokemon(types=("WATER",)), defender, move)

    assert fire > water


def test_fixed_damage_ignores_stats():
    attacker_level = 100
    defender_max_hp = 300

    defender = make_pokemon(max_hp=defender_max_hp)
    move = make_move(id="seismictoss")

    low_attack = get_damage_percent(make_pokemon(level=attacker_level, atk=0), defender, move)
    high_attack = get_damage_percent(make_pokemon(level=attacker_level, atk=999), defender, move)

    assert low_attack == high_attack == attacker_level / defender_max_hp


def test_speed_modifiers():
    boost = get_speed(make_pokemon(boosts=Boosts(spe=2)))
    choice_scarf = get_speed(make_pokemon(item="choicescarf"))
    default = get_speed(make_pokemon())
    paralyzed = get_speed(make_pokemon(status="PAR"))

    assert boost > choice_scarf > default > paralyzed
