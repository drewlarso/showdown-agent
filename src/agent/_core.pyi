from typing import SupportsIndex, final

__all__ = ["Action", "SearchResult", "search_rust"]

@final
class Action:
    @property
    def index(self, /) -> int: ...
    @property
    def is_switch(self, /) -> bool: ...

@final
class SearchResult:
    @property
    def action(self, /) -> Action | None: ...
    @property
    def action_values(self, /) -> list[tuple[Action, float]]: ...
    @property
    def nodes_processed(self, /) -> int: ...

def search_rust(state_json: str, depth: SupportsIndex) -> SearchResult: ...
