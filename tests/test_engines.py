import json
from pathlib import Path

import pytest

from agent._core import search_rust
from agent.engine.search import search_python

CASES = sorted((Path(__file__).parent.parent / "cases").glob("*.json"))


def expand(action, value):
    return (action.is_switch, action.index, round(value, 9))


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.stem)
@pytest.mark.parametrize("depth", [1, 2])
def test_rust_and_python_agree(path, depth):
    state_json = json.dumps(json.loads(path.read_text())["state"])
    rust_result = search_rust(state_json, depth)
    python_result = search_python(state_json, depth)

    assert rust_result.nodes_processed == python_result.nodes_processed
    assert [expand(action, value) for action, value in rust_result.action_values] == [
        expand(action, value) for action, value in python_result.action_values
    ]
