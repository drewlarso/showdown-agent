import json
from collections.abc import Callable
from dataclasses import asdict

from poke_env.battle import AbstractBattle, Battle
from poke_env.player import Player

from agent.build import GetOpponentMovePriors, build_state
from agent.engine.state import Action

type SearchFunction = Callable[[str, int], Action | None]


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

    def choose_move(self, battle: AbstractBattle):
        assert isinstance(battle, Battle)

        state = build_state(battle, self.get_opponent_move_priors)
        if state is None:
            return self.choose_random_move(battle)

        state_json = json.dumps(asdict(state))
        action = self.search(state_json, self.depth)
        if action is None:
            return self.choose_random_move(battle)

        if action.is_switch:
            return self.create_order(battle.available_switches[action.index])

        return self.create_order(battle.available_moves[action.index])
