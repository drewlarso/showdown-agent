import json
from pathlib import Path
from time import perf_counter

from agent.engine.search import search_python

DEPTHS = (1, 2, 3)


def run_cases():
    root = Path(__file__).parent.parent
    lines = [
        "| Case | Depth | Expected | Chosen | Met | Nodes | Search ms |",
        "|---|---:|---|---|---|---:|---:|",
    ]

    for path in sorted((root / "cases").glob("*.json")):
        case = json.loads(path.read_text())
        state = case["state"]

        for depth in DEPTHS:
            start = perf_counter()
            result = search_python(json.dumps(state), depth)
            ms = (perf_counter() - start) * 1000

            action = result.action
            if action is None:
                chosen = "none"
            elif action.is_switch:
                chosen = f"switch:{action.index}"
            else:
                chosen = state["friendly_pokemon"]["moves"][action.index]["id"]

            met = "yes" if chosen == case["expected"] else "no"
            lines.append(
                f"|{case['name']}|{depth}|{case['expected']}|{chosen}|{met}|{result.nodes_processed}|{ms:.1f}|"
            )

    table = "\n".join(lines) + "\n"
    print(table)

    results_folder = root / "results" / "baseline"
    results_folder.mkdir(parents=True, exist_ok=True)
    (results_folder / "cases.md").write_text(table)


if __name__ == "__main__":
    run_cases()
