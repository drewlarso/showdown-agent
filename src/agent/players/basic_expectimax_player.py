from agent.beliefs import get_revealed_moves
from agent.engine.search import search_python
from agent.players.expectimax_player import ExpectimaxPlayer, SearchFunction


class BasicExpectimaxPlayer(ExpectimaxPlayer):
    def __init__(self, *, depth: int = 1, search: SearchFunction = search_python, **kwargs):
        super().__init__(
            depth=depth,
            get_opponent_move_priors=get_revealed_moves,
            search=search,
            **kwargs,
        )
