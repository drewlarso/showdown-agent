from factories import make_move, make_pokemon
from pytest import approx

from agent.engine.simulate import get_friendly_first_chance, simulate_switch, simulate_turn
from agent.engine.state import Action, Boosts, GameState


def test_outcome_probabilities_add_to_one():
    move = make_move(accuracy=0.75)
    state = GameState(
        friendly_pokemon=make_pokemon(moves=(move,)),
        opponent_pokemon=make_pokemon(),
        friendly_bench=(),
    )

    outcomes = simulate_turn(state, Action(is_switch=False, index=0), move)
    probabilities = [probability for probability, _state in outcomes]

    assert sum(probabilities) == approx(1.0)
    assert len(outcomes) > 1
    assert all(probability > 0 for probability in probabilities)


def test_turn_order():
    low_priority = make_move()
    high_priority = make_move(priority=1)

    fast_vs_slow = GameState(make_pokemon(spe=300), make_pokemon(spe=100), ())
    slow_vs_fast = GameState(make_pokemon(spe=100), make_pokemon(spe=300), ())
    equal_speed = GameState(make_pokemon(spe=100), make_pokemon(spe=100), ())

    assert get_friendly_first_chance(fast_vs_slow, low_priority, low_priority) == 1.0
    assert get_friendly_first_chance(slow_vs_fast, low_priority, low_priority) == 0.0
    assert get_friendly_first_chance(slow_vs_fast, high_priority, low_priority) == 1.0
    assert get_friendly_first_chance(equal_speed, low_priority, low_priority) == 0.5


def test_ko_prevents_second_move():
    strong_move = make_move(base_power=999)
    state = GameState(
        friendly_pokemon=make_pokemon(spe=300, moves=(strong_move,)),
        opponent_pokemon=make_pokemon(spe=100),
        friendly_bench=(),
    )

    outcomes = simulate_turn(state, Action(is_switch=False, index=0), make_move())

    assert all(next_state.opponent_pokemon.hp_percent == 0 for _, next_state in outcomes)
    assert all(next_state.friendly_pokemon.hp_percent == 1.0 for _, next_state in outcomes)


def test_self_destruct_and_recoil():
    status_move = make_move(base_power=0, category="STATUS")
    explosion = make_move(id="explosion", base_power=999, self_destruct=True)
    brave_bird = make_move(id="bravebird", recoil=0.33)

    exploding = GameState(make_pokemon(spe=300, moves=(explosion,)), make_pokemon(spe=100), ())
    recoiling = GameState(make_pokemon(spe=300, moves=(brave_bird,)), make_pokemon(spe=100), ())
    nearly_fainted = GameState(make_pokemon(spe=300, hp_percent=0.01, moves=(brave_bird,)), make_pokemon(spe=100), ())

    use_move = Action(is_switch=False, index=0)
    exploded = simulate_turn(exploding, use_move, status_move)
    recoiled = simulate_turn(recoiling, use_move, status_move)
    recoil_fainted = simulate_turn(nearly_fainted, use_move, status_move)

    assert all(next_state.friendly_pokemon.hp_percent == 0 for _, next_state in exploded)
    assert all(next_state.friendly_pokemon.hp_percent < 1 for _, next_state in recoiled)
    assert all(next_state.friendly_pokemon.hp_percent == 0 for _, next_state in recoil_fainted)


def test_switch_swaps_active_and_resets_boosts():
    active = make_pokemon(types=("FIRE",), hp_percent=0.7, boosts=Boosts(atk=2))
    bench = make_pokemon(types=("WATER",))
    state = GameState(active, make_pokemon(), (bench,))

    switched = simulate_switch(state, 0)
    switched_out = switched.friendly_bench[0]

    assert switched.friendly_pokemon == bench
    assert switched_out.types == ("FIRE",)
    assert switched_out.boosts == Boosts()
    assert switched_out.hp_percent == 0.7
