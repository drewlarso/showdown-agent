import json
from math import comb
from pathlib import Path
from typing import Any

from poke_env.battle import Pokemon


def load_randbats() -> dict[str, Any]:
    data_file = Path(__file__).parent.parent.parent / "data" / "randbats.json"
    if not data_file.exists():
        raise RuntimeError("no randbats found, run the fetch_randbats.py script to fetch them")

    with data_file.open() as file:
        return json.load(file)


RANDBATS = load_randbats()


def get_revealed_moves(pokemon: Pokemon) -> dict[str, float]:
    return {move_id: 1.0 for move_id in pokemon.moves}


def get_believed_moves(pokemon: Pokemon) -> dict[str, float]:
    pokemon_info = get_pokemon_info(pokemon)
    if pokemon_info is None:
        return get_revealed_moves(pokemon)

    roles = pokemon_info["roles"]
    revealed_moves = set(pokemon.moves)
    move_priors: dict[str, float] = {}

    for role, role_probability in get_role_probabilities(pokemon, roles).items():
        move_probabilities = get_move_probabilities(revealed_moves, roles[role]["moves"])
        for move_id, move_probability in move_probabilities.items():
            move_priors[move_id] = move_priors.get(move_id, 0.0) + role_probability * move_probability

    return move_priors


def get_pokemon_info(pokemon: Pokemon) -> dict[str, Any] | None:
    if pokemon.species in RANDBATS:
        return RANDBATS[pokemon.species]
    return RANDBATS.get(pokemon.base_species)


def get_role_probabilities(pokemon: Pokemon, roles: dict[str, Any]) -> dict[str, float]:
    revealed_moves = set(pokemon.moves)
    beliefs = {role: 1 / len(roles) for role in roles}
    move_likelihoods = {role: get_move_likelihood(revealed_moves, info["moves"]) for role, info in roles.items()}
    item_likelihoods = {
        role: get_observed_likelihood(pokemon.item, info.get("items") or [], "unknown_item")
        for role, info in roles.items()
    }
    ability_likelihoods = {
        role: get_observed_likelihood(pokemon.ability, info.get("abilities") or [], "unknown_ability")
        for role, info in roles.items()
    }

    for likelihoods in (move_likelihoods, item_likelihoods, ability_likelihoods):
        weighted_roles = {role: beliefs[role] * likelihoods[role] for role in roles}
        total_weight = sum(weighted_roles.values())
        if total_weight > 0:
            beliefs = {role: weight / total_weight for role, weight in weighted_roles.items()}

    return beliefs


def get_move_probabilities(revealed_moves: set[str], move_pool: list[str]) -> dict[str, float]:
    unknown_moves = [move for move in move_pool if move not in revealed_moves]
    open_slots = max(0, min(4, len(move_pool)) - len(revealed_moves))
    share = min(1.0, open_slots / len(unknown_moves)) if unknown_moves else 0.0

    probabilities = {move: 1.0 for move in revealed_moves}
    for move in unknown_moves:
        probabilities[move] = share
    return probabilities


def get_move_likelihood(revealed_moves: set[str], move_pool: list[str]) -> float:
    set_size = min(4, len(move_pool))
    revealed_count = len(revealed_moves)
    if revealed_count > set_size or not revealed_moves.issubset(move_pool):
        return 0.0

    matching_sets = comb(len(move_pool) - revealed_count, set_size - revealed_count)
    possible_sets = comb(len(move_pool), set_size)
    return matching_sets / possible_sets


def get_observed_likelihood(observed: str | None, choices: list[str], unknown_value: str) -> float:
    if not observed or observed == unknown_value:
        return 1.0

    return 1 / len(choices) if observed in choices else 0.0
