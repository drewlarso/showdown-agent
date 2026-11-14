from poke_env.battle import AbstractBattle, Battle
from poke_env.player import Player

from agent.beliefs import get_revealed_moves
from agent.build import GetOpponentMoves, build_state
from agent.search import get_best_action
from agent.state import SwitchState


class ExpectimaxPlayer(Player):
    def __init__(self, *args, depth: int = 1, get_opponent_moves: GetOpponentMoves = get_revealed_moves, **kwargs):
        super().__init__(None, *args, **kwargs)

        self.depth = depth
        self.get_opponent_moves = get_opponent_moves

    def choose_move(self, battle: AbstractBattle):
        assert isinstance(battle, Battle)

        state = build_state(battle, self.get_opponent_moves)
        if state is None:
            return self.choose_random_move(battle)

        best_action = get_best_action(state, self.depth)
        if best_action is None:
            return self.choose_random_move(battle)

        if isinstance(best_action, SwitchState):
            return self.create_order(battle.available_switches[best_action.bench_index])

        moves_by_id = {move.id: move for move in battle.available_moves}
        return self.create_order(moves_by_id[best_action.id])
