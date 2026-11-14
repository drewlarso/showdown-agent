import asyncio

from poke_env.player import MaxBasePowerPlayer, Player, RandomPlayer, SimpleHeuristicsPlayer

from agent.beliefs import get_believed_moves, get_revealed_moves
from agent.expectimax_player import ExpectimaxPlayer

N_BATTLES = 10


async def run_gauntlet(agent: Player, n_battles: int = N_BATTLES):
    random_player = RandomPlayer(max_concurrent_battles=0)
    max_base_power_player = MaxBasePowerPlayer(max_concurrent_battles=0)
    simple_heuristics_player = SimpleHeuristicsPlayer(max_concurrent_battles=0)
    basic_expectimax = ExpectimaxPlayer(depth=1, get_opponent_moves=get_revealed_moves, max_concurrent_battles=0)

    print("Agent vs Random:")
    await agent.battle_against(random_player, n_battles=n_battles)
    print(f"    Finished battles: {agent.n_finished_battles}")
    print(f"    Agent wins: {agent.n_won_battles}")
    print(f"    Agent win rate: {agent.n_won_battles / agent.n_finished_battles:.1%}")
    agent.reset_battles()

    print("Agent vs Max Base Power:")
    await agent.battle_against(max_base_power_player, n_battles=n_battles)
    print(f"    Finished battles: {agent.n_finished_battles}")
    print(f"    Agent wins: {agent.n_won_battles}")
    print(f"    Agent win rate: {agent.n_won_battles / agent.n_finished_battles:.1%}")
    agent.reset_battles()

    print("Agent vs Simple Heuristics:")
    await agent.battle_against(simple_heuristics_player, n_battles=n_battles)
    print(f"    Finished battles: {agent.n_finished_battles}")
    print(f"    Agent wins: {agent.n_won_battles}")
    print(f"    Agent win rate: {agent.n_won_battles / agent.n_finished_battles:.1%}")
    agent.reset_battles()

    print("Agent vs Basic Expectimax:")
    await agent.battle_against(basic_expectimax, n_battles=n_battles)
    print(f"    Finished battles: {agent.n_finished_battles}")
    print(f"    Agent wins: {agent.n_won_battles}")
    print(f"    Agent win rate: {agent.n_won_battles / agent.n_finished_battles:.1%}")
    agent.reset_battles()


async def main():
    # basic_player = ExpectimaxPlayer(depth=1, get_opponent_moves=get_revealed_moves, max_concurrent_battles=0)
    bayes_player = ExpectimaxPlayer(depth=2, get_opponent_moves=get_believed_moves, max_concurrent_battles=0)
    # await run_gauntlet(basic_player, N_BATTLES)
    await run_gauntlet(bayes_player, N_BATTLES)


if __name__ == "__main__":
    asyncio.run(main())
