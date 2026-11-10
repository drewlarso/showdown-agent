from poke_env.battle import AbstractBattle, Battle
from poke_env.player import Player

from agent.state import GameState, PokeState, build_state


class BasicExpectimaxPlayer(Player):
    def __init__(self, *args, depth: int = 1, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.depth = depth

    def choose_move(self, battle: AbstractBattle):
        assert isinstance(battle, Battle)

        state = build_state(battle)
        print(state)

        return self.choose_random_move(battle)
