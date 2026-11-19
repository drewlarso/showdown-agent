from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter

from poke_env.battle import AbstractBattle, Battle, Move, Pokemon
from poke_env.player import BattleOrder, Player, SingleBattleOrder

from agent.build import GetOpponentMovePriors, build_state
from agent.engine.search import SearchResult
from agent.engine.state import dump_game_state

type SearchFunction = Callable[[str, int], SearchResult]


@dataclass(frozen=True)
class ActionValue:
    kind: str
    name: str
    value: float


@dataclass(frozen=True)
class ResultsLog:
    battle_id: str
    turn: int
    forced_switch: bool
    active: str | None
    active_hp: float | None
    opponent: str | None
    opponent_hp: float | None
    played_action_type: str
    played_action_name: str
    decision_ms: float
    search_ms: float | None
    nodes_processed: int | None
    fallback_reason: str | None
    action_values: list[ActionValue] | None


class ExpectimaxPlayer(Player):
    def __init__(
        self,
        *,
        depth: int,
        get_opponent_move_priors: GetOpponentMovePriors,
        search: SearchFunction,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.depth = depth
        self.get_opponent_move_priors = get_opponent_move_priors
        self.search = search
        self.results: list[ResultsLog] = []

    def choose_move(self, battle: AbstractBattle):
        assert isinstance(battle, Battle)

        decision_start = perf_counter()
        result = None
        search_ms = None

        state = build_state(battle, self.get_opponent_move_priors)
        if state is None:
            order = self.choose_random_move(battle)
            self.results.append(
                self.build_result_log(
                    battle,
                    order,
                    decision_start,
                    fallback_reason="state_unavailable",
                )
            )
            return order

        state_json = dump_game_state(state)

        search_start = perf_counter()
        try:
            result = self.search(state_json, self.depth)
        except Exception as error:  # noqa: BLE001
            order = self.choose_random_move(battle)
            self.results.append(
                self.build_result_log(
                    battle,
                    order,
                    decision_start,
                    search_ms=(perf_counter() - search_start) * 1000,
                    fallback_reason=f"search_error: {type(error).__name__}: {error}",
                )
            )
            return order
        search_ms = (perf_counter() - search_start) * 1000

        if result.action is None:
            order = self.choose_random_move(battle)
            self.results.append(
                self.build_result_log(
                    battle,
                    order,
                    decision_start,
                    search_ms=search_ms,
                    fallback_reason="no_action_found",
                )
            )
            return order

        if result.action.is_switch:
            order = self.create_order(battle.available_switches[result.action.index])
        else:
            order = self.create_order(battle.available_moves[result.action.index])
        self.results.append(self.build_result_log(battle, order, decision_start, search_ms=search_ms, result=result))

        return order

    def build_result_log(
        self,
        battle: Battle,
        order: BattleOrder,
        decision_start: float,
        *,
        search_ms: float | None = None,
        result: SearchResult | None = None,
        fallback_reason: str | None = None,
    ):
        decision_ms = (perf_counter() - decision_start) * 1000

        played_type, played_name = "other", order.message
        if isinstance(order, SingleBattleOrder):
            if isinstance(order.order, Move):
                played_type, played_name = "move", order.order.id
            elif isinstance(order.order, Pokemon):
                played_type, played_name = "switch", order.order.name

        action_values = None
        nodes_processed = None
        if result is not None:
            nodes_processed = result.nodes_processed
            action_values = []

            for action, value in result.action_values:
                if action.is_switch:
                    kind = "switch"
                    name = battle.available_switches[action.index].name
                else:
                    kind = "move"
                    name = battle.available_moves[action.index].id
                action_values.append(ActionValue(kind=kind, name=name, value=round(value, 3)))

            action_values.sort(key=lambda action_value: action_value.value, reverse=True)

        active = battle.active_pokemon
        opponent = battle.opponent_active_pokemon

        return ResultsLog(
            battle_id=battle.battle_tag,
            turn=battle.turn,
            forced_switch=battle.force_switch,
            active=active.species if active else None,
            active_hp=round(active.current_hp_fraction, 2) if active else None,
            opponent=opponent.species if opponent else None,
            opponent_hp=round(opponent.current_hp_fraction, 2) if opponent else None,
            played_action_type=played_type,
            played_action_name=played_name,
            decision_ms=round(decision_ms, 3),
            search_ms=round(search_ms, 3) if search_ms is not None else None,
            fallback_reason=fallback_reason,
            nodes_processed=nodes_processed,
            action_values=action_values,
        )
