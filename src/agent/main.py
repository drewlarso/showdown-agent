import asyncio
from datetime import datetime
from pathlib import Path

from poke_env.player import MaxBasePowerPlayer, Player, RandomPlayer, SimpleHeuristicsPlayer

from agent.players.basic_expectimax_player import BasicExpectimaxPlayer
from agent.players.bayes_expectimax_player import BayesExpectimaxPlayer
from agent.players.expectimax_player import ExpectimaxPlayer
from agent.trace import log_matchup, make_summary_row, save_summary

N_BATTLES = 3
DEPTH = 1
GAUNTLET_OPPONENTS: list[type[Player]] = [
    RandomPlayer,
    MaxBasePowerPlayer,
    SimpleHeuristicsPlayer,
    BasicExpectimaxPlayer,
    BayesExpectimaxPlayer,
]


async def run_gauntlet(agent: ExpectimaxPlayer, output_folder: Path, n_battles: int = N_BATTLES) -> None:
    output_folder.mkdir(parents=True, exist_ok=False)
    summary_rows = []

    agent_name = type(agent).__name__
    for opponent_type in GAUNTLET_OPPONENTS:
        opponent_name = opponent_type.__name__
        opponent = opponent_type(max_concurrent_battles=0)
        print(f"{agent_name} vs {opponent_name}:")
        await agent.battle_against(opponent, n_battles=n_battles)

        log_matchup(agent_name, opponent_name, agent.results, agent.battles, output_folder)
        summary_rows.append(make_summary_row(opponent_name, agent.results, agent.battles))

        agent.reset_battles()
        agent.results.clear()

    save_summary(f"{agent_name} vs Gauntlet", summary_rows, output_folder)


async def main() -> None:
    agent = BayesExpectimaxPlayer(depth=DEPTH, max_concurrent_battles=0)
    run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    await run_gauntlet(agent, Path("results") / run_name)


if __name__ == "__main__":
    asyncio.run(main())
