from dataclasses import replace

from poke_env.battle import AbstractBattle, Battle, Move, Pokemon
from poke_env.player import Player

from agent.beliefs import get_move_probabilities, get_role_info, get_role_probabilities
from agent.damage import DEFAULT_EV, DEFAULT_IV, calculate_hp, calculate_stat
from agent.search import get_move_values
from agent.state import GameState, PokeState, build_state, create_move_state


class BayesExpectimaxPlayer(Player):
    def __init__(self, *args, depth: int = 1, **kwargs):
        super().__init__(None, *args, **kwargs)

        self.depth = depth

    def choose_move(self, battle: AbstractBattle):
        assert isinstance(battle, Battle)

        if len(battle.available_moves) == 1:
            return self.create_order(battle.available_moves[0])
        if battle.opponent_active_pokemon is None:
            return self.choose_random_move(battle)

        state = build_state(battle)
        if state is None:
            return self.choose_random_move(battle)
        if len(battle.available_moves) <= 0:
            return self.choose_random_move(battle)

        states_with_roles = self.apply_roles(battle, state)

        move_weights: dict[str, float] = {}
        for state in states_with_roles:
            probability, game_state = state
            # for
            move_values = get_move_values(game_state, self.depth)
            for move_id, weight in move_values.items():
                move_weights.setdefault(move_id, 0)
                move_weights[move_id] += probability * weight

        best_move: str = max(move_weights, key=move_weights.get)  # type: ignore
        if best_move is None:
            return self.choose_random_move(battle)

        moves_by_id = {move.id: move for move in battle.available_moves}
        return self.create_order(moves_by_id[best_move])

    def apply_roles(self, battle: Battle, state: GameState):
        opponent = battle.opponent_active_pokemon
        if opponent is None:
            return [(1.0, state)]

        states: list[tuple[float, GameState]] = []
        for role, weight in get_role_probabilities(opponent).items():
            if weight <= 0:
                continue
            opponent_with_role = self._apply_role(opponent, state.opponent_pokemon, role)
            resulting_game_state = replace(state, opponent_pokemon=opponent_with_role)
            states.append((weight, resulting_game_state))

        return states

    def _apply_role(self, pokemon: Pokemon, poke_state: PokeState, role: str):
        role_info = get_role_info(pokemon, role)

        moves = []
        for move_id, probability in get_move_probabilities(pokemon, role).items():
            move = pokemon.moves.get(move_id) or Move(move_id=move_id, gen=9)
            moves.append(create_move_state(move, probability))

        evs = role_info.get("evs") or {}
        ivs = role_info.get("ivs") or {}

        stats = {}
        for stat, value in pokemon.base_stats.items():
            ev = evs.get(stat, DEFAULT_EV)
            iv = ivs.get(stat, DEFAULT_IV)
            if stat == "hp":
                calculate_hp(value, poke_state.level, ev, iv)
            else:
                calculate_stat(value, poke_state.level, ev, iv)

        return replace(poke_state, moves=moves, stats=stats)
