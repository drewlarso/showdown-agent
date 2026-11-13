from poke_env.battle import AbstractBattle, Battle
from poke_env.player import Player

from agent.search import get_best_move
from agent.state import build_state


class BasicExpectimaxPlayer(Player):
    def __init__(self, *args, depth: int = 1, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.depth = depth

    def choose_move(self, battle: AbstractBattle):
        assert isinstance(battle, Battle)

        if len(battle.available_moves) == 1:
            return self.create_order(battle.available_moves[0])

        state = build_state(battle, use_role_weights=False)
        if state is None:
            return self.choose_random_move(battle)
        if len(battle.available_moves) <= 0:
            return self.choose_random_move(battle)

        best_move = get_best_move(state, self.depth)
        if best_move is None:
            return self.choose_random_move(battle)

        moves_by_id = {move.id: move for move in battle.available_moves}
        return self.create_order(moves_by_id[best_move.id])
