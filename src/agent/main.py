import asyncio

from poke_env.player import MaxBasePowerPlayer, RandomPlayer, SimpleHeuristicsPlayer

from agent.basic_expectimax import BasicExpectimaxPlayer

N_BATTLES = 100


async def main():
    expectimax = BasicExpectimaxPlayer(depth=1)
    random = RandomPlayer(max_concurrent_battles=0)
    max_base_power = MaxBasePowerPlayer(max_concurrent_battles=0)
    simple_heuristics = SimpleHeuristicsPlayer(max_concurrent_battles=0)

    await expectimax.battle_against(random, n_battles=N_BATTLES)
    print("Expectimax vs Random:")
    print(f"    Finished battles: {expectimax.n_finished_battles}")
    print(f"    Expectimax wins: {expectimax.n_won_battles}")
    print(f"    Expectimax win rate: {expectimax.n_won_battles / expectimax.n_finished_battles:.1%}")
    expectimax.reset_battles()

    await expectimax.battle_against(max_base_power, n_battles=N_BATTLES)
    print("Expectimax vs Max Base Power:")
    print(f"    Finished battles: {expectimax.n_finished_battles}")
    print(f"    Expectimax wins: {expectimax.n_won_battles}")
    print(f"    Expectimax win rate: {expectimax.n_won_battles / expectimax.n_finished_battles:.1%}")
    expectimax.reset_battles()

    await expectimax.battle_against(simple_heuristics, n_battles=N_BATTLES)
    print("Expectimax vs Simple Heuristics:")
    print(f"    Finished battles: {expectimax.n_finished_battles}")
    print(f"    Expectimax wins: {expectimax.n_won_battles}")
    print(f"    Expectimax win rate: {expectimax.n_won_battles / expectimax.n_finished_battles:.1%}")
    expectimax.reset_battles()


if __name__ == "__main__":
    asyncio.run(main())
