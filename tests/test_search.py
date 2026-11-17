from factories import make_move, make_pokemon

from agent.engine.search import get_best_action, get_state_value
from agent.engine.state import Action, GameState


def test_picks_ko_move_when_available():
    weak_move = make_move(id="weak", base_power=1)
    strong_move = make_move(id="strong", base_power=100)
    state = GameState(
        friendly_pokemon=make_pokemon(spe=300, moves=(weak_move, strong_move)),
        opponent_pokemon=make_pokemon(spe=100, hp_percent=0.1, moves=(make_move(),)),
        friendly_bench=(),
    )

    result = get_best_action(state, 1)
    values = dict(result.action_values)

    assert result.action == Action(is_switch=False, index=1)
    assert values[Action(is_switch=False, index=1)] > values[Action(is_switch=False, index=0)]


def test_returns_value_for_every_legal_action():
    state = GameState(
        friendly_pokemon=make_pokemon(moves=(make_move(), make_move(type="FIRE"))),
        opponent_pokemon=make_pokemon(moves=(make_move(),)),
        friendly_bench=(make_pokemon(), make_pokemon(hp_percent=0)),
    )

    result = get_best_action(state, 1)
    switches = [action for action, _value in result.action_values if action.is_switch]

    assert len(result.action_values) == 3
    assert switches == [Action(is_switch=True, index=0)]
    assert result.nodes_processed > 0


def test_state_value_counts_alive_bonus():
    equal = GameState(make_pokemon(), make_pokemon(), ())
    friendly_fainted = GameState(make_pokemon(hp_percent=0), make_pokemon(), ())
    opponent_fainted = GameState(make_pokemon(), make_pokemon(hp_percent=0), ())

    assert get_state_value(equal) == 0.0
    assert get_state_value(friendly_fainted) == -1.5
    assert get_state_value(opponent_fainted) == 1.5


def test_search_is_deterministic():
    move = make_move(accuracy=0.75)
    state = GameState(
        friendly_pokemon=make_pokemon(moves=(move, make_move(type="FIRE"))),
        opponent_pokemon=make_pokemon(moves=(move,)),
        friendly_bench=(make_pokemon(),),
    )

    first = get_best_action(state, 1)

    for _ in range(10):
        assert get_best_action(state, 1) == first
