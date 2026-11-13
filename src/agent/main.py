import asyncio

from poke_env.player import MaxBasePowerPlayer, Player, RandomPlayer, SimpleHeuristicsPlayer

from agent.bayes_expectimax import BayesExpectimaxPlayer

N_BATTLES = 10


async def run_gauntlet(agent: Player, n_battles: int = N_BATTLES):
    random_player = RandomPlayer()
    max_base_power_player = MaxBasePowerPlayer()
    simple_heuristics_player = SimpleHeuristicsPlayer()

    await agent.battle_against(random_player, n_battles=n_battles)
    print("Expectimax vs Random:")
    print(f"    Finished battles: {agent.n_finished_battles}")
    print(f"    Expectimax wins: {agent.n_won_battles}")
    print(f"    Expectimax win rate: {agent.n_won_battles / agent.n_finished_battles:.1%}")
    agent.reset_battles()

    await agent.battle_against(max_base_power_player, n_battles=n_battles)
    print("Expectimax vs Max Base Power:")
    print(f"    Finished battles: {agent.n_finished_battles}")
    print(f"    Expectimax wins: {agent.n_won_battles}")
    print(f"    Expectimax win rate: {agent.n_won_battles / agent.n_finished_battles:.1%}")
    agent.reset_battles()

    await agent.battle_against(simple_heuristics_player, n_battles=n_battles)
    print("Expectimax vs Simple Heuristics:")
    print(f"    Finished battles: {agent.n_finished_battles}")
    print(f"    Expectimax wins: {agent.n_won_battles}")
    print(f"    Expectimax win rate: {agent.n_won_battles / agent.n_finished_battles:.1%}")
    agent.reset_battles()


async def main():
    bayes_player = BayesExpectimaxPlayer(depth=2)
    await run_gauntlet(bayes_player)


if __name__ == "__main__":
    asyncio.run(main())
