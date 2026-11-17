import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from statistics import mean

from poke_env.battle import AbstractBattle

from agent.players.expectimax_player import ResultsLog


def log_matchup(
    agent_name: str,
    opponent_name: str,
    results: list[ResultsLog],
    battles: dict[str, AbstractBattle],
    output_folder: Path,
):
    decisions = defaultdict(list)
    for result in results:
        decision = asdict(result)
        del decision["battle_id"]
        decisions[result.battle_id].append(decision)

    log = {
        "agent": agent_name,
        "opponent": opponent_name,
        "n_battles": len(battles),
        "battles": [
            {
                "battle_id": battle_id,
                "won": battle.won,
                "turns": battle.turn,
                "decisions": decisions[battle_id],
            }
            for battle_id, battle in battles.items()
        ],
    }

    with open(output_folder / f"{agent_name}_vs_{opponent_name}.json", "w") as f:
        json.dump(log, f)


def make_summary_row(opponent_name: str, results: list[ResultsLog], battles: dict[str, AbstractBattle]):
    games = list(battles.values())
    wins = [battle for battle in games if battle.won]
    searched = [result for result in results if result.search_ms is not None]
    fallbacks = [result for result in results if result.fallback_reason]

    turns = [battle.turn for battle in games]
    nodes = [result.nodes_processed for result in searched if result.nodes_processed]
    times = [result.search_ms for result in searched if result.search_ms]

    cells = [
        opponent_name,
        f"{len(wins)}/{len(games)}",
        f"{len(wins) / len(games):.1%}",
        f"{mean(turns):.1f}",
        f"{mean(nodes):.0f}",
        f"{mean(times):.3f}",
        f"{max(times):.3f}",
        str(len(fallbacks)),
    ]

    return "|" + "|".join(cells) + "|"


def save_summary(title: str, rows: list[str], output_folder: Path):
    lines = [
        f"# {title}",
        "",
        "| Opponent | Wins | Win rate | Avg turns | Avg nodes | Avg search ms | Max search ms | Fallbacks |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        *rows,
    ]

    with open(output_folder / "summary.md", "w") as f:
        f.write("\n".join(lines) + "\n")
