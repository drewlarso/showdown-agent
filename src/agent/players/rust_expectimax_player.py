from agent._core import search_rust
from agent.beliefs import get_believed_moves
from agent.players.expectimax_player import ExpectimaxPlayer


class RustExpectimaxPlayer(ExpectimaxPlayer):
    def __init__(self, *, depth: int = 2, **kwargs):
        super().__init__(
            depth=depth,
            get_opponent_move_priors=get_believed_moves,
            search=search_rust,  # type: ignore
            **kwargs,
        )
