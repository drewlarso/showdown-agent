import asyncio

from poke_env.player import MaxBasePowerPlayer, Player, RandomPlayer, SimpleHeuristicsPlayer

from agent.players.basic_expectimax_player import BasicExpectimaxPlayer
from agent.players.bayes_expectimax_player import BayesExpectimaxPlayer

N_BATTLES = 10
GAUNTLET_OPPONENTS: list[type[Player]] = [
    RandomPlayer,
    MaxBasePowerPlayer,
    SimpleHeuristicsPlayer,
    BasicExpectimaxPlayer,
    BayesExpectimaxPlayer,
]


async def run_gauntlet(agent: Player, n_battles: int = N_BATTLES) -> None:
    for opponent_type in GAUNTLET_OPPONENTS:
        opponent = opponent_type(max_concurrent_battles=0)

        print(f"{type(agent).__name__} vs {opponent_type.__name__}:")
        await agent.battle_against(opponent, n_battles=n_battles)
        print(f"    Finished battles: {agent.n_finished_battles}")
        print(f"    Agent wins: {agent.n_won_battles}")
        win_rate = f"{agent.n_won_battles / agent.n_finished_battles:.1%}" if agent.n_finished_battles else "N/A"
        print(f"    Agent win rate: {win_rate}")
        agent.reset_battles()


async def main() -> None:
    agent = BayesExpectimaxPlayer(max_concurrent_battles=0)
    await run_gauntlet(agent)


if __name__ == "__main__":
    asyncio.run(main())
